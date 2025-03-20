from django.core.mail import send_mail
from django.utils.timezone import now
from .models import Reminder

def send_due_reminders():
    """Send reminder emails for all due reminders today and mark them as sent."""
    reminders = Reminder.objects.filter(date__date=now().date(), status="Not Sent")

    for reminder in reminders:
        if reminder.lead.email:  # Ensure the lead has an email
            send_mail(
                subject="Reminder Notification",
                message=f"Hello {reminder.lead.name},\n\n{reminder.message}\n\nThank you!",
                from_email="your_email@gmail.com",  # Replace with your email
                recipient_list=[reminder.lead.email],
                fail_silently=False,
            )

        # Mark the reminder as sent
        reminder.status = "Sent"
        reminder.save()

    return f"Processed {reminders.count()} reminders."
