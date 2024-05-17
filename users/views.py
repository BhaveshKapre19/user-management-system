from django.contrib.auth import authenticate, login, logout , get_user_model
from django.shortcuts import render, redirect
from django.views.generic import FormView, TemplateView, View
from .forms import CustomUserCreationForm, CustomAuthenticationForm, ProfileEditForm
from .models import CustomUser
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import UpdateView , DeleteView
from django.urls import reverse_lazy
from django.contrib import messages


class RegisterView(FormView):
    form_class = CustomUserCreationForm
    template_name = 'user/register.html'
    success_url = reverse_lazy('home')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, 'You are already registered and logged in.')
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save(commit=False)
    
        if 'avatar' in self.request.FILES:
            user.avatar = self.request.FILES['avatar']
        else:
            user.avatar = None

        user.save()

        email = form.cleaned_data.get('email')
        raw_password = form.cleaned_data.get('password1')
        user = authenticate(email=email, password=raw_password)
        if user is not None:
            login(self.request, user)
            messages.success(self.request, 'Registration successful. You are now logged in.')
            return redirect(self.get_success_url())
        else:
            messages.error(self.request, 'Authentication failed. Please try again.')
            return redirect('register')

    def form_invalid(self, form):
        messages.error(self.request, 'Registration failed. Please correct the errors below.')
        return super().form_invalid(form)


class LoginView(FormView):
    form_class = CustomAuthenticationForm
    template_name = 'user/login.html'
    success_url = reverse_lazy('home')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, 'You are already logged in.')
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(self.request, user)
            messages.success(self.request, 'Login successful.')
            return redirect(self.get_success_url())
        else:
            messages.error(self.request, 'Invalid username or password. Please try again.')
            return self.form_invalid(form)


class LogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, 'You have successfully logged out.')
        return redirect('login')


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users_with_avatars'] = CustomUser.objects.all()
        return context


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'user/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        print(context['user'])
        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = ProfileEditForm
    template_name = 'user/edit-user.html'
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Update failed. Please correct the errors below.')
        return super().form_invalid(form)
    


class UserDeleteView(LoginRequiredMixin, DeleteView):
    model = CustomUser
    success_url = reverse_lazy('login')  # Redirect to home after deletion
    template_name = 'user/user_confirm_delete.html'  # Confirmation template

    def get_object(self, queryset=None):
        # Return the currently logged-in user
        return self.request.user

    def delete(self, request, *args, **kwargs):
        # Delete the user's avatar file
        if self.request.user.avatar:
            self.request.user.avatar.delete()
        # Logout the user
        LogoutView.as_view()(self.request)
        # Add success message
        messages.success(request, 'Your account has been deleted.')
        return super().delete(request, *args, **kwargs)
