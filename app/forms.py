from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Profile


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar', 'phone']


class RegisterForm(UserCreationForm):
    phone = forms.CharField(max_length=30, required=True, label='Телефон')
    username = forms.CharField(label='Логин')
    email = forms.EmailField(label='Эл. почта')
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Подтверждение пароля', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'password1', 'password2']
