from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.validators import MaxValueValidator
from django.db import models
from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager


class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('email должен быть указан')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)

        for field in ['username', 'first_name', 'last_name', 'age', 'gender', 'city']:
            if not extra_fields.get(field):
                raise ValueError(f'Поле {field} должно быть указано для обычных пользователей.')

        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Суперпользователь должен иметь is_superuser=True.')
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Суперпользователь должен иметь is_staff=True.')

        # For superusers
        extra_fields.setdefault('username', 'admin')
        extra_fields.setdefault('first_name', '')
        extra_fields.setdefault('last_name', '')
        extra_fields.setdefault('age', None)
        extra_fields.setdefault('gender', '')
        extra_fields.setdefault('city', '')

        return self._create_user(email, password, **extra_fields)


# Модель пользователя
class CustomUser(AbstractBaseUser, PermissionsMixin):
    GENDERS = (("1", "Male"),
               ("2", "Female"))

    email = models.EmailField(max_length=64, unique=True, verbose_name='Электронная почта')
    username = models.CharField(max_length=48, unique=True, verbose_name='Имя пользователя')
    first_name = models.CharField(max_length=48, verbose_name='Имя')
    last_name = models.CharField(max_length=48, verbose_name='Фамилия')
    gender = models.CharField(choices=GENDERS, max_length=1, verbose_name='Гендер', blank=True, default='')
    age = models.PositiveIntegerField(validators=[MaxValueValidator(100)], verbose_name='Возраст', blank=True,
                                      null=True)
    city = models.CharField(max_length=48, verbose_name='Город')
    bio = models.TextField(max_length=1000, null=True, blank=True)
    data_joined = models.DateTimeField(auto_now_add=True, verbose_name='Зарегистрирован')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)  # ''' ПУТЬ ЗАГРУЗКИ '''
    is_active = models.BooleanField(default=True, verbose_name='Состояние аккаунта')
    is_staff = models.BooleanField(default=False, verbose_name='Статус персонала')  #

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def get_friends(self):
        friends = FriendShip.objects.filter(user=self, status='accepted').values_list('friend', flat=True)
        return CustomUser.objects.filter(id__in=friends)

    def add_friend(self, friend):
        """Отправляет запрос на добавление в друзья"""
        if self == friend:
            raise ValueError('Нельзя добавить в друзья самого себя')
        if FriendShip.objects.filter(user=self, friend=friend).exists():
            raise ValueError('Такой запрос в друзья уже существует')
        FriendShip.objects.create(user=self, friend=friend, status='requested')

    def remove_friend(self, friend):
        FriendShip.objects.filter(user=self, friend=friend).delete()
        FriendShip.objects.filter(user=friend, friend=self).delete()


class FriendShip(models.Model):
    STATUS_CHOICES = [
        ('requested', 'Requested'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected')
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='friend_requests_sent', on_delete=models.CASCADE)
    friend = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='friend_requests_received',
                               on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='requested')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'friend')
        verbose_name = 'Дружба'
        verbose_name_plural = 'Дружба'

    def __str__(self):
        return f"{self.user} - {self.friend} ({self.status})"

class UserProfileSettings(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, unique=True, null=True, blank=True)
    invisible_friendlist = models.BooleanField(default=False, help_text='Закрытый список ваших друзей')

    class Meta:
        verbose_name = 'Настройки профиля'
        verbose_name_plural = 'Настройки профиля'
