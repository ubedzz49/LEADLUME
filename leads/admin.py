from django.contrib import admin
from .models import Lead, Medicine, Purchase, Reminder

admin.site.register(Lead)
admin.site.register(Medicine)
admin.site.register(Purchase)
admin.site.register(Reminder)
