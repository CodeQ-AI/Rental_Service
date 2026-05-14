from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from .forms import RegisterForm, LoginForm, ProfileEditForm, CustomPasswordChangeForm
from .models import CustomUser


def register_view(request):
    if request.user.is_authenticated:
        return redirect('rentals:item_list')

    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, 'Добро пожаловать! Регистрация прошла успешно.')
        return redirect('rentals:item_list')

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('rentals:item_list')

    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        messages.success(request, f'Вы вошли как {user.email}.')
        next_url = request.GET.get('next', 'rentals:item_list')
        return redirect(next_url)

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    if request.method == 'POST':
        logout(request)
        messages.info(request, 'Вы вышли из системы.')
    return redirect('rentals:item_list')


def profile_view(request, pk):
    profile_user = get_object_or_404(CustomUser, pk=pk)
    is_owner = request.user.is_authenticated and request.user.pk == profile_user.pk
    return render(request, 'accounts/profile.html', {
        'profile_user': profile_user,
        'is_owner':     is_owner,
    })


@login_required
def profile_edit_view(request, pk):
    profile_user = get_object_or_404(CustomUser, pk=pk)

    if request.user.pk != profile_user.pk:
        messages.error(request, 'Вы не можете редактировать чужой профиль.')
        return redirect('accounts:profile', pk=pk)

    form = ProfileEditForm(
        request.POST or None,
        request.FILES or None,
        instance=profile_user,
    )
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Профиль успешно обновлён.')
        return redirect('accounts:profile', pk=pk)

    return render(request, 'accounts/profile_edit.html', {'form': form, 'profile_user': profile_user})


@login_required
def password_change_view(request):
    form = CustomPasswordChangeForm(user=request.user, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        messages.success(request, 'Пароль успешно изменён.')
        return redirect('accounts:profile', pk=request.user.pk)

    return render(request, 'accounts/password_change.html', {'form': form})