from django.contrib.auth.forms import (
    AuthenticationForm,
    UserCreationForm
)

from users.models import User


class CustomAuthenticationForm(AuthenticationForm):

    class Meta:
        model = User
        fields = ["username", "password"]


class CustomerSignUpForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ("email", 'first_name', 'last_name')


class StoreSignUpForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = User  
        fields = UserCreationForm.Meta.fields + ('email', 'first_name', 'last_name')

