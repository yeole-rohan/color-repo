from django import forms
from .models import Banner, User, CreatorDesign, Address
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import EmailValidator, RegexValidator
from django.forms import ModelForm

class RegisterUser(UserCreationForm):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female')
    )
    gender = forms.ChoiceField(choices=GENDER_CHOICES, widget=forms.RadioSelect(),label='Gender',) 
    is_creator = forms.BooleanField(label = 'Register as a creator', required=False)
    class Meta: 
        model = User 
        fields = ('phone_number', 'username', 'email', 'first_name', 'last_name', 'is_creator', 'gender') 

class UpdateProfile(forms.ModelForm):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female')
    )
    gender = forms.ChoiceField(choices=GENDER_CHOICES, widget=forms.RadioSelect(),label='Gender')
    class Meta:
        model = User
        fields = ('phone_number', 'username', 'email', 'first_name', 'last_name', 'gender') 

class CreatorDesignForm(forms.ModelForm):
    
    class Meta:
        model = CreatorDesign
        fields = ("design_description", "design_name", "design_image")
 
class AddressForm(forms.ModelForm):

    class Meta:
        model = Address
        fields = ("address","locality", "landmark", "city", "state", "pin_code")

class CollaborateForm(forms.Form):
    full_name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    phone_regex = RegexValidator(regex=r'^\d{10,10}$', message="Phone number must be entered in the format: '1234567890'. Up to 10 digits allowed.")
    phone_number = forms.CharField(validators=[phone_regex], max_length=10,required=True)
    username = forms.CharField( max_length=50, required=True)
    design_file = forms.FileField( required=True)
    design_desc = forms.CharField( widget=forms.Textarea(), required=False)
    design_name = forms.CharField( required=True)

    

