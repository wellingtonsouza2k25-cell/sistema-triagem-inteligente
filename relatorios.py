import csv
import tkinter as tk
from collections import Counter
from datetime import datetime
from tkinter import filedialog, messagebox
from zoneinfo import ZoneInfo

import customtkinter as ctk

from database import buscar_pacientes_fila


# ==========================
# PALETA ESCURA DO SISTEMA
# ==========================
COR_FUNDO = "#242424"
COR_CARD = "#2b2b2b"
COR_CARD_CLARO = "#303030"
COR_BORDA = "#3a3a3a"

COR_TEXTO = "#ffffff"
COR_TEXTO_SUAVE = "#b8bec9"
COR_TEXTO_APAGADO = "#94a3b8"

COR_AZUL = "#5b5bff"
COR_ROSA = "#ef4f83"
COR_VERDE = "#00c48c"
COR_AMARELO = "#f6b000"
COR_VERMELHO = "#ef3b6d"
COR_LARANJA = "#ff8a00"
COR_BOTAO = "#0f172a"

FUSO_BRASILIA = ZoneInfo("America/Sao_Paulo")

PRIORIDADES = ("Emergência", "Urgente", "Pouco Urgente")
METAS_ESPERA = {
    "Emergência": 0,
    "Urgente": 10,
    "Pouco Urgente": 60,
}


# ==========================
# TRATAMENTO DOS DADOS
# ==========================
def converter_data_iso(data_iso):
    """Converte uma data ISO do banco para o fuso de Brasília."""
    if not data_iso:
        return None

    try:
        data = datetime.fromisoformat(data_iso)
        if data.tzinfo is None:
            data = data.replace(tzinfo=FUSO_BRASILIA)
        return data.astimezone(FUSO_BRASILIA)
    except (TypeError, ValueError):
        return None


def normalizar_prioridade(prioridade):
    texto = (prioridade or "").strip().lower()

    if texto in {"emergência", "emergencia"}:
        return "Emergência"
    if texto in {"urgente", "urgência", "urgencia"}:
        return "Urgente"
    if texto in {"pouco urgente", "pouco_urgente"}:
        return "Pouco Urgente"

    return "Pouco Urgente"


def normalizar_status(status):
    texto = (status or "AGUARDANDO").strip().upper()
    if texto in {"AGUARDANDO", "EM ATENDIMENTO", "FINALIZADO"}:
        return texto
    return "AGUARDANDO"


def transformar_registros(pacientes_db):
    """Transforma as tuplas retornadas pelo banco em dicionários legíveis."""
    registros = []

    for paciente in pacientes_db:
        if len(paciente) < 16:
            continue

        (
            id_paciente,
            nome,
            idade,
            genero,
            documento,
            telefone,
            sintomas,
            descricao_livre,
            sinais_fisicos,
            observacoes,
            prioridade_ia,
            cor_prioridade,
            justificativa_ia,
            data_hora_chegada,
            status,
            data_hora_finalizacao,
        ) = paciente[:16]

        registros.append({
            "id": id_paciente,
            "nome": nome or "",
            "idade": idade or "",
            "genero": genero or "",
            "documento": documento or "",
            "telefone": telefone or "",
            "sintomas": sintomas or "",
            "descricao_livre": descricao_livre or "",
            "sinais_fisicos": sinais_fisicos or "",
            "observacoes": observacoes or "",
            "prioridade": normalizar_prioridade(prioridade_ia),
            "cor_prioridade": cor_prioridade or "",
            "justificativa": justificativa_ia or "",
            "data_chegada_texto": data_hora_chegada or "",
            "data_finalizacao_texto": data_hora_finalizacao or "",
            "data_chegada": converter_data_iso(data_hora_chegada),
            "data_finalizacao": converter_data_iso(data_hora_finalizacao),
            "status": normalizar_status(status),
        })

    return registros


