import re

from django import forms
from django.core.exceptions import ValidationError

from dentist.models import ContactMessage


class ContactForm(forms.ModelForm):
    """Bog'lanish formasi"""

    class Meta:
        model = ContactMessage
        fields = ['name', 'phone', 'subject', 'message']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ismingiz'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+998XXXXXXXXX'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Xabar mavzusi'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 10, 'placeholder': 'Xabaringiz...'}),
        }

        labels = {
            'name': 'Ism',
            'phone': 'Telefon',
            'subject': 'Mavzu',
            'message': 'Xabar'
        }

        help_texts = {
            'phone': 'Telefon raqamingizni +998XXXXXXXXX formatida kiriting',
            'message': 'Kamida 13 ta belgi kiriting',
        }

    def clean_name(self):
        """Ism validatsiyasi"""
        name =self.cleaned_data.get('name')

        if not name:
            raise ValidationError("Ism majburiy maydon")

        name =' '.join(name.split())

        if len(name) < 3:
            raise ValidationError("Ism kamida 3 ta harfdan iborat bo'lishi kerak")
        if len(name) > 100:
            raise ValidationError("Ism juda uzun (maksimal 100 ta belgi)")

        return name

    def clean_subject(self):
        """Mavzu validatsiyasi"""
        subject = self.cleaned_data.get('subject')

        if not subject:
            raise ValidationError("Mavzu majburiy maydon")

        subject = ' '.join(subject.split())

        if len(subject) < 5:
            raise ValidationError("Mavzu kamida 5 ta harfdan iborat bo'lishi kerak")

        if len(subject) > 200:
            raise ValidationError("Mavzu juda uzun (maksimal 200 ta belgi)")

        return subject

    def clean_message(self):
        """Xabar validatsiyasi"""
        message = self.cleaned_data.get('message')

        if not message:
            raise ValidationError("Xabar majburiy maydon")

        message = message.strip()

        if len(message) < 10:
            raise ValidationError(
                f"Xabar juda qisqa. Kamida 10 ta belgi kiriting. "
                f"Hozir: {len(message)} ta belgi"
            )

        if len(message) > 5000:
            raise ValidationError(
                f"Xabar juda uzun (maksimal 5000 ta belgi). "
                f"Hozir: {len(message)} ta belgi"
            )

        return message

    def clean_phone(self):
        """Telefon raqami validatsiyasi"""
        phone = self.cleaned_data.get('phone')
        # forms.py oxirida validate_uzbek_phone bor, shundan foydalanamiz
        return validate_uzbek_phone(phone)



def validate_uzbek_phone(phone: str) -> str:
    """
    O'zbekiston telefon raqamini tekshirish.
    Returns: Formatlangan telefon (+998XXXXXXXXX) yoki ValidationError.
    """

    if not phone:
        raise ValidationError("Telefon raqam majburiy maydon")

    # Bo'sh joylar va maxsus belgilarni olib tashlash
    phone = re.sub(r'[\s\-\(\)]', '', phone)

    if phone.startswith('++'):
        phone = phone.lstrip('+')

    pattern = r'^(?:\+?998\d{9})$'
    if not re.match(pattern, phone):
        raise ValidationError(
            "Telefon raqam +998XXXXXXXXX formatida bo'lishi kerak. Masalan: +998901234567"
        )

    # + qo'shish agar yo'q bo'lsa
    if not phone.startswith('+'):
        phone = '+' + phone

    return phone