"""Este módulo define erros da aplicação."""



class EmailAddressAlreadyExistsError(Exception):
    """Representa um erro de cadastro quando um e-mail já foi utilizado."""

    message = "Já existe um cadastro utilizando este endereço de e-mail."
    http_error_code = 409
    internal_error_code = 409001


class EmailConfirmationCodeInactive(Exception):
    """O código de ativação de e-mail informado não existe ou expirou."""

    message = "Código de ativação não existe ou expirou."
    internal_error_code = 409002


class EmailConfirmationConflict(Exception):
    """Confirmação não pode ser realizada devido a conflito."""

    message = "Não foi possível processar a confirmação."
    internal_error_code = 4009003
