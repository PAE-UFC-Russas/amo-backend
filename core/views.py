"""Conjunto de Views do aplicativo 'core'."""
from django_filters.rest_framework import DjangoFilterBackend
from rest_access_policy import AccessViewSetMixin
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from django.db import transaction
from django.db import IntegrityError
from django.contrib.auth.models import Group
from accounts.models import CustomUser
from core import access_policy, filters
from core.models import Agendamento, Curso, Disciplinas, Monitoria
from core.serializer import (
    AgendamentoRequestSerializer,
    AgendamentoSerializer,
    CursoSerializer,
    DisciplinaSerializer,
    MonitoriaSerializer,
)


class CursoViewSet(AccessViewSetMixin, ModelViewSet):  # pylint: disable=R0901
    """ViewSet para ações relacionadas a cursos."""

    access_policy = access_policy.CursoAccessPolicy
    serializer_class = CursoSerializer
    queryset = Curso.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ["nome"]


class DisciplinaViewSet(AccessViewSetMixin, ModelViewSet):  # pylint: disable=R0901
    """ViewSet para ações relacionadas a disciplinas."""

    # permission_classes = []
    access_policy = access_policy.DisciplinaAccessPolicy
    serializer_class = DisciplinaSerializer
    queryset = Disciplinas.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["cursos"]
    search_fields = ["nome"]

    @action(methods=["PATCH"], detail=False, url_path="adicionar-monitor")
    def adicionar_monitor(self, request):
        """Adicionar um monitor à uma disciplina.
        É passado o email do usuário e id da disciplina.
        """
        try:
            disciplina = Disciplinas.objects.get(id=request.data["disciplina"])
        except Disciplinas.DoesNotExist:
            return Response(
                {"erro": "Disciplina não encontrada."}, status=status.HTTP_404_NOT_FOUND
            )
        try:
            monitor = CustomUser.objects.get(email=request.data["email"]).id
        except CustomUser.DoesNotExist:
            return Response(
                {"erro": "Usuário com este email não encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Verifica se o monitor já está associado à disciplina
        if disciplina.monitores.filter(id=monitor).exists():
            return Response(
                {"mensagem": "Usuário já é monitor desta disciplina."},
                status=status.HTTP_200_OK,
            )

        CustomUser.objects.get(id=monitor).groups.add(Group.objects.get(name="monitor"))
        disciplina.monitores.add(monitor)
        return Response(
            {"mensagem": "Monitor adicionado com sucesso à disciplina."},
            status=status.HTTP_200_OK,
        )

    @action(methods=["PATCH"], detail=False, url_path="remover-monitor")
    def remover_monitor(self, request):
        """remover um monitor à uma disciplina.
        É passado o email do usuário e id da disciplina.
        """
        try:
            disciplina = Disciplinas.objects.get(id=request.data["disciplina"])
        except Disciplinas.DoesNotExist:
            return Response(
                {"erro": "Disciplina não encontrada."}, status=status.HTTP_404_NOT_FOUND
            )
        try:
            monitor = CustomUser.objects.get(email=request.data["email"]).id
        except CustomUser.DoesNotExist:
            return Response(
                {"erro": "Usuário com este email não encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Verifica se o monitor já está associado à disciplina
        if disciplina.monitores.filter(id=monitor).exists():
            # Remove o monitor da disciplina atual
            disciplina.monitores.remove(monitor)
            # Verifica se o usuário ainda é monitor em alguma outra disciplina
            ainda_monitor = Disciplinas.objects.filter(monitores__id=monitor).exists()
            if not ainda_monitor:
                # Remove o usuário do grupo monitor se não for mais monitor em nenhuma disciplina
                CustomUser.objects.get(id=monitor).groups.remove(
                    Group.objects.get(name="monitor")
                )

            return Response(
                {"mensagem": "Monitor removido com sucesso da disciplina."},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"mensagem": "Monitor não está acossiado com essa disciplina."},
            status=status.HTTP_200_OK,
        )


class AgendamentoViewSet(AccessViewSetMixin, ModelViewSet):
    """Ações do agendamento de atendimento."""

    access_policy = access_policy.AgendamentoAccessPolicy
    serializer_class = AgendamentoSerializer
    filterset_class = filters.AgendamentoFilter
    queryset = Agendamento.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["assunto", "descricao"]
    ordering = ["data"]
    ordering_fields = ["data"]

    def create(self, request, *args, **kwargs):
        disciplina = Disciplinas.objects.get(id=request.data["disciplina"])
        s_agen = None
        link = "Link é disponibilizado apenas para agendamentos remotos."
        if request.data["tipo"] == "virtual":
            link = "O link estará disponível após o monitor confirmar o agendamento."

        try:
            with transaction.atomic():
                agendamento = Agendamento.objects.create(
                    link_zoom=link,
                    tipo=request.data["tipo"],
                    data=request.data["data"],
                    assunto=request.data["assunto"],
                    descricao=request.data["descricao"],
                    disciplina=disciplina,
                    solicitante_id=request.user.id,
                )
                agendamento.save()
                s_agen = AgendamentoSerializer(agendamento)

        except IntegrityError:
            return Response(
                data={"mensagem": "já existe um agendamento pra essa data e horário"},
                status=status.HTTP_409_CONFLICT,
            )

        return Response(data=s_agen.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, pk=None):  # pylint: disable=W0221
        allowed_keys = ["tipo", "data", "assunto", "descricao", "disciplina", "status"]
        agendamento = Agendamento.objects.get(id=pk)
        if (
            request.data["status"]
            and request.data["status"] == "confirmado"
            and request.user not in agendamento.disciplina.monitores.all()
        ):
            return Response(
                data={
                    "mensagem": """Alunos e professores não podem
                    confirmar um agendamento com um monitor"""
                },
                status=401,
            )

        with transaction.atomic():
            for key, value in request.data.items():
                if key in allowed_keys:
                    setattr(agendamento, key, value)
            # agendamento.link_zoom = create_meeting()
            agendamento.save()
        return Response(data={"sucesso"}, status=200)

    def perform_create(self, serializer):
        """Salva o agendamento adicionando o usuário atual como solicitante."""
        serializer.save(solicitante=self.request.user)

    def get_request_serializer(self):
        """Altera o serializer nas requisições."""
        return AgendamentoRequestSerializer

    def get_queryset(self):
        """Passa o controle sobre a queryset para o módulo de controle de acesso."""
        return self.access_policy.scope_queryset(self.request, self.queryset)


class MonitoresHorarioViewSet(AccessViewSetMixin, ModelViewSet):
    """Ações do horário de monitoria."""

    access_policy = access_policy.MonitoriaAccessPolicy
    serializer_class = MonitoriaSerializer
    queryset = Monitoria.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["disciplina", "professor", "monitor", "dia_semana"]
    search_fields = ["local"]
    ordering = ["dia_semana", "hora_inicio"]
    ordering_fields = ["dia_semana", "hora_inicio"]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data, status=status.HTTP_201_CREATED, headers=headers
            )
        except IntegrityError:
            return Response(
                data={
                    "mensagem": (
                        "Já existe um horário para esse monitor nessa "
                        "disciplina, dia e hora"
                    )
                },
                status=status.HTTP_409_CONFLICT,
            )

    def perform_create(self, serializer):
        serializer.save()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def get_queryset(self):
        return self.access_policy.scope_queryset(self.request, self.queryset)
