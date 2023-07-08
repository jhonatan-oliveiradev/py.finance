from django.shortcuts import render, redirect
from extrato.models import Valores
from datetime import datetime
from perfil.utils import calcula_equilibrio_financeiro, calcula_total
from .models import Categoria, Conta
from django.contrib import messages
from django.contrib.messages import constants
from django.db.models import Sum


from django.template.defaultfilters import floatformat


def home(request):
    valores = Valores.objects.filter(data__month=datetime.now().month)
    entradas = valores.filter(tipo="E")
    saidas = valores.filter(tipo="S")

    total_entradas = round(calcula_total(entradas, "valor"), 2)
    total_saidas = round(calcula_total(saidas, "valor"), 2)

    contas = Conta.objects.all()
    saldo_total = round(calcula_total(contas, "valor"), 2)

    (
        percentual_gastos_essenciais,
        percentual_gastos_nao_essenciais,
    ) = calcula_equilibrio_financeiro()

    for conta in contas:
        conta.valor = round(conta.valor, 2)

    saldo_livre = saldo_total - total_saidas

    return render(
        request,
        "home.html",
        {
            "contas": contas,
            "saldo_total": floatformat(saldo_total, 2),
            "total_entradas": total_entradas,
            "total_saidas": total_saidas,
            "percentual_gastos_essenciais": int(percentual_gastos_essenciais),
            "percentual_gastos_nao_essenciais": int(percentual_gastos_nao_essenciais),
            "saldo_livre": floatformat(saldo_livre, 2),
        },
    )


from datetime import date, timedelta


def gerenciar(request):
    contas = Conta.objects.all()
    categorias = Categoria.objects.all()
    saldo_total = round(calcula_total(contas, "valor"), 2)

    # Filtrar contas próximas do vencimento
    hoje = date.today()
    tres_dias_depois = hoje + timedelta(days=3)
    contas_proximas_vencimento = contas.filter(
        data_vencimento__gte=hoje, data_vencimento__lte=tres_dias_depois
    ).count()

    # Filtrar contas vencidas
    contas_vencidas = contas.filter(data_vencimento__lt=hoje).count()

    return render(
        request,
        "gerenciar.html",
        {
            "contas": contas,
            "total_contas": saldo_total,
            "categorias": categorias,
            "contas_proximas_vencimento": contas_proximas_vencimento,
            "contas_vencidas": contas_vencidas,
        },
    )


def cadastrar_banco(request):
    apelido = request.POST.get("apelido")
    banco = request.POST.get("banco")
    tipo = request.POST.get("tipo")
    valor = request.POST.get("valor")
    icone = request.FILES.get("icone")

    if len(apelido.strip()) == 0 or len(valor.strip()) == 0:
        messages.add_message(request, constants.ERROR, "Preencha todos os campos.")
        return redirect("/perfil/gerenciar/")

    conta = Conta(apelido=apelido, banco=banco, tipo=tipo, valor=valor, icone=icone)

    conta.save()

    messages.add_message(request, constants.SUCCESS, "Conta cadastrada com sucesso.")

    return redirect("/perfil/gerenciar/")


def deletar_banco(request, id):
    conta = Conta.objects.get(id=id)
    conta.delete()

    messages.add_message(request, constants.SUCCESS, "Conta removida com sucesso")
    return redirect("/perfil/gerenciar/")


def cadastrar_categoria(request):
    nome = request.POST.get("categoria")
    essencial = bool(request.POST.get("essencial"))

    categoria = Categoria(categoria=nome, essencial=essencial)

    categoria.save()

    messages.add_message(request, constants.SUCCESS, "Categoria cadastrada com sucesso")
    return redirect("/perfil/gerenciar/")


def update_categoria(request, id):
    categoria = Categoria.objects.get(id=id)

    categoria.essencial = not categoria.essencial

    categoria.save()

    return redirect("/perfil/gerenciar/")


def dashboard(request):
    categorias = Categoria.objects.all()
    dados = []

    for categoria in categorias:
        valor_total = Valores.objects.filter(categoria=categoria).aggregate(
            Sum("valor")
        )["valor__sum"]
        valor_total = round(valor_total, 2) if valor_total else 0.0
        dados.append(valor_total)

    return render(
        request,
        "dashboard.html",
        {"labels": [categoria.categoria for categoria in categorias], "values": dados},
    )
