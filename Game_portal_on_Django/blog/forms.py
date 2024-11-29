from ckeditor.widgets import CKEditorWidget
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .models import *


class AddArticleForm(forms.ModelForm):
    '''Клас формирует форму для добавления статей'''
    content = forms.CharField(widget=CKEditorUploadingWidget(), label='Статья')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        '''
        Подстановка в поле "Сат" вместо прочерков значения "Категория не выбрана"
        '''
        self.fields['cat'].empty_label = 'Категория не выбрана'

    class Meta:
        model = GamePost
        # fields = '__all__'
        fields = ['title', 'content', 'photo', 'status', 'cat']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            # 'content': forms.Textarea(attrs={'cols': 80, 'rows': 10}),

        }

    def clean_title(self):
        '''Метод проверки длинны введенных данных в поле'''
        title = self.cleaned_data['title']
        if len(title) > 255:
            raise ValidationError('Длина превышает 255 символов')
        return title


class RegisterUserForm(UserCreationForm):
    '''Клас формирует форму Регистрации пользователя'''
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-input'}))
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'class': 'form-input'}))
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    password2 = forms.CharField(label='Повтор пароля', widget=forms.PasswordInput(attrs={'class': 'form-input'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
        labels = {
            'email': 'e-mail',
            'first_name': 'Имя',
            'last_name': 'Фамилия',
        }
        widget = {
            'email': forms.TextInput(attrs={'class': 'form-input'}),
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
        }

    # def clean_password2(self):   # не нужен перешол на класс
    #     cd = self.cleaned_data
    #     if cd['password'] != cd['password2']:
    #         raise forms.ValidationError("Пароли не совпадают!")
    #     return cd['password']

    def clean_email(self):
        '''Метод для проверки уникальности e-mail в User'''
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            # отбираем пользователей с указанным
            # e-mail и если они есть метод exists() вернет True
            # далее вызываем исключение иначе возвращаем email
            raise forms.ValidationError('Данный e-mail уже существует !')
        return email


class LoginUserForm(AuthenticationForm):
    '''Клас формирует форму Авторизации пользователя'''
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-input'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-input'}))


class CommentForm(forms.ModelForm):
    '''Клас формирует форму для добавления и редактирования
    Комментариев к статьям
    '''

    class Meta:
        model = Comment
        fields = ('content', 'photo', 'photo1', 'photo2', 'active')
        widgets = {
            'content': forms.Textarea(attrs={'cols': 80, 'rows': 10}),
        }


class ProfileUserForm(forms.ModelForm):
    username = forms.CharField(disabled=True, label='Логин', widget=forms.TextInput(attrs={'class': 'form-input'}))
    email = forms.CharField(disabled=True, label='E-mail', widget=forms.TextInput(attrs={'class': 'form-input'}))

    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'first_name', 'last_name']

    labels = {
        'first_name': 'Имя',
        'last_name': 'Фамилия',
    }

    widgets = {
        'first_name': forms.TextInput(attrs={'class': 'form-input'}),
        'last_name': forms.TextInput(attrs={'class': 'form-input'}),
    }


class UserPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(label='Старый пароль', widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    new_password1 = forms.CharField(label='Новый пароль', widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    new_password2 = forms.CharField(label='Повторение пароля',
                                    widget=forms.PasswordInput(attrs={'class': 'form-input'}))



