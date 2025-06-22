from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import bleach

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Повтор пароля")

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean_password_confirm(self):
        pw = self.cleaned_data.get('password')
        pw2 = self.cleaned_data.get('password_confirm')
        if pw and pw2 and pw != pw2:
            raise ValidationError("Пароли не совпадают")
        return pw2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

class SearchForm(forms.Form):
    q = forms.CharField(required=True, max_length=100)
    page = forms.IntegerField(required=False, min_value=1)


ALLOWED_TAGS = [
    'b', 'i', 'u', 'strong', 'em', 'p', 'br', 'ul', 'ol', 'li', 'a'
]
ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'rel'],
}
ALLOWED_STYLES = []  # если не нужно inline-стилей
ALLOWED_PROTOCOLS = ['http', 'https', 'mailto']

def clean_user_html(text):
    #очистка текста от нежелательных тегов
    cleaned = bleach.clean(
        text,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        styles=ALLOWED_STYLES,
        protocols=ALLOWED_PROTOCOLS,
        strip=True  # удалить теги, не входящие в ALLOWED_TAGS
    )
    return cleaned


class CommentForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea)

    def clean_content(self):
        raw_content = self.cleaned_data['content']
        return self.sanitize_text(raw_content)

    @staticmethod
    def sanitize_text(text):
        """Очистка HTML-контента"""
        allowed_tags = ['b', 'i', 'u', 'strong', 'em', 'p', 'br']
        return bleach.clean(text, tags=allowed_tags, strip=True)


class FileUploadForm(forms.Form):
    file = forms.FileField(
        label="Выберите файл",
        help_text="Максимальный размер 5MB. Разрешены: JPEG, PNG"
    )

    def clean_file(self):
        uploaded_file = self.cleaned_data['file']

        # Проверка размера файла (5MB)
        if uploaded_file.size > 5 * 1024 * 1024:
            raise ValidationError("Слишком большой файл (>5MB)")

        # Проверка типа файла
        allowed_types = ['image/jpeg', 'image/png']
        if uploaded_file.content_type not in allowed_types:
            raise ValidationError("Только JPEG/PNG разрешены")

        # Проверка расширения файла (дополнительная безопасность)
        valid_extensions = ['.jpg', '.jpeg', '.png']
        if not any(uploaded_file.name.lower().endswith(ext) for ext in valid_extensions):
            raise ValidationError("Недопустимое расширение файла")

        return uploaded_file