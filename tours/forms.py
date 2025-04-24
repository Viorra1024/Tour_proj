from django import forms
from django.contrib.auth.models import User
from .models import Profile # Убедись, что импортировал свою модель Profile

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField() # Добавляем поле email для валидации

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email'] # Поля User, которые можно менять

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        # Перечисли поля из твоей модели Profile, которые есть в форме settings.html
        fields = ['phone_number', 'address', 'bio', 'image']
        # Если хочешь сделать поле изображения необязательным на уровне формы:
        # widgets = {
        #     'image': forms.FileInput(attrs={'required': False}),
        # }