from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    

    class Meta:
        model = User
        fields = ["username", "email", "phone", "password1", "password2"]
        
        def clean_phone(self):
          phone = self.cleaned_data.get("phone")
  
          if User.objects.filter(phone=phone).exists():
              raise forms.ValidationError("This phone number is already registered.")
  
          return phone