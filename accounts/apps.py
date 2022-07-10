"""Configurações relacionadas ao aplicativo 'accounts'."""
from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """Configurações do aplicativo 'accounts'."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"

    def ready(self):
        import accounts.signals  # pylint: disable=unused-import, import-outside-toplevel
