from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Atrakcja, Plan

class LogInForm(forms.Form):
    """
    Formularz logowania użytkownika.
    """
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class SignUpForm(UserCreationForm):
    """
    Formularz rejestracji użytkownika.
    """
    def __init__(self, *args, **kwargs):
        super(UserCreationForm,self).__init__(*args,**kwargs)

        for fieldname in ["username","password1","password2"]:
            self.fields[fieldname].help_text = None
    class Meta:
        model = User
        fields = ("username","first_name", "last_name", "email", "password1", "password2")
        widgets = {
            'password1': forms.PasswordInput(),
            'password2': forms.PasswordInput(),
        }

    def save(self, commit=True):
        user = super(SignUpForm, self).save(commit=False)
        if commit:
            user.save()
        return user

class StartLocation(forms.Form):
    """
    Formularz wyboru lokalizacji początkowej i trybu podróży.
    """
    start_location = forms.CharField()
    mode_choices = {
        ('driving', 'Pojazd'),
        ('walking', 'Pieszo')
    }
    mode = forms.ChoiceField(choices=mode_choices)

class PlanForm(forms.ModelForm):
    """
    Formularz tworzenia planu podróży.
    """
    atrakcje = forms.ModelMultipleChoiceField(queryset=Atrakcja.objects.all(), widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = Plan
        fields = ['id_klienta', 'nazwa_planu', 'opis_planu', 'atrakcje', 'data_utworzenia', 'obraz']