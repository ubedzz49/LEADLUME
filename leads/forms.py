from django import forms
from .models import Lead

class LeadForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = ["name", "email", "phone"]


# forms.py

from django import forms
from .models import Purchase

from django import forms
from .models import Purchase, Lead, Reminder
from datetime import timedelta  # Make sure to import timedelta
from django.core.mail import send_mail  # For sending notifications via email
from django.utils.timezone import now
class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ['lead', 'product_name', 'amount', 'purchase_date']
        widgets = {
            'purchase_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def save(self, commit=True):
        purchase = super().save(commit=False)
        lead = purchase.lead

        # Update the lead_score
        lead_score_increase = purchase.amount / 100
        lead.lead_score += lead_score_increase
        lead.lead_amount+=purchase.amount
        lead.save()  # Save the Lead instance
        if lead.lead_score > 1000:
            reminder_message = "Congratulations! You are eligible for free delivery."
            # Create reminder
            Reminder.objects.create(
                lead=lead,
                message=reminder_message,
                date=now(),  # You can change this to any date when you want the reminder to be sent
                status="Not Sent"  # Set status as not sent initially
            )
        # Create reminders for 7 days, 15 days, and 1 month from purchase_date
        reminder_dates = [timedelta(days=7), timedelta(days=15), timedelta(days=30)]
        for reminder_date in reminder_dates:
            reminder_message = f"Do you need {purchase.product_name} again?"  # Example message
            reminder_date_time = purchase.purchase_date + reminder_date

            # Create the reminder with the specific date
            Reminder.objects.create(
                lead=lead,
                message=reminder_message,  # Store the reminder message
                date=reminder_date_time,  # Set the reminder date
                status="Not Sent"  # Initially set the status to "Not Sent"
            )

        # If commit is true, save the purchase
        if commit:
            purchase.save()  # Save the Purchase instance
        return purchase
