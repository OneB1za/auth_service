from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model
from django import forms
from .models import CustomUser, FriendShip, UserProfileSettings

User = get_user_model()


class UserLoginForm(AuthenticationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'password']


class UserRegistrForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Имя пользователя'
        self.fields['email'].label = 'Почта'
        self.fields['first_name'].label = 'Имя'
        self.fields['last_name'].label = 'Фамилия'
        self.fields['gender'].label = 'Гендер'
        self.fields['age'].label = 'Возраст'
        self.fields['city'].label = 'Город'
        self.fields['bio'].label = 'Статус'

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'gender', 'age', 'city', 'bio']


class AddFriendForm(forms.Form):
    friend_id = forms.IntegerField(widget=forms.HiddenInput())

    def clean_friend_id(self):
        friend_id = self.cleaned_data['friend_id']
        if not User.objects.filter(id=friend_id).exists():
            raise forms.ValidationError('Такого пользователя не существует')
        return friend_id


class RejectFriendForm(forms.Form):
    request_id = forms.IntegerField(widget=forms.HiddenInput())

    def clean_request_id(self):
        request_id = self.cleaned_data['request_id']
        if not FriendShip.objects.filter(id=request_id).exists():
            raise forms.ValidationError('Такого пользователя не существует')
        return request_id


class AcceptFriendForm(forms.Form):
    request_id = forms.IntegerField(widget=forms.HiddenInput())

    def clean_request_id(self):
        request_id = self.cleaned_data['request_id']
        if not FriendShip.objects.filter(id=request_id).exists():
            raise forms.ValidationError('Такого пользователя не существует')
        return request_id


class UserProfileSettingsForm(forms.ModelForm):
    class Meta:
        model = UserProfileSettings
        fields = ['invisible_friendlist']
        labels = {'invisible_friendlist': 'Скрыть список друзей'}
