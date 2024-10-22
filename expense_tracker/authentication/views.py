from django.shortcuts import redirect, render
from django.views import View
import json
from django.http import JsonResponse
from django.contrib.auth.models import User
from validate_email import validate_email  # type: ignore
from django.contrib import messages
from django.core.mail import EmailMessage
from django.contrib import auth
# Create your views here.

class EmailValidationView(View):
    def post(self, request):
        data=json.loads(request.body)
        email=data['email']

        if not validate_email(email):
            return JsonResponse({'email_error':'Email is invalid'}, status=400)
        if User.objects.filter(email=email).exists():
            return JsonResponse({'email_error':'Email already exists. Pleaes enter a new email'}, status=409)
        return JsonResponse({'email_valid':True})
    

class UsernameValidationView(View):
    def post(self, request):
        data=json.loads(request.body)
        username=data['username']

        if not str(username).isalnum():
            return JsonResponse({'username_error':'username should only contain alphanumeric characters'}, status=400)
        if User.objects.filter(username=username).exists():
            return JsonResponse({'username_error':'Username already exists. Please choose a new username'}, status=409)
        return JsonResponse({'username_valid':True})

class RegistrationView(View):
    def get(self, request):
        return render(request, 'authentication/register.html')
    
    def post(self, request):
        username=request.POST['username']
        email=request.POST['email']
        password=request.POST['password']

        context={
            'fieldValues': request.POST
        }

        if not User.objects.filter(username=username).exists():
            if not User.objects.filter(email=email).exists():
                if len(password)<6:
                    messages.error(request, "Password must be greater than 6 chars.")
                    return render(request, 'authentication/register.html', context)
                user = User.objects.create_user(username=username,email=email)
                user.set_password(password)
                user.save()
                messages.success(request, "Acccount created successfully! Redirecting you to the login page")
                context['registration_success'] = True
                return render(request, 'authentication/register.html', context)
        return render(request, 'authentication/register.html')
    
class LoginView(View):

    def get(self, request):
        return render(request, 'authentication/login.html')
    
    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']

        if username and password:
            user = auth.authenticate(username=username, password=password)

            if user:
                if user.is_active:
                    auth.login(request, user)
                    messages.success(request, "Welcome, "+user.username+" You are now logged in.")
                    return redirect('expenses')
               
            messages.error(request, "Invalid credentials. Try again")
            return render(request, 'authentication/login.html')        
        messages.error(request, "Please fill in all fields")
        return render(request, 'authentication/login.html')


class LogoutView(View):
    def post(self, request):
        auth.logout(request)
        messages.success(request, "You have been logged out.")
        return redirect('login')