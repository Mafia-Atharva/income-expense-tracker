from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns=[
    path('',views.index, name='expenses'),
    path('add-expense/', views.add_expense, name='add-expense'),
    path('edit-expense/<int:id>', views.expense_edit, name='expense_edit'),
    path('delete-expense/<int:id>', views.expense_delete, name='expense_delete'),
    path('search-expenses/',csrf_exempt(views.search_expenses), name='search_expenses'),
    path('expenses_category_summary/',csrf_exempt(views.expense_category_summary), name='expense_category_summary'),
    path('view_stats/',csrf_exempt(views.stats_view), name='stats_view'),
    path('export_csv/',csrf_exempt(views.export_csv), name='export_csv'),
    path('export_excel/',csrf_exempt(views.export_excel), name='export_excel'),
]