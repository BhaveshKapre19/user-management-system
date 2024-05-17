from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.views.generic import FormView , TemplateView 
from .forms import CustomUserCreationForm,CustomAuthenticationForm,ProfileEditForm
from .models import CustomUser
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy


class RegisterView(FormView):
    form_class = CustomUserCreationForm
    template_name = 'user/register.html'

    def form_valid(self, form):
        form.save()
        username = form.cleaned_data.get('username')
        raw_password = form.cleaned_data.get('password1')
        user = authenticate(username=username, password=raw_password)
        login(self.request, user)
        return redirect('/')

class LoginView(FormView):
    form_class = CustomAuthenticationForm
    template_name = 'user/login.html'

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(self.request, user)
            return redirect('/')
        else:
            return self.form_invalid(form)


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fetch users with their avatars
        users_with_avatars = CustomUser.objects.all()
        context['users_with_avatars'] = users_with_avatars
        return context
    


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'user/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context
    

class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = ProfileEditForm
    template_name = 'user/edit-user.html'
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        return self.request.user