from django.contrib import admin
from .models import User, Event, Attendee, Resource, ScheduleItem, Notification

admin.site.register(User)
admin.site.register(Event)
admin.site.register(Attendee)
admin.site.register(Resource)
admin.site.register(ScheduleItem)
admin.site.register(Notification)
