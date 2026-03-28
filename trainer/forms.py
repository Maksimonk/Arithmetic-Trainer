from django import forms


class SettingsForm(forms.Form):
    nickname = forms.CharField(
        label="Никнейм",
        required=False,
        max_length=32,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Например, Дима"}),
    )
    allow_addition = forms.BooleanField(label="Сложение", required=False)
    allow_subtraction = forms.BooleanField(label="Вычитание", required=False)
    allow_multiplication = forms.BooleanField(label="Умножение", required=False)

    def clean(self) -> dict:
        cleaned = super().clean()
        if not (
            cleaned.get("allow_addition")
            or cleaned.get("allow_subtraction")
            or cleaned.get("allow_multiplication")
        ):
            raise forms.ValidationError("Выберите хотя бы один тип примеров.")
        return cleaned


class AnswerForm(forms.Form):
    left = forms.IntegerField(widget=forms.HiddenInput())
    right = forms.IntegerField(widget=forms.HiddenInput())
    operation = forms.CharField(widget=forms.HiddenInput())

    answer = forms.IntegerField(
        label="Ваш ответ",
        widget=forms.NumberInput(attrs={"class": "form-control", "autofocus": "autofocus"}),
        error_messages={"required": "Введите число."},
    )

    def clean_operation(self) -> str:
        op = (self.cleaned_data.get("operation") or "").strip()
        if op not in {"+", "-", "×"}:
            raise forms.ValidationError("Неизвестная операция.")
        return op
