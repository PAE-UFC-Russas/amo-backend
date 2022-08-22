"""Este módulo define schemas para serialização."""
from marshmallow import Schema, fields, validate


class UserRegistration(Schema):
    """Schema para validação dos dados de cadastro do usuário."""

    email = fields.Email(required=True, load_only=True)
    password = fields.String(
        required=True,
        load_only=True,
        validate=[
            validate.Length(min=8, error="Senha deve ter pelo menos 8 caracteres."),
            validate.Regexp(
                regex=r".*\d+", error="Senha deve conter pelo menos um número."
            ),
            validate.Regexp(
                regex=r".*[a-zA-Z]", error="Senha deve conter pelo menos uma letra."
            ),
        ],
    )
