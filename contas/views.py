from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.messages import constants
from .models import ContaPaga, ContaPagar
from perfil.models import Categoria
from django.contrib import messages
from datetime import datetime


def definir_contas(request):
    if request.method == "GET":
        categorias = Categoria.objects.all()
        return render(request, "definir_contas.html", {"categorias": categorias})
    else:
        titulo = request.POST.get("titulo")
        categoria = request.POST.get("categoria")
        descricao = request.POST.get("descricao")
        valor = request.POST.get("valor")
        dia_pagamento = request.POST.get("dia_pagamento")

        conta = ContaPagar(
            titulo=titulo,
            categoria_id=categoria,
            descricao=descricao,
            valor=valor,
            dia_pagamento=dia_pagamento,
        )

        conta.save()

        messages.add_message(request, constants.SUCCESS, "Conta cadastrada com sucesso")
        return redirect("/contas/definir_contas")


def ver_contas(request):
    import locale

    MES_ATUAL = datetime.now().month
    DIA_ATUAL = datetime.now().day

    contas = ContaPagar.objects.all()

    contas_pagas = ContaPaga.objects.filter(data_pagamento__month=MES_ATUAL).values(
        "conta"
    )

    contas_vencidas = contas.filter(dia_pagamento__lt=DIA_ATUAL).exclude(
        id__in=contas_pagas
    )

    contas_proximas_vencimento = (
        contas.filter(dia_pagamento__lte=DIA_ATUAL + 5)
        .filter(dia_pagamento__gte=DIA_ATUAL)
        .exclude(id__in=contas_pagas)
    )

    restantes = (
        contas.exclude(id__in=contas_vencidas)
        .exclude(id__in=contas_pagas)
        .exclude(id__in=contas_proximas_vencimento)
    )

    locale.setlocale(locale.LC_TIME, "pt_BR.UTF-8")
    nome_mes_atual = datetime.now().strftime("%B")

    total_contas_pagas = ContaPaga.objects.filter(
        data_pagamento__month=MES_ATUAL
    ).count()

    relatorio = {
        "contas_vencidas_relatorio": len(contas_vencidas) if contas_vencidas else 0,
        "contas_proximas_vencimento_relatorio": len(contas_proximas_vencimento)
        if contas_proximas_vencimento
        else 0,
        "restantes_relatorio": len(restantes) if restantes else 0,
        "total_contas_mes_relatorio": total_contas_pagas,
    }

    return render(
        request,
        "ver_contas.html",
        {
            "contas_vencidas": contas_vencidas,
            "contas_proximas_vencimento": contas_proximas_vencimento,
            "restantes": restantes,
            "relatorio": relatorio,
            "nome_mes_atual": nome_mes_atual,
        },
    )


def pagar_conta(request, conta_id):
    conta = get_object_or_404(ContaPagar, id=conta_id)

    if request.method == "POST":
        # Atualizar o status da conta para "Paga"
        conta.status = "Paga"
        conta.save()
        # Redirecionar para a página de visualização de contas
        return redirect("ver_contas")

    return render(request, "pagar_conta.html", {"conta": conta})
