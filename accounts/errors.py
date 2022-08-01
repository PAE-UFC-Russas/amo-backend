"""Este módulo define erros da aplicação."""


class EmailAddressAlreadyExistsError(Exception):
    """Representa um erro de cadastro quando um e-mail já foi utilizado."""

    message = "Já existe um cadastro utilizando este endereço de e-mail."
    http_error_code = 409
    internal_error_code = 409001
