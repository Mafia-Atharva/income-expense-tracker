from django.shortcuts import render, redirect
import os
import json
from django.conf import settings
from .models import UserPreferences
from django.contrib import messages

def index(request):
    exists = UserPreferences.objects.filter(user=request.user).exists()
    user_preferences = None
    currency_data = []  # Initialize the variable
    file_path = os.path.join(settings.BASE_DIR, 'currencies.json')
    with open(file_path) as json_file:
        data = json.load(json_file)
        for k, v in data.items():
            currency_data.append({'key': k, 'value': v})

    if exists:
        user_preferences = UserPreferences.objects.get(user=request.user)

    if request.method == 'GET':
        return render(request, 'preferences/index.html', {'currencies': currency_data, 'user_preferences': user_preferences})
    else:
        currency = request.POST.get('currency')
        if exists:
            user_preferences.currency = currency
            user_preferences.save()
        else:
            UserPreferences.objects.create(user=request.user, currency=currency)
        messages.success(request, "Currency saved successfully")
        return render(request, 'preferences/index.html', {'currencies': currency_data, 'user_preferences': user_preferences})
