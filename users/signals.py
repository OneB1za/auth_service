from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import UserProfileSettings

user = get_user_model()

@receiver(post_save, sender=user)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    # Создаём запись настроек профиля, если она отсутствует
    if created:
        UserProfileSettings.objects.create(user=instance)
    else:
        # Проверяем, есть ли связанные настройки профиля, и если есть, сохраняем
        if hasattr(instance, 'userprofilesettings'):
            instance.userprofilesettings.save()
