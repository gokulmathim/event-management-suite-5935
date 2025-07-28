from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.response import Response
from django.contrib.auth import logout
from .models import User, Event, Attendee, Resource, ScheduleItem, Notification
from .serializers import (
    UserSerializer, EventSerializer, AttendeeSerializer,
    ResourceSerializer, ScheduleItemSerializer, NotificationSerializer
)
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from django.db.models import Q

# PUBLIC_INTERFACE
@api_view(['GET'])
def health(request):
    """Health check endpoint. Returns a simple message."""
    return Response({"message": "Server is up!"})

# PUBLIC_INTERFACE
@api_view(['POST'])
def register(request):
    """
    User registration endpoint.
    Expects: username, email, password, first_name, last_name (optional)
    """
    data = request.data
    if User.objects.filter(username=data.get('username')).exists():
        return Response({'error': 'Username already taken.'}, status=400)
    if User.objects.filter(email=data.get('email')).exists():
        return Response({'error': 'Email already registered.'}, status=400)
    user = User.objects.create_user(
        username=data['username'],
        email=data['email'],
        password=data['password'],
        first_name=data.get('first_name', ''),
        last_name=data.get('last_name', '')
    )
    serializer = UserSerializer(user)
    return Response(serializer.data, status=201)


# PUBLIC_INTERFACE
class CustomObtainAuthToken(ObtainAuthToken):
    """
    User login endpoint. Returns token and user info on success.
    """
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        user_data = UserSerializer(user).data
        return Response({'token': token.key, 'user': user_data})

# PUBLIC_INTERFACE
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """
    Logs out the authenticated user by deleting token.
    """
    request.user.auth_token.delete()
    logout(request)
    return Response({"message": "Logged out"}, status=200)

# PUBLIC_INTERFACE
class EventViewSet(viewsets.ModelViewSet):
    """
    ViewSet for CRUD operations on events.
    """
    queryset = Event.objects.all().select_related('organizer')
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def attend(self, request, pk=None):
        """
        Marks the authenticated user as an attendee for the event.
        """
        event = self.get_object()
        attendee, created = Attendee.objects.get_or_create(event=event, user=request.user)
        if created:
            attendee.status = 'confirmed'
            attendee.save()
            return Response({'status': 'confirmed'}, status=201)
        return Response({'status': attendee.status}, status=200)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def unattend(self, request, pk=None):
        """
        Removes the authenticated user from the attendees of the event.
        """
        event = self.get_object()
        try:
            Attendee.objects.filter(event=event, user=request.user).delete()
            return Response({'status': 'removed'}, status=200)
        except Attendee.DoesNotExist:
            return Response({'error': 'Not found.'}, status=404)

# PUBLIC_INTERFACE
class AttendeeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for listing and managing attendees (organizer/admin rights).
    """
    queryset = Attendee.objects.all().select_related('event', 'user')
    serializer_class = AttendeeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Organizer sees all attendees of their events
        if self.request.user.is_staff:
            return Attendee.objects.all()
        return Attendee.objects.filter(Q(user=self.request.user) | Q(event__organizer=self.request.user))

# PUBLIC_INTERFACE
class ResourceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for allocating and viewing resources for events.
    """
    queryset = Resource.objects.all().select_related('event')
    serializer_class = ResourceSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        # Show only resources belonging to events user can access
        if self.request.user.is_staff:
            return Resource.objects.all()
        user_events = Event.objects.filter(organizer=self.request.user)
        return Resource.objects.filter(event__in=user_events)

# PUBLIC_INTERFACE
class ScheduleItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing event schedules.
    """
    queryset = ScheduleItem.objects.all().select_related('event')
    serializer_class = ScheduleItemSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        # Allows filtering by event id, permission to own events
        event_id = self.request.query_params.get('event')
        qs = ScheduleItem.objects.all()
        if event_id:
            qs = qs.filter(event_id=event_id)
        if not self.request.user.is_staff:
            user_events = Event.objects.filter(organizer=self.request.user)
            qs = qs.filter(event__in=user_events)
        return qs

# PUBLIC_INTERFACE
class NotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for listing and marking notifications as read.
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def mark_read(self, request, pk=None):
        """
        Mark this notification as read.
        """
        notif = self.get_object()
        notif.is_read = True
        notif.save()
        return Response({'status': 'read'}, status=200)

# PUBLIC_INTERFACE
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def dashboard_overview(request):
    """
    Dashboard overview for the current user.
    Returns counts of events, attendees, resources, schedule items and unread notifications.
    """
    user = request.user
    total_events = Event.objects.filter(organizer=user).count()
    attending_events = Event.objects.filter(attendees__user=user).count()
    notifications = Notification.objects.filter(user=user, is_read=False).count()
    schedule_items = ScheduleItem.objects.filter(event__organizer=user).count()
    resources = Resource.objects.filter(event__organizer=user).count()

    return Response({
        "total_events": total_events,
        "attending_events": attending_events,
        "schedule_items": schedule_items,
        "resources": resources,
        "unread_notifications": notifications
    })

