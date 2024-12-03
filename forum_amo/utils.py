"""
Utilidades
"""
from django.core.mail import send_mail
from django.conf import settings


def send_report_mail(report):
    """Função para enviar e-mail de denúncia"""
    subject = f"Nova denúncia em {report.duvida.titulo}"
    message = f"""
    Nova denúncia recebida. 

    Razão: {report.reason}
    Comentário: {report.descricao}

    Dúvida: {report.duvida.titulo}
    Resposta: {report.resposta.resposta if report.resposta else "Apenas dúvida"}
    
    Autor: {report.autor}

    """

    send_mail(subject, message, settings.EMAIL_HOST_USER, [settings.EMAIL_HOST_USER])
