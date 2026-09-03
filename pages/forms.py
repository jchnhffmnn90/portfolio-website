from django import forms

from pages.models import ContactMessage


class ContactForm(forms.ModelForm):
    # Honeypot field for bot detection
    honeypot = forms.CharField(
        required=False,
        widget=forms.HiddenInput(attrs={"tabindex": "-1", "autocomplete": "off"}),
    )

    class Meta:
        model = ContactMessage
        fields = ["name", "email", "subject", "message"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "placeholder": "Dein Name oder Firma",
                    "class": (
                        "w-full bg-gray-950 border border-gray-800 rounded-lg px-4 py-3 "
                        "text-sm text-gray-100 placeholder-gray-500 focus:outline-none "
                        "focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition"
                    ),
                    "required": "required",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "placeholder": "deine.email@beispiel.de",
                    "class": (
                        "w-full bg-gray-950 border border-gray-800 rounded-lg px-4 py-3 "
                        "text-sm text-gray-100 placeholder-gray-500 focus:outline-none "
                        "focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition"
                    ),
                    "required": "required",
                }
            ),
            "subject": forms.TextInput(
                attrs={
                    "placeholder": "Betreff oder Projektidee",
                    "class": (
                        "w-full bg-gray-950 border border-gray-800 rounded-lg px-4 py-3 "
                        "text-sm text-gray-100 placeholder-gray-500 focus:outline-none "
                        "focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition"
                    ),
                }
            ),
            "message": forms.Textarea(
                attrs={
                    "rows": 5,
                    "placeholder": "Erzähle kurz von deinem Vorhaben, deinen Fragen oder wie ich helfen kann...",
                    "class": (
                        "w-full bg-gray-950 border border-gray-800 rounded-lg px-4 py-3 "
                        "text-sm text-gray-100 placeholder-gray-500 focus:outline-none "
                        "focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition resize-none"
                    ),
                    "required": "required",
                }
            ),
        }

    def clean_honeypot(self) -> str:
        honeypot = self.cleaned_data.get("honeypot")
        if honeypot:
            raise forms.ValidationError("Spam detected.")
        return honeypot or ""
