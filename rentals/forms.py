from django import forms
from django.utils import timezone
from .models import RentalItem, Booking

BOOTSTRAP  = 'form-control'
BS_SELECT  = 'form-select'


class RentalItemForm(forms.ModelForm):
    class Meta:
        model  = RentalItem
        fields = ('title', 'description', 'price', 'photo')
        widgets = {
            'title': forms.TextInput(attrs={
                'class': BOOTSTRAP,
                'placeholder': 'Название объекта аренды',
            }),
            'description': forms.Textarea(attrs={
                'class': BOOTSTRAP,
                'rows': 4,
                'placeholder': 'Подробное описание...',
            }),
            'price': forms.NumberInput(attrs={
                'class': BOOTSTRAP,
                'placeholder': '0.00',
                'min': '0',
                'step': '0.01',
            }),
            'photo': forms.FileInput(attrs={'class': BOOTSTRAP}),
        }
        labels = {
            'title':       'Название',
            'description': 'Описание',
            'price':       'Цена (₸/сутки)',
            'photo':       'Фото',
        }

    def clean_title(self):
        title = self.cleaned_data.get('title', '').strip()
        if len(title) < 3:
            raise forms.ValidationError('Название должно содержать не менее 3 символов.')
        return title

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price <= 0:
            raise forms.ValidationError('Цена должна быть больше нуля.')
        return price

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if photo and hasattr(photo, 'size'):
            if photo.size > 5 * 1024 * 1024:
                raise forms.ValidationError('Размер фото не должен превышать 5 МБ.')
            allowed = ('image/jpeg', 'image/png', 'image/webp')
            if hasattr(photo, 'content_type') and photo.content_type not in allowed:
                raise forms.ValidationError('Допустимые форматы: JPEG, PNG, WEBP.')
        return photo


class BookingForm(forms.ModelForm):
    class Meta:
        model  = Booking
        fields = ('date_start', 'date_end')
        widgets = {
            'date_start': forms.DateInput(attrs={
                'class': BOOTSTRAP,
                'type':  'date',
            }),
            'date_end': forms.DateInput(attrs={
                'class': BOOTSTRAP,
                'type':  'date',
            }),
        }
        labels = {
            'date_start': 'Дата начала',
            'date_end':   'Дата окончания',
        }

    def clean_date_start(self):
        date_start = self.cleaned_data.get('date_start')
        if date_start and date_start < timezone.now().date():
            raise forms.ValidationError('Дата начала не может быть в прошлом.')
        return date_start

    def clean(self):
        cleaned_data = super().clean()
        date_start   = cleaned_data.get('date_start')
        date_end     = cleaned_data.get('date_end')

        if date_start and date_end:
            if date_end <= date_start:
                raise forms.ValidationError('Дата окончания должна быть позже даты начала.')
            days = (date_end - date_start).days
            if days > 365:
                raise forms.ValidationError('Максимальный срок аренды — 365 дней.')

        return cleaned_data