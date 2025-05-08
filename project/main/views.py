from django.shortcuts import render
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