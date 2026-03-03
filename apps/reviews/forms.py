from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rhymes', 'structure', 'style', 'charisma', 'atmosphere', 'text']
        widgets = {
            'rhymes': forms.RangeInput(attrs={
                'min': 1, 'max': 10, 'value': 5,
                'class': 'criteria-slider',
                'data-criteria': 'rhymes'
            }),
            'structure': forms.RangeInput(attrs={
                'min': 1, 'max': 10, 'value': 5,
                'class': 'criteria-slider',
                'data-criteria': 'structure'
            }),
            'style': forms.RangeInput(attrs={
                'min': 1, 'max': 10, 'value': 5,
                'class': 'criteria-slider',
                'data-criteria': 'style'
            }),
            'charisma': forms.RangeInput(attrs={
                'min': 1, 'max': 10, 'value': 5,
                'class': 'criteria-slider',
                'data-criteria': 'charisma'
            }),
            'atmosphere': forms.RangeInput(attrs={
                'min': 1, 'max': 5, 'value': 3,
                'class': 'criteria-slider atmosphere-slider',
                'data-criteria': 'atmosphere'
            }),
            'text': forms.Textarea(attrs={
                'rows': 6,
                'placeholder': 'Напишите вашу рецензию (минимум 100 символов)...',
                'class': 'review-textarea',
                'minlength': 100,
            }),
        }
        labels = {
            'rhymes': 'Рифмы',
            'structure': 'Структура',
            'style': 'Стиль',
            'charisma': 'Харизма',
            'atmosphere': 'Атмосфера',
            'text': 'Текст рецензии',
        }

    def clean_text(self):
        text = self.cleaned_data.get('text', '')
        if len(text) < 100:
            raise forms.ValidationError('Текст рецензии должен содержать минимум 100 символов.')
        return text
