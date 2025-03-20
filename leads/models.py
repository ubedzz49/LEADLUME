from django.db import models
from django.utils.timezone import now

from django.db import models
from django.utils.timezone import now

from django.utils.timezone import now

class Lead(models.Model):
    name = models.CharField(max_length=255, default="Unknown")  # Default name
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True, default="")  
    message = models.TextField(blank=True, null=True, default="")  
    lead_score = models.IntegerField(default=0)  # New field for lead score
    lead_amount = models.IntegerField(default=0)
    def __str__(self):
        return self.name

# Medicine Model - Stores medicine details
class Medicine(models.Model):
    name = models.CharField(max_length=255, default="Unnamed Medicine")
    dosage = models.CharField(max_length=50, default="1 tablet once a day")
    frequency = models.IntegerField(help_text="Days between refills", default=30)

    def __str__(self):
        return self.name


# Purchase Model - Tracks purchases of medicines by customers
class Purchase(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name="purchases")
    product_name = models.CharField(max_length=255, default="Unknown Product")
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    purchase_date = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.lead.name} - {self.product_name}"


# Reminder Model - Stores medicine refill reminders
from django.db import models
from .models import Lead

from django.db import models
from .models import Lead

class Reminder(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE)  # Customer
    message = models.TextField()  # The message to store, like "Do you need this medicine again?"
    date = models.DateTimeField()  # The date when the reminder should be sent
    status = models.CharField(
        max_length=20,
        choices=[("Not Sent", "Not Sent"), ("Sent", "Sent")],
        default="Not Sent"
    )

    def __str__(self):
        return f"Reminder for {self.lead.name} - Status: {self.status} on {self.date}"
