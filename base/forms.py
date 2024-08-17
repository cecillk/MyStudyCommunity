from django.forms import ModelForm
from .models import Room
from django.contrib.auth.models import User



#IMPORTANT :'ModelForm' is a special form class that automatically generates form fields based on a Django model.
class RoomForm(ModelForm):
    # Define the form based on the Room model
    class Meta:
        # Specify the model that this form is associated with
        model = Room
        
        # Specify which fields should be included in the form
        # '__all__' includes all fields from the Room model
        fields = '__all__'
        exclude = ['host', 'participants']


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']
        