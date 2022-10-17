"""Este módulo contém filtros usados na views do aplicativo Core."""
from django_filters import rest_framework as filters

from core.models import Agendamento


class AgendamentoFilter(filters.FilterSet):
    """Filtros para view de agendamentos."""

    data = filters.DateFilter(lookup_expr="date", label="Data")
    data__gt = filters.DateFilter(
        lookup_expr="date__gt", field_name="data", label="Data é maior que"
    )
    data__lt = filters.DateFilter(
        lookup_expr="date__lt", field_name="data", label="Data é menor que"
    )

    class Meta:
        model = Agendamento
        fields = ["data", "data__gt", "data__lt", "disciplina", "status"]
