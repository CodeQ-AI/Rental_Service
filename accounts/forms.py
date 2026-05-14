from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser

BOOTSTRAP = 'form-control'
BS_SELECT = 'form-select'


class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': BOOTSTRAP, 'placeholder': 'Придумайте пароль'})
    )
    password2 = forms.CharField(
        label='Повтор пароля',
        widget=forms.PasswordInput(attrs={'class': BOOTSTRAP, 'placeholder': 'Повторите пароль'})
    )

    class Meta:
        model  = CustomUser
        fields = ('email', 'first_name', 'last_name', 'phone')
        widgets = {
            'email':      forms.EmailInput(attrs={'class': BOOTSTRAP, 'placeholder': 'example@mail.com'}),
            'first_name': forms.TextInput(attrs={'class': BOOTSTRAP, 'placeholder': 'Имя'}),
            'last_name':  forms.TextInput(attrs={'class': BOOTSTRAP, 'placeholder': 'Фамилия'}),
            'phone':      forms.TextInput(attrs={'class': BOOTSTRAP, 'placeholder': '+7 (___) ___-__-__'}),
        }

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже существует.')
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '')
        if phone:
            digits = ''.join(filter(str.isdigit, phone))
            if len(digits) < 10:
                raise forms.ValidationError('Введите корректный номер телефона (минимум 10 цифр).')
        return phone

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password1')
        p2 = cleaned_data.get('password2')
        if p1 and p2:
            if p1 != p2:
                raise forms.ValidationError('Пароли не совпадают.')
            validate_password(p1)
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': BOOTSTRAP,
            'placeholder': 'example@mail.com',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': BOOTSTRAP, 'placeholder': 'Ваш пароль'})
    )

    error_messages = {
        'invalid_login': 'Неверный email или пароль.',
        'inactive':      'Этот аккаунт отключён.',
    }


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model  = CustomUser
        fields = ('first_name', 'last_name', 'phone', 'avatar')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': BOOTSTRAP}),
            'last_name':  forms.TextInput(attrs={'class': BOOTSTRAP}),
            'phone':      forms.TextInput(attrs={'class': BOOTSTRAP, 'placeholder': '+7 (___) ___-__-__'}),
            'avatar':     forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '')
        if phone:
            digits = ''.join(filter(str.isdigit, phone))
            if len(digits) < 10:
                raise forms.ValidationError('Введите корректный номер телефона.')
        return phone

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar and hasattr(avatar, 'size'):
            if avatar.size > 2 * 1024 * 1024:
                raise forms.ValidationError('Размер аватара не должен превышать 2 МБ.')
            allowed = ('image/jpeg', 'image/png', 'image/webp')
            if hasattr(avatar, 'content_type') and avatar.content_type not in allowed:
                raise forms.ValidationError('Допустимые форматы: JPEG, PNG, WEBP.')
        return avatar


class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label='Текущий пароль',
        widget=forms.PasswordInput(attrs={'class': BOOTSTRAP, 'placeholder': 'Текущий пароль'})
    )
    new_password1 = forms.CharField(
        label='Новый пароль',
        widget=forms.PasswordInput(attrs={'class': BOOTSTRAP, 'placeholder': 'Новый пароль'})
    )
    new_password2 = forms.CharField(
        label='Повтор нового пароля',
        widget=forms.PasswordInput(attrs={'class': BOOTSTRAP, 'placeholder': 'Повторите новый пароль'})
    )

    def clean_new_password1(self):
        password = self.cleaned_data.get('new_password1')
        if password:
            validate_password(password, self.user)
        return password