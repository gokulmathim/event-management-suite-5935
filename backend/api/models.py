from django.db import models
from django.contrib.auth.models import AbstractUser

# PUBLIC_INTERFACE
class User(AbstractUser):
    """
    Custom User model. Extends Django's AbstractUser.
    Fields: username, email, password, first_name, last_name, is_active, date_joined (via AbstractUser)
    Additional fields can be added, e.g., profile details.
    """
    # Extend as needed - currently uses default fields

    def __str__(self):
        return self.username


# PUBLIC_INTERFACE
class Event(models.Model):
    """
    Event model representing an event.
    """
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    organizer = models.ForeignKey(User, related_name="organized_events", on_delete=models.CASCADE)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    location = models.CharField(max_length=256, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_public = models.BooleanField(default=True)

    def __str__(self):
        return self.title


# PUBLIC_INTERFACE
class Attendee(models.Model):
    """
    Attendee model representing a user invited/registered to an event.
    """
    event = models.ForeignKey(Event, related_name="attendees", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="attending_events", on_delete=models.CASCADE)
    status = models.CharField(max_length=32, choices=(
        ('invited', 'Invited'),
        ('confirmed', 'Confirmed'),
        ('declined', 'Declined')
    ), default='invited')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'user')

    def __str__(self):
        return f"{self.user.username} -> {self.event.title} ({self.status})"


# PUBLIC_INTERFACE
class Resource(models.Model):
    """
    Resource allocated to an event (e.g. room, AV equipment).
    """
    event = models.ForeignKey(Event, related_name="resources", on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.name} ({self.quantity}) for {self.event.title}"


# PUBLIC_INTERFACE
class ScheduleItem(models.Model):
    """
    Item in an event's schedule (e.g. talk, activity).
    """
    event = models.ForeignKey(Event, related_name="schedule_items", on_delete=models.CASCADE)
    title = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    location = models.CharField(max_length=256, blank=True)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.event.title} - {self.title} ({self.start_datetime:%Y-%m-%d %H:%M})"


# PUBLIC_INTERFACE
class Notification(models.Model):
    """
    Notifications sent to users for events or changes.
    """
    user = models.ForeignKey(User, related_name="notifications", on_delete=models.CASCADE)
    event = models.ForeignKey(Event, related_name="notifications", on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification to {self.user.username}: {self.message[:30]}..."

