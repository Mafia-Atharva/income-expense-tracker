import json
from django.http import JsonResponse
from django.shortcuts import redirect, render
from .models import Source, Income
from django.core.paginator import Paginator
from userpreferences.models import UserPreferences
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib import messages
from django.utils.timezone import now

# Create your views here.

@login_required(login_url='authentication/login')
@never_cache
def index(request):
    sources= Source.objects.all()
    income = Income.objects.filter(owner=request.user)
    paginator=Paginator(income,8)
    page_number=request.GET.get('page')
    currency=UserPreferences.objects.get(user=request.user)
    page_obj=Paginator.get_page(paginator,page_number)
    context={
        'income':income,
        'page_obj':page_obj,
        'currency':currency,
    }
    return render(request, 'income/index.html', context)

@login_required(login_url='authentication/login')
@never_cache
def add_income(request):
    sources= Source.objects.all()
    context={
            'sources': sources,
            'values': request.POST,
        }
    if request.method=="POST":
        amount=request.POST['amount']
        description=request.POST['description']
        date=request.POST['income_date']
        source=request.POST['source']

        if not amount :
            messages.error(request, "Amount must be greater than 0")
            return render(request,'income/add_income.html', context)
        if not amount.isdecimal():
            messages.error(request, "Amount must be a number")
            return render(request,'income/add_income.html', context)
        if not description:
            messages.error(request, "Description is required")
            return render(request,'income/add_income.html', context)
        if not date:
            date = now()
        Income.objects.create(owner=request.user,amount=amount,date=date, source=source, description=description)
        messages.success(request, "Income saved successfully")
        return redirect('income')
        
    if request.method=="GET":
        return render(request, 'income/add_income.html', context)


def income_edit(request, id):
    sources= Source.objects.all()
    income=Income.objects.get(pk=id)
    context={
        'income':income,
        'values':income,
        'sources':sources
    }
    if request.method=="GET":
        return render(request, 'income/edit_income.html', context)
        
    if request.method=="POST":
        amount=request.POST['amount']
        description=request.POST['description']
        date=request.POST['income_date']
        source=request.POST['source']

        if not amount:
            messages.error(request, "Amount must be greater than 0")
            return render(request,'income/edit_income.html', context)
        if not description:
            messages.error(request, "Description is required")
            return render(request,'income/edit_income.html', context)
        if not date:
            date = now()

        income.amount=amount
        income.date=date
        income.source=source
        income.description=description
        income.save()
        messages.success(request, "Income edited successfully")
        return redirect('income')
    
def income_delete(request, id):
    income=Income.objects.get(pk=id)
    income.delete()
    messages.success(request, "Income deleted successfully")
    return redirect('income')


def search_income(request):
    if request.method=='POST':
        search_str=json.loads(request.body).get('seachText')
        income=Income.objects.filter(amount__istartswith=search_str, owner=request.user) | Income.objects.filter(date__istartswith=search_str, owner=request.user) | Income.objects.filter(description__icontains=search_str, owner=request.user) | Income.objects.filter(source__icontains=search_str, owner=request.user)
        data = income.values()
        return JsonResponse(list(data), safe=False)