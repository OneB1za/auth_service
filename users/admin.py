from django.contrib import admin
from .models import CustomUser, FriendShip, UserProfileSettings


# Register your models here.

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'first_name', 'last_name', 'age', 'city', 'is_active']
    search_fields = ['username', 'first_name', 'last_name']


@admin.register(FriendShip)
class FriendShipAdmin(admin.ModelAdmin):
    list_display = ['user', 'friend', 'status', 'created_at']


@admin.register(UserProfileSettings)
class UserProfileSettingsAdmin(admin.ModelAdmin):
    list_display = ['user', 'invisible_friendlist']