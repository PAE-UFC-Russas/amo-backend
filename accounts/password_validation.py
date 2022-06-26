from django.core.exceptions import ValidationError
import re


class NumberValidator:
    def validate(self, password, user=None):
        if not re.findall("\d", password):
            raise ValidationError("Password deve conter pelo menos um número")

    def get_help_text(self):
        return "Senha deve conter pelo menos um número."


class LetterValidator:
    def validate(self, password, user=None):
        if not re.findall("[a-zA-Z]", password):
            raise ValidationError("Password deve conter pelo menos uma letra")

    def get_help_text(self):
        return "Senha deve conter pelo menos uma letra."
