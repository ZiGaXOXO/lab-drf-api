from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import RegistrationForm

def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Регистрация успешна. Пожалуйста, войдите.")
            return redirect('lab2:login')
    else:
        form = RegistrationForm()
    return render(request, 'lab2/register.html', {'form': form})
