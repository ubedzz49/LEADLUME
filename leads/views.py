from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
from django.shortcuts import render
from twilio.twiml.messaging_response import MessagingResponse
from .models import Lead, Purchase, Reminder  # Import necessary models

from django.shortcuts import render
from .models import Lead



from django.core.mail import send_mail
from django.utils.timezone import now
from .models import Reminder
from django.shortcuts import render
from .models import Lead
from .utils import send_due_reminders  # ✅ Correct import

def lead_list(request):
    # Call the reminder processing function
    send_due_reminders()

    # Fetch all leads
    leads = Lead.objects.all()

    return render(request, "leads/lead_list.html", {"leads": leads})


@csrf_exempt  # Exempt CSRF for external Twilio requests
def whatsapp_webhook(request):
    if request.method == "POST":
        from_number = request.POST.get("From", "").replace("whatsapp:", "")
        message_body = request.POST.get("Body", "").strip()

        if not from_number:  # Ensure the phone number exists
            return HttpResponse("Missing phone number", status=400)

        # Check if the lead already exists
        lead, created = Lead.objects.get_or_create(phone=from_number, defaults={"name": "New Lead"})

        response = MessagingResponse()
        if created:
            reply_text = f"Hello! Thanks for reaching out. You are now registered in our system."
        else:
            reply_text = f"Welcome back! How can we assist you today?"

        response.message(reply_text)
        return HttpResponse(str(response), content_type="application/xml")

    return HttpResponse("Invalid request", status=400)

def home(request):
    return render(request, "leads/home.html")

from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    send_due_reminders()
    leads = Lead.objects.all()
    purchases = Purchase.objects.all()
    reminders = Reminder.objects.all()

    return render(request, 'leads/dashboard.html', {
        'leads': leads,
        'purchases': purchases,
        'reminders': reminders
    })




from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import render, redirect