def calcular_espera_minutos(registro, agora=None):
    chegada = registro.get("data_chegada")
    if chegada is None:
        return None

    if agora is None:
        agora = datetime.now(FUSO_BRASILIA)

    finalizacao = registro.get("data_finalizacao")
    status = registro.get("status")

    if status == "FINALIZADO" and finalizacao is not None:
        fim = finalizacao
    else:
        fim = agora

    minutos = int((fim - chegada).total_seconds() // 60)
    return max(minutos, 0)


def formatar_minutos(minutos):
    if minutos is None:
        return "—"

    minutos = int(round(minutos))
    if minutos < 60:
        return f"{minutos} min"

    horas, resto = divmod(minutos, 60)
    return f"{horas}h {resto:02d}min"


def separar_sintomas(texto):
    if not texto:
        return []

    texto = texto.replace(";", ",").replace("\n", ",")
    return [item.strip() for item in texto.split(",") if item.strip()]


def calcular_estatisticas(registros):
    agora = datetime.now(FUSO_BRASILIA)
    hoje = agora.date()

    registros_hoje = [
        registro
        for registro in registros
        if registro["data_chegada"] is not None
        and registro["data_chegada"].date() == hoje
    ]

    finalizados_hoje = [
        registro
        for registro in registros
        if registro["status"] == "FINALIZADO"
        and registro["data_finalizacao"] is not None
        and registro["data_finalizacao"].date() == hoje
    ]

    por_prioridade = Counter(
        registro["prioridade"] for registro in registros_hoje
    )

    por_status = Counter(
        registro["status"] for registro in registros_hoje
    )

    esperas = [
        espera
        for registro in registros_hoje
        if (espera := calcular_espera_minutos(registro, agora)) is not None
    ]
    media_geral = sum(esperas) / len(esperas) if esperas else None

    fluxo_horario = Counter()
    for registro in registros_hoje:
        fluxo_horario[registro["data_chegada"].hour] += 1

    sintomas = Counter()
    for registro in registros_hoje:
        sintomas.update(separar_sintomas(registro["sintomas"]))

    medias_prioridade = {}
    for prioridade in PRIORIDADES:
        esperas_prioridade = [
            espera
            for registro in registros_hoje
            if registro["prioridade"] == prioridade
            and (espera := calcular_espera_minutos(registro, agora)) is not None
        ]
        medias_prioridade[prioridade] = (
            sum(esperas_prioridade) / len(esperas_prioridade)
            if esperas_prioridade
            else None
        )

    ativos = sum(
        quantidade
        for status, quantidade in por_status.items()
        if status != "FINALIZADO"
    )

    return {
        "total_acumulado": len(registros),
        "registros_hoje": len(registros_hoje),
        "atendidos_hoje": len(finalizados_hoje),
        "emergencias_hoje": por_prioridade["Emergência"],
        "urgentes_hoje": por_prioridade["Urgente"],
        "pouco_urgentes_hoje": por_prioridade["Pouco Urgente"],
        "ativos_hoje": ativos,
        "media_geral": media_geral,
        "fluxo_horario": fluxo_horario,
        "sintomas": sintomas,
        "medias_prioridade": medias_prioridade,
        "por_status": por_status,
        "por_prioridade": por_prioridade,
        "registros_hoje_lista": registros_hoje,
    }


# ==========================
# EXPORTAÇÃO
# ==========================
def exportar_csv(registros):
    if not registros:
        messagebox.showwarning(
            "Sem dados",
            "Ainda não existem pacientes cadastrados para exportar.",
        )
        return

    nome_padrao = f"atendimentos_{datetime.now(FUSO_BRASILIA):%Y-%m-%d}.csv"
    caminho = filedialog.asksaveasfilename(
        title="Salvar relatório de atendimentos",
        defaultextension=".csv",
        initialfile=nome_padrao,
        filetypes=[("Arquivo CSV", "*.csv")],
    )

    if not caminho:
        return

    campos = [
        "ID",
        "Nome",
        "Idade",
        "Gênero",
        "Documento",
        "Telefone",
        "Sintomas",
        "Descrição livre",
        "Sinais físicos",
        "Observações",
        "Prioridade",
        "Cor",
        "Justificativa da IA",
        "Data/hora de chegada",
        "Status",
        "Data/hora de finalização",
        "Tempo de espera (minutos)",
    ]

    try:
        with open(caminho, "w", newline="", encoding="utf-8-sig") as arquivo:
            escritor = csv.writer(arquivo, delimiter=";")
            escritor.writerow(campos)

            for registro in registros:
                escritor.writerow([
                    registro["id"],
                    registro["nome"],
                    registro["idade"],
                    registro["genero"],
                    registro["documento"],
                    registro["telefone"],
                    registro["sintomas"],
                    registro["descricao_livre"],
                    registro["sinais_fisicos"],
                    registro["observacoes"],
                    registro["prioridade"],
                    registro["cor_prioridade"],
                    registro["justificativa"],
                    registro["data_chegada_texto"],
                    registro["status"],
                    registro["data_finalizacao_texto"],
                    calcular_espera_minutos(registro),
                ])

        messagebox.showinfo(
            "Exportação concluída",
            f"Os dados foram exportados com sucesso para:\n{caminho}",
        )
    except OSError as erro:
        messagebox.showerror(
            "Erro ao exportar",
            f"Não foi possível salvar o arquivo.\n\n{erro}",
        )


# ==========================
# FUNÇÕES VISUAIS
# ==========================
def criar_card_metrica(master, titulo, valor, subtitulo, cor_valor):
    card = ctk.CTkFrame(
        master,
        width=180,
        height=95,
        fg_color=COR_CARD,
        border_width=1,
        border_color=COR_BORDA,
        corner_radius=14,
    )
    card.pack_propagate(False)

    ctk.CTkLabel(
        card,
        text=titulo.upper(),
        font=("Arial", 11, "bold"),
        text_color=COR_TEXTO_APAGADO,
    ).pack(anchor="w", padx=16, pady=(12, 2))

    ctk.CTkLabel(
        card,
        text=str(valor),
        font=("Arial", 18, "bold"),
        text_color=cor_valor,
    ).pack(anchor="w", padx=16)

    ctk.CTkLabel(
        card,
        text=subtitulo,
        font=("Arial", 11),
        text_color=COR_TEXTO_SUAVE,
    ).pack(anchor="w", padx=16, pady=(2, 0))

    return card


def criar_card_grande(master, titulo, subtitulo, sizaFont=15, largura=540, altura=260):
    card = ctk.CTkFrame(
        master,
        width=largura,
        height=altura,
        fg_color=COR_CARD,
        border_width=1,
        border_color=COR_BORDA,
        corner_radius=18,
    )
    card.pack_propagate(False)

    ctk.CTkLabel(
        card,
        text=titulo,
        font=("Arial", sizaFont, "bold"),
        text_color=COR_TEXTO,
    ).pack(anchor="w", padx=20, pady=(18, 4))

    ctk.CTkLabel(
        card,
        text=subtitulo,
        font=("Arial", 12),
        text_color=COR_TEXTO_SUAVE,
        wraplength=largura - 50,
        justify="left",
    ).pack(anchor="w", padx=20, pady=(0, 10))

    return card


def criar_linha_resumo(master, nome, quantidade, descricao):
    linha = ctk.CTkFrame(
        master,
        fg_color=COR_CARD_CLARO,
        border_width=1,
        border_color=COR_BORDA,
        corner_radius=12,
        height=42,
    )
    linha.pack(fill="x", pady=6, padx=18)
    linha.pack_propagate(False)

    ctk.CTkLabel(
        linha,
        text=nome,
        font=("Arial", 13, "bold"),
        text_color=COR_TEXTO,
    ).pack(side="left", padx=12)

    sufixo = "registro" if quantidade == 1 else "registros"
    ctk.CTkLabel(
        linha,
        text=f"{quantidade} {descricao or sufixo}",
        font=("Consolas", 11, "bold"),
        text_color=COR_AZUL,
        fg_color="#1f2535",
        corner_radius=8,
        padx=10,
        pady=4,
    ).pack(side="right", padx=12)


def criar_item_sintoma(master, nome, ocorrencias, maior_ocorrencia):
    linha = ctk.CTkFrame(master, fg_color="transparent")
    linha.pack(fill="x", padx=20, pady=(3, 0))

    ctk.CTkLabel(
        linha,
        text=nome,
        font=("Arial", 12, "bold"),
        text_color=COR_TEXTO,
        width=135,
        anchor="w",
    ).pack(side="left")

    ctk.CTkLabel(
        linha,
        text=str(ocorrencias),
        font=("Consolas", 12, "bold"),
        text_color=COR_TEXTO,
    ).pack(side="right")

    barra = ctk.CTkProgressBar(
        master,
        width=230,
        height=7,
        progress_color="#dfe5ee",
        fg_color="#3a3a3a",
    )
    barra.pack(anchor="w", padx=20, pady=(0, 3))
    barra.set(ocorrencias / maior_ocorrencia if maior_ocorrencia else 0)


def criar_item_categoria(
    master,
    nome,
    meta,
    tempo,
    status,
    cor_bolinha,
    cor_tempo,
    cor_status,
):
    linha = ctk.CTkFrame(master, fg_color="transparent")
    linha.pack(fill="x", padx=20, pady=12)

    bloco_esq = ctk.CTkFrame(linha, fg_color="transparent")
    bloco_esq.pack(side="left", fill="x", expand=True)

    topo = ctk.CTkFrame(bloco_esq, fg_color="transparent")
    topo.pack(anchor="w")

    ctk.CTkLabel(
        topo,
        text="●",
        font=("Arial", 14),
        text_color=cor_bolinha,
    ).pack(side="left", padx=(0, 6))

    ctk.CTkLabel(
        topo,
        text=nome,
        font=("Arial", 13, "bold"),
        text_color=COR_TEXTO,
    ).pack(side="left")

    ctk.CTkLabel(
        bloco_esq,
        text=meta,
        font=("Arial", 10),
        text_color=COR_TEXTO_SUAVE,
    ).pack(anchor="w", padx=(20, 0))

    bloco_dir = ctk.CTkFrame(linha, fg_color="transparent")
    bloco_dir.pack(side="right")

    ctk.CTkLabel(
        bloco_dir,
        text=tempo,
        font=("Consolas", 14, "bold"),
        text_color=cor_tempo,
    ).pack(anchor="e")

    ctk.CTkLabel(
        bloco_dir,
        text=status,
        font=("Arial", 9, "bold"),
        text_color=cor_status,
    ).pack(anchor="e")


def desenhar_grafico_fluxo(master, fluxo_horario):
    largura = 520
    altura = 185
    margem_esquerda = 34
    margem_direita = 12
    margem_superior = 15
    margem_inferior = 28

    canvas = tk.Canvas(
        master,
        width=largura,
        height=altura,
        bg="#262626",
        highlightthickness=0,
    )
    canvas.pack(fill="both", expand=True, padx=4, pady=4)

    valores = [fluxo_horario.get(hora, 0) for hora in range(24)]
    maior = max(valores, default=0)

    x_inicial = margem_esquerda
    x_final = largura - margem_direita
    y_base = altura - margem_inferior
    area_altura = y_base - margem_superior

    canvas.create_line(
        x_inicial,
        y_base,
        x_final,
        y_base,
        fill=COR_TEXTO_APAGADO,
        width=1,
    )

    for fracao in (0.25, 0.5, 0.75, 1.0):
        y = y_base - area_altura * fracao
        canvas.create_line(
            x_inicial,
            y,
            x_final,
            y,
            fill="#343434",
            width=1,
        )

    if maior == 0:
        canvas.create_text(
            largura / 2,
            altura / 2 - 5,
            text="Nenhum paciente registrado hoje",
            fill=COR_TEXTO_SUAVE,
            font=("Arial", 12, "italic"),
        )
    else:
        espaco = (x_final - x_inicial) / 24
        largura_barra = max(5, espaco * 0.62)

        for hora, valor in enumerate(valores):
            if valor == 0:
                continue

            altura_barra = (valor / maior) * area_altura
            centro_x = x_inicial + espaco * hora + espaco / 2
            x1 = centro_x - largura_barra / 2
            x2 = centro_x + largura_barra / 2
            y1 = y_base - altura_barra

            canvas.create_rectangle(
                x1,
                y1,
                x2,
                y_base,
                fill=COR_AZUL,
                outline="",
            )
            canvas.create_text(
                centro_x,
                y1 - 8,
                text=str(valor),
                fill=COR_TEXTO,
                font=("Arial", 9, "bold"),
            )

    for hora in range(0, 24, 4):
        espaco = (x_final - x_inicial) / 24
        x = x_inicial + espaco * hora + espaco / 2
        canvas.create_text(
            x,
            altura - 12,
            text=f"{hora}h",
            fill=COR_TEXTO_APAGADO,
            font=("Consolas", 9),
        )


def dados_categoria(prioridade, media):
    metas_texto = {
        "Emergência": "Meta: atendimento imediato",
        "Urgente": "Meta: máximo 10 minutos",
        "Pouco Urgente": "Meta: até 60 minutos",
    }
    cores = {
        "Emergência": COR_VERMELHO,
        "Urgente": COR_AMARELO,
        "Pouco Urgente": COR_VERDE,
    }

    if media is None:
        return (
            metas_texto[prioridade],
            "—",
            "SEM DADOS",
            cores[prioridade],
            COR_TEXTO_SUAVE,
            COR_TEXTO_APAGADO,
        )

    meta = METAS_ESPERA[prioridade]
    dentro_meta = media <= meta
    status = "DENTRO DA META" if dentro_meta else "FORA DA META"
    cor_status = COR_VERDE if dentro_meta else COR_VERMELHO
    cor_tempo = COR_VERDE if dentro_meta else "#ff8bb0"

    return (
        metas_texto[prioridade],
        formatar_minutos(media),
        status,
        cores[prioridade],
        cor_tempo,
        cor_status,
    )


# ==========================
# TELA RELATÓRIOS
# ==========================
def criar_tela_relatorios(master):
    pacientes_db = buscar_pacientes_fila()
    registros = transformar_registros(pacientes_db)
    estatisticas = calcular_estatisticas(registros)

    master.configure(fg_color=COR_FUNDO)
    master.grid_columnconfigure(0, weight=1)

    container = ctk.CTkFrame(master, fg_color="transparent")
    container.grid(row=0, column=0, sticky="n", padx=20, pady=20)

    def atualizar_relatorio():
        for widget in master.winfo_children():
            widget.destroy()
        criar_tela_relatorios(master)

    # TOPO
    topo = ctk.CTkFrame(
        container,
        width=1140,
        height=95,
        fg_color=COR_CARD,
        border_width=1,
        border_color=COR_BORDA,
        corner_radius=18,
    )
    topo.grid(row=0, column=0, sticky="ew", pady=(0, 20))
    topo.pack_propagate(False)

    bloco_titulo = ctk.CTkFrame(topo, fg_color="transparent")
    bloco_titulo.pack(side="left", padx=22, pady=18)

    ctk.CTkLabel(
        bloco_titulo,
        text="▥  Consolidação de Relatórios e Métricas",
        font=("Arial", 21, "bold"),
        text_color=COR_TEXTO,
    ).pack(anchor="w")

    ctk.CTkLabel(
        bloco_titulo,
        text="Dados calculados automaticamente com base nos pacientes cadastrados no sistema.",
        font=("Arial", 13),
        text_color=COR_TEXTO_SUAVE,
    ).pack(anchor="w", pady=(4, 0))

    botao_exportar = ctk.CTkButton(
        topo,
        text="⭳ Exportar atendimentos (.CSV)",
        width=235,
        height=40,
        fg_color=COR_BOTAO,
        hover_color="#1e293b",
        text_color="#ffffff",
        corner_radius=12,
        font=("Arial", 12, "bold"),
        command=lambda: exportar_csv(registros),
    )
    botao_exportar.pack(side="right", padx=(8, 22), pady=25)

    botao_atualizar = ctk.CTkButton(
        topo,
        text="↻ Atualizar",
        width=105,
        height=40,
        fg_color="#343a46",
        hover_color="#454d5c",
        text_color="#ffffff",
        corner_radius=12,
        font=("Arial", 12, "bold"),
        command=atualizar_relatorio,
    )
    botao_atualizar.pack(side="right", padx=(0, 0), pady=25)

    # MÉTRICAS
    linha_metricas = ctk.CTkFrame(container, fg_color="transparent")
    linha_metricas.grid(row=1, column=0, sticky="w", pady=(0, 20))

    criar_card_metrica(
        linha_metricas,
        "Registros hoje",
        estatisticas["registros_hoje"],
        f'{estatisticas["total_acumulado"]} no total',
        COR_TEXTO,
    ).pack(side="left", padx=(0, 12))

    criar_card_metrica(
        linha_metricas,
        "Atendidos hoje",
        estatisticas["atendidos_hoje"],
        "Sessões finalizadas",
        COR_VERDE,
    ).pack(side="left", padx=(0, 12))

    criar_card_metrica(
        linha_metricas,
        "Emergências",
        estatisticas["emergencias_hoje"],
        "Classificadas hoje",
        COR_VERMELHO,
    ).pack(side="left", padx=(0, 12))

    criar_card_metrica(
        linha_metricas,
        "Urgentes",
        estatisticas["urgentes_hoje"],
        "Classificadas hoje",
        COR_LARANJA,
    ).pack(side="left", padx=(0, 12))

    criar_card_metrica(
        linha_metricas,
        "Méd. espera geral",
        formatar_minutos(estatisticas["media_geral"]),
        "Registros de hoje",
        COR_TEXTO,
    ).pack(side="left", padx=(0, 12))

    criar_card_metrica(
        linha_metricas,
        "Em aberto",
        estatisticas["ativos_hoje"],
        "Aguardando/atendimento",
        COR_AZUL,
    ).pack(side="left")

    # LINHA SUPERIOR
    linha_superior = ctk.CTkFrame(container, fg_color="transparent")
    linha_superior.grid(row=2, column=0, sticky="w", pady=(0, 20))

    card_fluxo = criar_card_grande(
        linha_superior,
        "↗ DISTRIBUIÇÃO DE HORÁRIO DE MAIOR FLUXO",
        "Quantidade real de admissões registradas em cada hora do dia atual.",
        largura=560,
        altura=320,
    )
    card_fluxo.pack(side="left", padx=(0, 18))

    if estatisticas["fluxo_horario"]:
        hora_pico, quantidade_pico = max(
            estatisticas["fluxo_horario"].items(),
            key=lambda item: (item[1], -item[0]),
        )
        texto_pico = f"PICO: {hora_pico:02d}H ({quantidade_pico} PACT.)"
    else:
        texto_pico = "PICO: SEM DADOS"

    ctk.CTkLabel(
        card_fluxo,
        text=texto_pico,
        font=("Consolas", 10, "bold"),
        text_color="#8b7cf6",
        fg_color="#2f2c49",
        corner_radius=7,
        padx=8,
        pady=3,
    ).place(x=405, y=20)

    area_grafico = ctk.CTkFrame(
        card_fluxo,
        fg_color="#262626",
        border_width=1,
        border_color=COR_BORDA,
        corner_radius=12,
        width=520,
        height=195,
    )
    area_grafico.pack(padx=18, pady=(8, 8))
    area_grafico.pack_propagate(False)
    desenhar_grafico_fluxo(area_grafico, estatisticas["fluxo_horario"])

    card_sintomas = criar_card_grande(
        linha_superior,
        "SINTOMAS MAIS FREQUENTES",
        "Contagem dos sintomas informados nos registros de hoje.",
        largura=270,
        altura=320,
    )
    card_sintomas.pack(side="left", padx=(0, 18))

    sintomas_frequentes = estatisticas["sintomas"].most_common(5)
    if sintomas_frequentes:
        maior_ocorrencia = sintomas_frequentes[0][1]
        for nome, ocorrencias in sintomas_frequentes:
            criar_item_sintoma(
                card_sintomas,
                nome,
                ocorrencias,
                maior_ocorrencia,
            )
    else:
        ctk.CTkLabel(
            card_sintomas,
            text="Nenhum sintoma registrado hoje.",
            font=("Arial", 12, "italic"),
            text_color=COR_TEXTO_SUAVE,
            wraplength=220,
        ).pack(expand=True, padx=20, pady=20)

    card_media = criar_card_grande(
        linha_superior,
        "MÉDIA DE ESPERA POR CATEGORIA",
        "Tempo médio entre a chegada e a finalização ou o momento atual.",
        13,
        largura=290,
        altura=320,
    )
    card_media.pack(side="left")

    for prioridade in PRIORIDADES:
        meta, tempo, status, cor_bolinha, cor_tempo, cor_status = dados_categoria(
            prioridade,
            estatisticas["medias_prioridade"][prioridade],
        )
        criar_item_categoria(
            card_media,
            prioridade,
            meta,
            tempo,
            status,
            cor_bolinha,
            cor_tempo,
            cor_status,
        )

    # LINHA INFERIOR
    linha_inferior = ctk.CTkFrame(container, fg_color="transparent")
    linha_inferior.grid(row=3, column=0, sticky="w")

    card_status = criar_card_grande(
        linha_inferior,
        "STATUS DOS ATENDIMENTOS DE HOJE",
        "Distribuição real dos pacientes conforme o andamento na fila.",
        largura=560,
        altura=250,
    )
    card_status.pack(side="left", padx=(0, 18))

    criar_linha_resumo(
        card_status,
        "AGUARDANDO",
        estatisticas["por_status"]["AGUARDANDO"],
        "pacientes",
    )
    criar_linha_resumo(
        card_status,
        "EM ATENDIMENTO",
        estatisticas["por_status"]["EM ATENDIMENTO"],
        "pacientes",
    )
    criar_linha_resumo(
        card_status,
        "FINALIZADO",
        estatisticas["por_status"]["FINALIZADO"],
        "pacientes",
    )

    card_classificacoes = criar_card_grande(
        linha_inferior,
        "DISTRIBUIÇÃO DAS CLASSIFICAÇÕES DE HOJE",
        "Quantidade de pacientes em cada prioridade sugerida pela IA.",
        largura=560,
        altura=250,
    )
    card_classificacoes.pack(side="left")

    criar_linha_resumo(
        card_classificacoes,
        "EMERGÊNCIA",
        estatisticas["por_prioridade"]["Emergência"],
        "pacientes",
    )
    criar_linha_resumo(
        card_classificacoes,
        "URGENTE",
        estatisticas["por_prioridade"]["Urgente"],
        "pacientes",
    )
    criar_linha_resumo(
        card_classificacoes,
        "POUCO URGENTE",
        estatisticas["por_prioridade"]["Pouco Urgente"],
        "pacientes",
    )