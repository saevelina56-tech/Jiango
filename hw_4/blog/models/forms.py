from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
import re

from models import CustomUser, Profile

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    city = forms.CharField(max_length=100, required=False)
    bio = forms.CharField(widget=forms.Textarea, required=False)
    
    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'password1', 'password2')
    
    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        
        if len(password) < 8:
            raise ValidationError('Пароль должен быть минимум 8 символов')
        if not re.search(r'[A-Z]', password):
            raise ValidationError('Пароль должен содержать заглавную букву')
        if not re.search(r'[a-z]', password):
            raise ValidationError('Пароль должен содержать строчную букву')
        if not re.search(r'\d', password):
            raise ValidationError('Пароль должен содержать цифру')
        if not re.search(r'[!@#$%^&*]', password):
            raise ValidationError('Пароль должен содержать спецсимвол')
        
        return password
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError('Пользователь с таким email уже существует')
        return email