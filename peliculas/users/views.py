
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages

def index(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    else:
        return render(request,'users/profile.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirect to a success page.
            return HttpResponseRedirect(reverse('index'))
        else:
            # Return an 'invalid login' error message.
            return render(request, 'users/login.html', {'errors':['Invalid Login']})
    else:
        return render(request, 'users/login.html')

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))

def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Las contraseñas no coinciden.")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "El usuario ya existe.")
            return redirect("register")

        # Crear usuario
        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        return redirect("index")  # redirige al inicio después de registrarse

    # Si es GET, renderiza el formulario
    return render(request, "users/register.html")
    