def user_login(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("dashboard")  # Redirect after login
    else:
        form = AuthenticationForm()
    
    return render(request, "leads/login.html", {"form": form})


def user_logout(request):
    logout(request)
    return redirect("login")  # Redirect after logout

def user_register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log in the user immediately
            return redirect("dashboard")
    else:
        form = UserCreationForm()
    
    return render(request, "leads/register.html", {"form": form})


from django.shortcuts import render, redirect
from .models import Lead
from .forms import LeadForm

def create_lead(request):
    if request.method == "POST":
        form = LeadForm(request.POST)
        if form.is_valid():
            lead=form.save()
            Reminder.objects.create(
                lead=lead,
                message= "Welcome, do you know for how long we were waiting for you!",  # Assuming you want to associate the medicine with the reminder
                date=now(),  # You can change this to any date when you want the reminder to be sent
                status="Not Sent"  # Set status as pending initially
            )
            return redirect("lead_list")
    else:
        form = LeadForm()
    
    return render(request, "leads/lead_form.html", {"form": form})



from django.shortcuts import get_object_or_404

def update_lead(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    if request.method == "POST":
        form = LeadForm(request.POST, instance=lead)
        if form.is_valid():
            form.save()
            return redirect("lead_list")
    else:
        form = LeadForm(instance=lead)

    return render(request, "leads/lead_form.html", {"form": form})



from django.shortcuts import redirect

def delete_lead(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    if request.method == "POST":
        lead.delete()
        return redirect("lead_list")
    return render(request, "leads/lead_confirm_delete.html", {"lead": lead})


# from django.shortcuts import render, get_object_or_404
# from .models import Lead

# def lead_detail(request, pk):
#     lead = get_object_or_404(Lead, pk=pk)
#     return render(request, "leads/lead_detail.html", {"lead": lead})

import plotly.graph_objects as go
from django.db.models import Sum
from django.shortcuts import render, get_object_or_404
from django.utils.timezone import now, timedelta
from .models import Lead, Purchase

def lead_detail(request, pk):
    lead = get_object_or_404(Lead, pk=pk)

    # 📌 PIE CHART DATA
    total_spent_by_lead = Purchase.objects.filter(lead=lead).aggregate(Sum('amount'))['amount__sum'] or 0
    total_spent_by_all = Purchase.objects.aggregate(Sum('amount'))['amount__sum'] or 1  # Avoid division by zero
    remaining_amount = total_spent_by_all - total_spent_by_lead

    # 🥧 CREATE PIE CHART
    pie_chart = go.Figure(data=[go.Pie(
        labels=["This Lead", "Other Leads"],
        values=[total_spent_by_lead, remaining_amount],
        marker=dict(colors=["#ffbc3b", "#1f77b4"])
    )])
    pie_chart_html = pie_chart.to_html(full_html=False)

    # 📌 LINE CHART DATA (Day-by-Day Spending)
    last_90_days = now() - timedelta(days=90)  # Last 30 days
    purchases = Purchase.objects.filter(lead=lead, purchase_date__gte=last_90_days)

    daily_spending = purchases.values('purchase_date__date').annotate(total_spent=Sum('amount')).order_by('purchase_date__date')

    if daily_spending:
        dates = [entry['purchase_date__date'].strftime('%Y-%m-%d') for entry in daily_spending]
        amounts = [entry['total_spent'] for entry in daily_spending]

        # 📈 CREATE LINE CHART
        line_chart = go.Figure(data=go.Scatter(
            x=dates,
            y=amounts,
            mode='lines+markers',
            line=dict(color='blue'),
            marker=dict(size=6, color='red'),
            name="Daily Spending"
        ))
        line_chart.update_layout(title="Daily Spending Trend (Last 0 Days)", xaxis_title="Date", yaxis_title="Amount (₹)")
        line_chart_html = line_chart.to_html(full_html=False)
    else:
        line_chart_html = None  # No data available

    return render(request, "leads/lead_detail.html", {
        "lead": lead,
        "pie_chart": pie_chart_html,
        "line_chart": line_chart_html
    })


from django.shortcuts import render
from django.db.models import Count, Sum
from .models import Lead, Purchase

def lead_report(request):
    send_due_reminders()
    from django.db.models import Count, Sum
    from .models import Lead, Purchase

    leads = Lead.objects.annotate(
        total_purchases=Count('purchases'),
        total_spent=Sum('purchases__amount')
    ).order_by('-lead_score')

    return render(request, 'leads/lead_report.html', {'leads': leads})

from django.shortcuts import render, redirect
from .models import Lead, Purchase
from .forms import PurchaseForm

# leads/views.py

from django.shortcuts import render, redirect
from .models import Lead, Purchase
from .forms import PurchaseForm

# views.py

from django.shortcuts import render, redirect
from .forms import PurchaseForm
from .models import Purchase,Reminder,Lead

def add_purchase(request):
    send_due_reminders()
    if request.method == 'POST':
        form = PurchaseForm(request.POST)
        if form.is_valid():
            form.save()  # This will update the lead_score
           
            return redirect('dashboard')  # Redirect to dashboard or another page
    else:
        form = PurchaseForm()
    
    return render(request, 'leads/add_purchase.html', {'form': form})


# leads/views.py

from django.shortcuts import render
from .models import Purchase

from django.shortcuts import render
from .models import Lead, Reminder

from django.shortcuts import render
from .models import Lead, Reminder, Purchase  # Make sure to import the Purchase model

def dashboard(request):
    send_due_reminders()
    # Get all leads, reminders, and purchases
    leads = Lead.objects.all()  # You can filter these if needed
    reminders = Reminder.objects.all()
    purchases = Purchase.objects.all()
    
    # Pass them to the template context
    context = {
        'leads': leads,
        'reminders': reminders,
        'purchases': purchases
    }

    return render(request, 'leads/dashboard.html', context)




