from django import forms

from eservice.models import Newsletter


class NewsletterForm(forms.ModelForm):
    class Meta:
        model = Newsletter
        fields = '__all__'

        widgets = {
            'date_time_first_sent': forms.TextInput(attrs={'type': 'datetime-local'}),
        }
