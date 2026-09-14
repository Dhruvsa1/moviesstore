from django import forms
from .models import ReviewReport


class ReviewReportForm(forms.ModelForm):
    class Meta:
        model = ReviewReport
        fields = ['reason', 'details']
        labels = {'details': 'Additional details (optional)'}
        widgets = {
            'reason': forms.Select(attrs={'class': 'form-select'}),
            'details': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'maxlength': 500}),
        }
