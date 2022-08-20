"""Este módulo contém funções para tratamento de dados recebidos do usuário."""
import bleach


def strip_xss(text: str) -> str:
    """Limpa texto de atributos html para evitar ataques XSS."""
    allowed_attributes = []
    allowed_protocols = []
    allowed_tags = []

    return bleach.clean(
        text,
        attributes=allowed_attributes,
        protocols=allowed_protocols,
        tags=allowed_tags,
        strip=True,
        strip_comments=True,
    )
