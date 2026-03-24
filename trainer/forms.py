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
