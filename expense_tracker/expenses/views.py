from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from .models import Category, Expense
from django.contrib import messages
from django.utils.timezone import now
from django.core.paginator import Paginator
import json
from django.http import JsonResponse, HttpResponse
from userpreferences.models import UserPreferences
import datetime
import csv
import xlwt


@login_required(login_url='authentication/login')
@never_cache
def index(request):
    categories = Category.objects.all()
    expenses = Expense.objects.filter(owner=request.user)
    paginator = Paginator(expenses, 8)
    page_number = request.GET.get('page')
    
    # Get or create UserPreferences for the current user
    user_preferences, created = UserPreferences.objects.get_or_create(user=request.user)
    
    page_obj = paginator.get_page(page_number)
    
    context = {
        'expenses': expenses,
        'page_obj': page_obj,
        'currency': user_preferences.currency,  # Access currency from user_preferences
    }
    return render(request, 'expenses/index.html', context)

@login_required(login_url='authentication/login')
@never_cache
def add_expense(request):
    categories= Category.objects.all()
    context={
            'categories': categories,
            'values': request.POST,
        }
    if request.method=="POST":
        amount=request.POST['amount']
        description=request.POST['description']
        date=request.POST['expense_date']
        category=request.POST['category']

        if not amount :
            messages.error(request, "Amount must be greater than 0")
            return render(request,'expenses/add_expense.html', context)
        if not amount.isdecimal():
            messages.error(request, "Amount must be a number")
            return render(request,'expenses/add_expense.html', context)
        if not description:
            messages.error(request, "Description is required")
            return render(request,'expenses/add_expense.html', context)
        if not date:
            date = now()
        Expense.objects.create(owner=request.user,amount=amount,date=date, category=category, description=description)
        messages.success(request, "Expense added successfully")
        return redirect('expenses')
        
    if request.method=="GET":
        return render(request, 'expenses/add_expense.html', context)



def expense_edit(request, id):
    categories= Category.objects.all()
    expense=Expense.objects.get(pk=id)
    context={
        'expense':expense,
        'values':expense,
        'categories':categories
    }
    if request.method=="GET":
        return render(request, 'expenses/edit-expense.html', context)
        
    if request.method=="POST":
        amount=request.POST['amount']
        description=request.POST['description']
        date=request.POST['expense_date']
        category=request.POST['category']

        if not amount:
            messages.error(request, "Amount must be greater than 0")
            return render(request,'expenses/edit-expense.html', context)
        if not description:
            messages.error(request, "Description is required")
            return render(request,'expenses/edit-expense.html', context)
        if not date:
            date = now()
        expense.owner=request.user
        expense.amount=amount
        expense.date=date
        expense.category=category
        expense.description=description
        expense.save()
        messages.success(request, "Expense edited successfully")
        return redirect('expenses')
    
def expense_delete(request, id):
    expense=Expense.objects.get(pk=id)
    expense.delete()
    messages.success(request, "Expense deleted successfully")
    return redirect('expenses')


def search_expenses(request):
    if request.method=='POST':
        search_str=json.loads(request.body).get('seachText')
        expenses=Expense.objects.filter(amount__istartswith=search_str, owner=request.user) | Expense.objects.filter(date__istartswith=search_str, owner=request.user) | Expense.objects.filter(description__icontains=search_str, owner=request.user) | Expense.objects.filter(category__icontains=search_str, owner=request.user)
        data = expenses.values()
        return JsonResponse(list(data), safe=False)
    
def expense_category_summary(request):
    todays_data=datetime.date.today()
    six_months_ago=todays_data-datetime.timedelta(days=30*6)
    expenses=Expense.objects.filter(owner=request.user,date__gte=six_months_ago,date__lte=todays_data)
    finalrep={}

    def getCategory(expense):
        return expense.category
    
    def get_expense_category_amount(category):
        amount=0
        filter_by_category=expenses.filter(category=category)
        for item in filter_by_category:
            amount+=item.amount
        return amount
    
    category_list=list(set(map(getCategory, expenses)))

    for x in expenses:
        for y in category_list:
            finalrep[y]=get_expense_category_amount(y)

    return JsonResponse({'expense_category_data':finalrep}, safe=False)


def stats_view(request):
    return render(request, 'expenses/stats.html')

def export_csv(request):
    # Correct MIME type for CSV
    response = HttpResponse(content_type='text/csv')
    # Proper Content-Disposition with closing quote
    response['Content-Disposition'] = 'attachment; filename="Expenses-' + str(datetime.datetime.now()) + '.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Amount', 'Description', 'Category', 'Date'])

    # Fetching expenses for the logged-in user
    expenses = Expense.objects.filter(owner=request.user)

    # Writing each expense's data
    for expense in expenses:
        writer.writerow([expense.amount, expense.description, expense.category, expense.date])

    return response


def export_excel(request):
    # Correct MIME type for Excel file
    response = HttpResponse(content_type='application/ms-excel')
    # Proper Content-Disposition with closing quote
    response['Content-Disposition'] = 'attachment; filename="Expenses-' + str(datetime.datetime.now()) + '.xls"'
    
    # Create a workbook and a worksheet
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Expenses')

    # First row will contain column headers
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    
    # Defining the columns
    columns = ['Amount', 'Description', 'Category', 'Date']

    # Writing the column headers
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Now writing the actual data
    font_style = xlwt.XFStyle()
    rows = Expense.objects.filter(owner=request.user).values_list('amount', 'description', 'category', 'date')

    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, str(row[col_num]), font_style)

    # Save the workbook to response
    wb.save(response)

    return response