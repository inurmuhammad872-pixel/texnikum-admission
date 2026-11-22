import re
from datetime import date
from django import forms
from .models import Student, Direction


class ApplicationForm(forms.ModelForm):
    consent = forms.BooleanField(required=True, label='Maxfiylik shartlari bilan tanishdim va roziman')
    # Simple bot-trap; do not rely on this as the only spam control.
    website = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = Student
        fields = ['fio', 'jshshir', 'phone', 'email', 'birth_date', 'address', 'direction']
        labels = {
            'fio': 'F.I.Sh.', 'jshshir': 'JSHSHIR (14 raqam)',
            'phone': 'Telefon raqami', 'email': 'Email manzil',
            'birth_date': 'Tug\'ilgan sana', 'address': 'Yashash manzili',
            'direction': 'Ta\'lim yo\'nalishi',
        }
        widgets = {
            'fio': forms.TextInput(attrs={'autocomplete': 'name', 'placeholder': 'Familiya, ism, sharif'}),
            'jshshir': forms.TextInput(attrs={'inputmode': 'numeric', 'pattern': '[0-9]{14}', 'maxlength': '14', 'autocomplete': 'off', 'placeholder': '14 xonali JSHSHIR'}),
            'phone': forms.TextInput(attrs={'type': 'tel', 'autocomplete': 'tel', 'placeholder': '+998 90 123 45 67'}),
            'email': forms.EmailInput(attrs={'autocomplete': 'email', 'placeholder': 'example@mail.com'}),
            'birth_date': forms.DateInput(attrs={'type': 'date', 'autocomplete': 'bday'}),
            'address': forms.Textarea(attrs={'rows': '3', 'autocomplete': 'street-address', 'placeholder': 'Viloyat, tuman, ko\'cha va uy'}),
            'direction': forms.Select(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['direction'].queryset = Direction.objects.filter(is_active=True).order_by('name')
        self.fields['direction'].empty_label = 'Yo\'nalishni tanlang'

    def clean_jshshir(self):
        value = self.cleaned_data['jshshir'].strip()
        if not re.fullmatch(r'\d{14}', value):
            raise forms.ValidationError('JSHSHIR 14 ta raqamdan iborat bo\'lishi kerak.')
        return value

    def clean_phone(self):
        digits = re.sub(r'\D', '', self.cleaned_data['phone'])
        if len(digits) == 9:
            digits = '998' + digits
        if not (len(digits) == 12 and digits.startswith('998')):
            raise forms.ValidationError('Telefon raqamini +998 XX XXX XX XX shaklida kiriting.')
        return '+' + digits

    def clean_birth_date(self):
        value = self.cleaned_data['birth_date']
        if value >= date.today() or value.year < 1900:
            raise forms.ValidationError('Tug\'ilgan sanani tekshiring.')
        return value

    def clean(self):
        data = super().clean()
        if data.get('website'):
            raise forms.ValidationError('Arizani qayta tekshiring.')
        return data
