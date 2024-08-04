from django import forms

from eservice.models import Newsletter


class NewsletterForm(forms.ModelForm):
    class Meta:
        model = Newsletter
        fields = '__all__'
        exclude = ('status', 'date_time_next_sent',)

        widgets = {
            'date_time_first_sent': forms.TextInput(attrs={'type': 'datetime-local'}),
            'date_time_last_sent': forms.TextInput(attrs={'type': 'datetime-local'}),
        }

    def clean_date_time_last_sent(self):
        cleaned_data = self.cleaned_data.get('date_time_last_sent')
        if cleaned_data and cleaned_data < self.cleaned_data.get('date_time_first_sent'):
            raise forms.ValidationError("Дата последнего отправления не может быть раньше даты первого отправления")
        return cleaned_data
