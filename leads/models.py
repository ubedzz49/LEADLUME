from django.db import models
from django.utils.timezone import now

class Lead(models.Model):
    name = models.CharField(max_length=255, default="Unknown")
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True, default="")  
    message = models.TextField(blank=True, null=True, default="")  
    lead_score = models.IntegerField(default=0)
    lead_amount = models.IntegerField(default=0)
    
    def __str__(self):
        return self.name

class Medicine(models.Model):
    name = models.CharField(max_length=255, default="Unnamed Medicine")
    dosage = models.CharField(max_length=50, default="1 tablet once a day")
    frequency = models.IntegerField(default=30)
    
    def __str__(self):
        return self.name

class Purchase(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name="purchases")
    product_name = models.CharField(max_length=255, default="Unknown Product")
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    purchase_date = models.DateTimeField(default=now)
    
    def __str__(self):
        return f"{self.lead.name} - {self.product_name}"

class Reminder(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE)
    message = models.TextField()
    date = models.DateTimeField()
    status = models.CharField(
        max_length=20,
        choices=[("Not Sent", "Not Sent"), ("Sent", "Sent")],
        default="Not Sent"
    )
    
    def __str__(self):
        return f"Reminder for {self.lead.name} - Status: {self.status} on {self.date}"
