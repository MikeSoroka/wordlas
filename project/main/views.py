from django.shortcuts import render
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from .forms import UserRegisterForm, UserLoginForm
from django.views.decorators.csrf import csrf_exempt
from .forms import WordForm

# Create your views here.

def index(request):
    form = WordForm()
    
    if request.method == 'POST':
        form = WordForm(request.POST)
        if form.is_valid():
            # Form is valid, the word contains only Lithuanian characters
            # Just initialize a new form as we're handling the actual game logic in JS
            form = WordForm()
    
    return render(request, 'index.html', {'form': form})

def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully! You can now log in.')
            return redirect('user_login')
    else:
        form = UserRegisterForm()

    return render(request, 'register.html', {'form': form})

def user_login(request):
    if request.method == "POST":
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, 'Successfully logged in!')
                return redirect("index")
            else:
                messages.error(request, 'Invalid username or password')
    else:
        form = UserLoginForm()

    return render(request, 'login.html', {'form': form})
