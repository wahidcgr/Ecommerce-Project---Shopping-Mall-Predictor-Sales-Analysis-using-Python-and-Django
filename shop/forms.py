from django import forms
from .models import FileUpload

class FileUploadForm(forms.ModelForm):
    class Meta:
        model = FileUpload
        fields = ['file']

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            if not file.name.endswith('.csv'):
                raise forms.ValidationError('Only CSV files are allowed.')
        return file