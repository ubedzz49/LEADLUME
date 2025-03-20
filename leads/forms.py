from django import forms
from .models import Purchase, Lead, Reminder
from datetime import timedelta
from django.core.mail import send_mail
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

        lead_score_increase = purchase.amount / 100
        lead.lead_score += lead_score_increase
        lead.lead_amount += purchase.amount
        lead.save()

        if lead.lead_score > 1000:
            reminder_message = "Congratulations! You are eligible for free delivery."
            Reminder.objects.create(
                lead=lead,
                message=reminder_message,
                date=now(),
                status="Not Sent"
            )

        reminder_dates = [timedelta(days=7), timedelta(days=15), timedelta(days=30)]
        for reminder_date in reminder_dates:
            reminder_message = f"Do you need {purchase.product_name} again?"
            reminder_date_time = purchase.purchase_date + reminder_date

            Reminder.objects.create(
                lead=lead,
                message=reminder_message,
                date=reminder_date_time,
                status="Not Sent"
            )

        if commit:
            purchase.save()
        return purchase
