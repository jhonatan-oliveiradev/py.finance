import os
from io import BytesIO
from weasyprint import HTML
from django.conf import settings
from extrato.models import Valores
from django.contrib import messages
from datetime import datetime, timedelta
from perfil.models import Categoria, Conta
from django.shortcuts import render, redirect
from django.contrib.messages import constants
from django.template.loader import render_to_string
from django.http import FileResponse, HttpResponseRedirect


def novo_valor(request):
    if request.method == "GET":
        contas = Conta.objects.all()
        categorias = Categoria.objects.all()
        return render(
            request, "novo_valor.html", {"contas": contas, "categorias": categorias}
        )
    elif request.method == "POST":
        valor_str = request.POST.get("valor")
        valor = float(valor_str.replace(",", "."))  # Substitui vírgula por ponto
        categoria = request.POST.get("categoria")
        descricao = request.POST.get("descricao")
        data = request.POST.get("data")
        conta = request.POST.get("conta")
        tipo = request.POST.get("tipo")

        valores = Valores(
            valor=valor,
            categoria_id=categoria,
            descricao=descricao,
            data=data,
            conta_id=conta,
            tipo=tipo,
        )

        valores.save()

        conta = Conta.objects.get(id=conta)

        if tipo == "E":
            adicionar_mensagem_sucesso(request, "Entrada")
            conta.valor += valor
        else:
            adicionar_mensagem_sucesso(request, "Saída")
            conta.valor -= valor

        conta.save()

        return redirect("/extrato/novo_valor")


def adicionar_mensagem_sucesso(request, tipo):
    if tipo == "Entrada":
        mensagem = "Entrada cadastrada com sucesso."
    else:
        mensagem = "Saída cadastrada com sucesso."
    messages.add_message(request, constants.SUCCESS, mensagem)


def view_extrato(request):
    contas = Conta.objects.all()
    categorias = Categoria.objects.all()

    valores = Valores.objects.filter(data__month=datetime.now().month)

    conta_get = request.GET.get("conta")

    categoria_get = request.GET.get("categoria")

    if conta_get:
        valores = valores.filter(conta__id=conta_get)
    if categoria_get:
        valores = valores.filter(categoria__id=categoria_get)

    # Botão para zerar os filtros
    if "zerar_filtros" in request.GET:
        return HttpResponseRedirect("/extrato/view_extrato")

    # Filtrar por período
    periodo = request.GET.get("periodo")
    if periodo:
        try:
            periodo_int = int(periodo)
            data_inicial = datetime.now().date() - timedelta(days=periodo_int)
            valores = valores.filter(data__gte=data_inicial)
        except ValueError:
            pass

    return render(
        request,
        "view_extrato.html",
        {"valores": valores, "contas": contas, "categorias": categorias},
    )


def exportar_pdf(request):
    valores = Valores.objects.filter(data__month=datetime.now().month)
    contas = Conta.objects.all()
    categorias = Categoria.objects.all()

    path_template = os.path.join(settings.BASE_DIR, "templates/partials/extrato.html")
    path_output = BytesIO()

    template_render = render_to_string(
        path_template, {"valores": valores, "contas": contas, "categorias": categorias}
    )
    HTML(string=template_render).write_pdf(path_output)

    path_output.seek(0)

    return FileResponse(path_output, filename="extrato.pdf")
