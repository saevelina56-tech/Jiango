from django import forms
from .models import News

class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ['title', 'content', 'category', 'is_published']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 5}),
        }