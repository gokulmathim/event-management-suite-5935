from rest_framework import serializers
from .models import User, Event, Attendee, Resource, ScheduleItem, Notification

# PUBLIC_INTERFACE
class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


# PUBLIC_INTERFACE
class EventSerializer(serializers.ModelSerializer):
    """Serializer for Event model."""
    organizer = UserSerializer(read_only=True)
    attendees_count = serializers.IntegerField(source='attendees.count', read_only=True)
    
    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'organizer',
            'start_datetime', 'end_datetime', 'location',
            'created_at', 'updated_at', 'is_public', 'attendees_count'
        ]


# PUBLIC_INTERFACE
class AttendeeSerializer(serializers.ModelSerializer):
    """Serializer for Attendee model."""
    user = UserSerializer(read_only=True)
    class Meta:
        model = Attendee
        fields = ['id', 'user', 'status', 'joined_at', 'event']


# PUBLIC_INTERFACE
class ResourceSerializer(serializers.ModelSerializer):
    """Serializer for Resource model."""
    class Meta:
        model = Resource
        fields = ['id', 'event', 'name', 'description', 'quantity']


# PUBLIC_INTERFACE
class ScheduleItemSerializer(serializers.ModelSerializer):
    """Serializer for ScheduleItem model."""
    class Meta:
        model = ScheduleItem
        fields = [
            'id', 'event', 'title', 'description',
            'start_datetime', 'end_datetime', 'location', 'order'
        ]


# PUBLIC_INTERFACE
class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification model."""
    class Meta:
        model = Notification
        fields = ['id', 'user', 'event', 'message', 'created_at', 'is_read']
