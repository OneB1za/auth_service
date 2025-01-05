import logging

from django.contrib.auth import login, authenticate, logout
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.views.generic.edit import FormView, UpdateView
from django.contrib import messages
from .models import CustomUser, FriendShip, UserProfileSettings
from .forms import UserRegistrForm, UserLoginForm, AddFriendForm, RejectFriendForm, AcceptFriendForm, \
    UserProfileSettingsForm


logger = logging.getLogger('main')

def registration_view(request):
    if request.method == 'POST':
        form = UserRegistrForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # user.username = user.username.lower()
            user.save()
            messages.success(request, 'Вы успешно создали аккаунт')
            login(request, user)
            return redirect('/')
        else:
            return render(request, 'users/register.html', {'form': form})
    else:
        form = UserRegistrForm()
        return render(request, 'users/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Вы успешно вошли в аккаунт, {request.user.username}')
                return redirect('/')
        else:
            return render(request, 'users/login.html', {'form': form})
    else:
        form = UserLoginForm()
        return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, 'Вы успешно вышли из аккаунта')
    return redirect('/')


class UserProfileView(View):

    def get(self, request, *args, **kwargs):
        logger.info('go into UserProfileView')
        username_slug = kwargs.get('username')
        user = CustomUser.objects.get(username=username_slug)
        try:
            if user.username != request.user.username:
                privacy_settings = UserProfileSettings.objects.get(user=user)
                if privacy_settings.invisible_friendlist:
                    friend_list = user.get_friends()
                else:
                    friend_list = None
            else:
                friend_list = user.get_friends()
        except UserProfileSettings.DoesNotExist:
            friend_list = user.get_friends()
        if request.user.is_authenticated:
            is_friend = FriendShip.objects.filter(user=request.user, friend=user, status='accepted').exists() or \
                        FriendShip.objects.filter(user=user, friend=request.user, status='accepted').exists()
        else:
            is_friend = 'rejected'
        return render(request, 'users/user_profile.html',
                      context={'user': user, 'friend_list': friend_list, 'is_friend': is_friend})


class AddFriendView(LoginRequiredMixin, FormView):
    template_name = 'users/user_profile.html'
    form_class = AddFriendForm

    def form_valid(self, form):
        friend_id = form.cleaned_data['friend_id']
        friend = CustomUser.objects.get(id=friend_id)
        try:
            self.request.user.add_friend(friend)
            messages.success(self.request, 'Запрос на добавление в друзья успешно отправлен!')
        except ValueError as e:
            messages.error(self.request, str(e))
        return super().form_valid(form)

    def get_success_url(self):
        """
        Возвращает URL профиля добавленного друга.
        Используйте username друга для создания URL.
        """
        friend_id = self.request.POST.get('friend_id')
        friend = CustomUser.objects.get(id=friend_id)
        return reverse('users:user_profile', kwargs={'username': friend.username})


class RejectFriendView(LoginRequiredMixin, FormView):
    template_name = 'users/my_requested_friend.html'
    form_class = RejectFriendForm

    def form_valid(self, form):
        request_id = form.cleaned_data['request_id']
        friendship = FriendShip.objects.get(id=request_id)
        if friendship.friend == self.request.user:
            friendship.status = 'rejected'
            friendship.save()
            messages.success(self.request, "Запрос в друзья успешно отклонен")
        else:
            messages.error(self.request, "Вы не можете отклонить этот запрос")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('users:user_profile', kwargs={'username': self.request.user.username})


class AcceptFriendView(LoginRequiredMixin, FormView):
    template_name = 'users/my_requested_friend.html'
    form_class = AcceptFriendForm

    def form_valid(self, form):
        request_id = form.cleaned_data['request_id']
        with transaction.atomic():  # Используем атомарные транзакции для обеспечения целостности данных
            friendship = FriendShip.objects.get(id=request_id)
            if friendship.friend == self.request.user:
                # Обновляем существующую запись
                friendship.status = 'accepted'
                friendship.save()

                # Создаем зеркальную запись
                FriendShip.objects.create(
                    user=friendship.friend,  # Текущий пользователь, который принимает запрос
                    friend=friendship.user,  # Пользователь, отправивший запрос
                    status='accepted'  # Сразу устанавливаем статус как принятый
                )
                messages.success(self.request, "Вы успешно приняли запрос в друзья")
            else:
                messages.error(self.request, "Вы не можете принять этот запрос")
            return super().form_valid(form)

    def get_success_url(self):
        return reverse('users:user_profile', kwargs={'username': self.request.user.username})


class RemoveFriendView(LoginRequiredMixin, View):
    def post(self, request, username):
        user = request.user
        friend = get_object_or_404(CustomUser, username=username)
        if FriendShip.objects.filter(user=user, friend=friend, status='accepted').exists() or \
                FriendShip.objects.filter(user=friend, friend=user, status='accepted').exists():
            user.remove_friend(friend)
            messages.success(request, 'Друг успешно удален.')
        else:
            messages.error(request, 'Не удалось найти такого друга.')
        return redirect('users/user_profile', username=user.username)


class GetMyRequestedFriendsView(LoginRequiredMixin, ListView):
    template_name = 'users/my_requested_friend.html'  # friendlist
    model = CustomUser
    context_object_name = 'friend_requests'

    def get_queryset(self):
        return FriendShip.objects.filter(friend=self.request.user, status='requested')




class FriendlistView(ListView):
    template_name = 'users/frinedlist.html'
    model = CustomUser

    def get(self, request, *args, **kwargs):
        username_slug = kwargs.get('username')
        user = CustomUser.objects.get(username=username_slug)
        friend_list = user.get_friends()
        return render(request, 'users/friendlist.html', context={'friend_list': friend_list, 'user': user})


class UserProfileSettingsView(LoginRequiredMixin,UpdateView):
    template_name = 'users/user_profile_settings.html'
    model = UserProfileSettings
    form_class = UserProfileSettingsForm

    def get_success_url(self):
        return reverse('users:user_profile', kwargs={'username': self.request.user.username})

    def form_valid(self, form):
        messages.success(self.request, 'Настройки успешно обновлены!')
        return super().form_valid(form)

    def get_object(self):
        return UserProfileSettings.objects.get(user=self.request.user)

