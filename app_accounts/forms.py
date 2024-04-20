from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm, UsernameField, PasswordResetForm, SetPasswordForm
from django.contrib.auth.models import User

from django.core.exceptions import ValidationError


def validate_username_length(value, min_length=6):
    if len(value) < min_length:  # 7 because it should be more than 6 characters
        raise ValidationError('Username must be at least 6 characters long.')


class RegistrationForm(UserCreationForm):
    username = forms.CharField(
        label= ("Email"),
        validators=[validate_username_length],
        widget=forms.EmailInput(attrs={
            'placeholder': 'Your email',
            'required': 'required',
            'class': 'form-input',
        })
    )

    first_name = forms.CharField(
        label= ("Full Name"),
        widget=forms.TextInput(attrs={
            'placeholder': 'Your full name',
            'required': 'required',
            'minlength': '6',
            'maxlength': '50',
            'class': 'form-input',
        })
    )

    password1 = forms.CharField(
        label=("Password"),
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Your Password',
            'required': 'required',
            'class': 'form-input',
        }),
    )   
    password2 = forms.CharField(
        label=("Password Confirmation"),
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Password Confirmation',
            'required': 'required',
            'class': 'form-input',
        }),
    )

    class Meta:
      model = User
      fields = ('username', 'first_name')


class LoginForm(AuthenticationForm):
    username = UsernameField(
        label=("Email"),
        widget=forms.TextInput(attrs={
            "placeholder": "Your username or email",
            'class': 'form-input'}))
    password = forms.CharField(
        label=("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={
            "placeholder": "Your password",
            'class': 'form-input'}),
    )
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "checkbox"}),)
    

class UserPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={
        'placeholder': 'Old Password',
        'class': 'form-input',
    }), label='Old Password')
    new_password1 = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={
        'placeholder': 'New Password',
        'class': 'form-input',
    }), label="New Password")
    new_password2 = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={
        'placeholder': 'Confirm New Password',
        'class': 'form-input',
    }), label="Confirm New Password")


class UserPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-input', 
        'placeholder': 'Your registered email'}))

class UserSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={
        'placeholder': 'New Password'
    }), label="New Password")
    new_password2 = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={
        'class': 'form-input', 
        'placeholder': 'Confirm New Password'
    }), label="Confirm New Password")
    


