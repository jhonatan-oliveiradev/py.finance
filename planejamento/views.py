from django.shortcuts import render
import calendar
import locale
from datetime import datetime
from perfil.models import Categoria
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json


def definir_planejamento(request):
    categorias = Categoria.objects.all()
    return render(request, "definir_planejamento.html", {"categorias": categorias})


@csrf_exempt
def update_valor_categoria(request, id):
    novo_valor = json.load(request)["novo_valor"]
    categoria = Categoria.objects.get(id=id)
    categoria.valor_planejamento = novo_valor
    categoria.save()

    return JsonResponse({"status": "Sucesso"})


def ver_planejamento(request):
    categorias = Categoria.objects.all()

    # Definir localização para pt-BR
    locale.setlocale(locale.LC_TIME, "pt_BR.utf8")

    mes_referente = calendar.month_name[datetime.now().month].capitalize()

    total_gastos = 0
    total_planejamento = 0

    for categoria in categorias:
        total_gastos += categoria.total_gasto()
        total_planejamento += categoria.valor_planejamento

    total_gastos = int(total_gastos)
    total_planejamento = int(total_planejamento)
    total_gastos_percentage = (
        int((total_gastos * 100) / total_planejamento) if total_planejamento else 0
    )

    return render(
        request,
        "ver_planejamento.html",
        {
            "categorias": categorias,
            "mes_referente": mes_referente,
            "total_gastos": total_gastos,
            "total_planejamento": total_planejamento,
            "total_gastos_percentage": total_gastos_percentage,
        },
    )
