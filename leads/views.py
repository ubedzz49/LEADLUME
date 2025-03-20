from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
from django.shortcuts import render
from twilio.twiml.messaging_response import MessagingResponse
from .models import Lead, Purchase, Reminder
from django.core.mail import send_mail
from .utils import send_due_reminders
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import redirect, get_object_or_404
import plotly.graph_objects as go
from django.db.models import Sum, Count
from django.utils.timezone import timedelta
from .forms import LeadForm, PurchaseForm

def lead_list(request):
    send_due_reminders()
    leads = Lead.objects.all()
    return render(request, "leads/lead_list.html", {"leads": leads})

@csrf_exempt
def whatsapp_webhook(request):
    if request.method == "POST":
        from_number = request.POST.get("From", "").replace("whatsapp:", "")
        message_body = request.POST.get("Body", "").strip()
        if not from_number:
            return HttpResponse("Missing phone number", status=400)
        lead, created = Lead.objects.get_or_create(phone=from_number, defaults={"name": "New Lead"})
        response = MessagingResponse()
        reply_text = "Hello! Thanks for reaching out. You are now registered in our system." if created else "Welcome back! How can we assist you today?"
        response.message(reply_text)
        return HttpResponse(str(response), content_type="application/xml")
    return HttpResponse("Invalid request", status=400)

def home(request):
    return render(request, "leads/home.html")

@login_required
def dashboard(request):
    send_due_reminders()
    leads = Lead.objects.all()
    purchases = Purchase.objects.all()
    reminders = Reminder.objects.all()
    return render(request, 'leads/dashboard.html', {'leads': leads, 'purchases': purchases, 'reminders': reminders})

def user_login(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("dashboard")
    else:
        form = AuthenticationForm()
    return render(request, "leads/login.html", {"form": form})

def user_logout(request):
    logout(request)
    return redirect("login")

def user_register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("dashboard")
    else:
        form = UserCreationForm()
    return render(request, "leads/register.html", {"form": form})

def create_lead(request):
    if request.method == "POST":
        form = LeadForm(request.POST)
        if form.is_valid():
            lead = form.save()
            Reminder.objects.create(
                lead=lead,
                message="Welcome, do you know for how long we were waiting for you!",
                date=now(),
                status="Not Sent"
            )
            return redirect("lead_list")
    else:
        form = LeadForm()
    return render(request, "leads/lead_form.html", {"form": form})

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

def delete_lead(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    if request.method == "POST":
        lead.delete()
        return redirect("lead_list")
    return render(request, "leads/lead_confirm_delete.html", {"lead": lead})

def lead_detail(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    total_spent_by_lead = Purchase.objects.filter(lead=lead).aggregate(Sum('amount'))['amount__sum'] or 0
    total_spent_by_all = Purchase.objects.aggregate(Sum('amount'))['amount__sum'] or 1
    remaining_amount = total_spent_by_all - total_spent_by_lead
    pie_chart = go.Figure(data=[go.Pie(labels=["This Lead", "Other Leads"], values=[total_spent_by_lead, remaining_amount], marker=dict(colors=["#ffbc3b", "#1f77b4"])])])
    pie_chart_html = pie_chart.to_html(full_html=False)
    last_90_days = now() - timedelta(days=90)
    purchases = Purchase.objects.filter(lead=lead, purchase_date__gte=last_90_days)
    daily_spending = purchases.values('purchase_date__date').annotate(total_spent=Sum('amount')).order_by('purchase_date__date')
    if daily_spending:
        dates = [entry['purchase_date__date'].strftime('%Y-%m-%d') for entry in daily_spending]
        amounts = [entry['total_spent'] for entry in daily_spending]
        line_chart = go.Figure(data=go.Scatter(x=dates, y=amounts, mode='lines+markers', line=dict(color='blue'), marker=dict(size=6, color='red'), name="Daily Spending"))
        line_chart.update_layout(title="Daily Spending Trend (Last 90 Days)", xaxis_title="Date", yaxis_title="Amount (₹)")
        line_chart_html = line_chart.to_html(full_html=False)
    else:
        line_chart_html = None
    return render(request, "leads/lead_detail.html", {"lead": lead, "pie_chart": pie_chart_html, "line_chart": line_chart_html})

def lead_report(request):
    send_due_reminders()
    leads = Lead.objects.annotate(total_purchases=Count('purchases'), total_spent=Sum('purchases__amount')).order_by('-lead_score')
    return render(request, 'leads/lead_report.html', {'leads': leads})

def add_purchase(request):
    send_due_reminders()
    if request.method == 'POST':
        form = PurchaseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = PurchaseForm()
    return render(request, 'leads/add_purchase.html', {'form': form})
