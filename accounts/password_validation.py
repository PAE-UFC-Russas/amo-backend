"""Este módulo contém validadores de senha."""
import re

from django.core.exceptions import ValidationError


class NumberValidator:
    """Validador para verificar que senha tem pelo menos um número."""

    @staticmethod
    def validate(password, user=None):  # pylint: disable=W0613,C0116
        if not re.findall(r"\d", password):
            raise ValidationError("Password deve conter pelo menos um número")

    @staticmethod
    def get_help_text():
        """Retorna texto de ajuda usado na gui."""
        return "Senha deve conter pelo menos um número."


class LetterValidator:
    """Validador para verificar que senha tem pelo menos uma letra."""

    @staticmethod
    def validate(password, user=None):  # pylint: disable=W0613,C0116
        if not re.findall("[a-zA-Z]", password):
            raise ValidationError("Password deve conter pelo menos uma letra")

    @staticmethod
    def get_help_text():
        """Retorna texto de ajuda usado na gui."""
        return "Senha deve conter pelo menos uma letra."
