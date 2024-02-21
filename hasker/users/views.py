from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import LoginView
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView

from users.forms import LoginUserForm, RegisterUserForm
from users.models import User


class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'users/login.html'
    extra_context = {'title': 'Authentication'}

    def get_success_url(self):
        return reverse_lazy('question:home')


def register(request):
    if request.method == 'POST':
        form = RegisterUserForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            return render(request, 'users/register_done.html')
    else:
        form = RegisterUserForm()
    return render(request, 'users/register.html', {'form': form})


class UserDetailView(DetailView):
    model = User
    template_name = "users/detail.html"
    context_object_name = "user"
    slug_url_kwarg = "username"
    slug_field = "username"
