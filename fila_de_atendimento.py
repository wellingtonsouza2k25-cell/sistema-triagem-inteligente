import customtkinter as ctk
from tkinter import messagebox
from database import (
    buscar_pacientes_fila,
    deletar_paciente_db,
    atualizar_status_paciente,
    gerar_codigo_atendimento,
)

from datetime import datetime
from zoneinfo import ZoneInfo


# ==========================
# CORES
# ==========================

COR_FUNDO = "#242424"
COR_CARD = "#2b2b2b"
COR_CARD_CLARO = "#303030"
COR_TEXTO = "#ffffff"
COR_TEXTO_SUAVE = "#b8bec9"

COR_ROSA = "#ef4f83"
COR_VERDE = "#00a878"
COR_AMARELO = "#f6b000"
COR_VERMELHO = "#ef3b6d"
COR_AZUL_ESCURO = "#0f172a"

COLUNAS_TABELA = [
    ("POSIÇÃO", 70),
    ("CÓD.", 70),
    ("PACIENTE / IDADE", 220),
    ("PRIORIDADE", 150),
    ("SINTOMAS / INFORMAÇÃO", 330),
    ("CHEGADA", 90),
    ("ESPERA", 90),
    ("STATUS", 150),
    ("AÇÃO", 90)
]

FUSO_BRASILIA = ZoneInfo("America/Sao_Paulo")


def formatar_horario_chegada(data_hora_chegada):
    if not data_hora_chegada:
        return "--:--"

    try:
        data = datetime.fromisoformat(data_hora_chegada)
        return data.strftime("%H:%M")
    except:
        return "--:--"


def calcular_tempo_espera(data_hora_chegada):
    if not data_hora_chegada:
        return "--"

    try:
        chegada = datetime.fromisoformat(data_hora_chegada)

        if chegada.tzinfo is None:
            chegada = chegada.replace(tzinfo=FUSO_BRASILIA)

        agora = datetime.now(FUSO_BRASILIA)

        diferenca = agora - chegada
        total_minutos = int(diferenca.total_seconds() // 60)

        if total_minutos < 0:
            total_minutos = 0

        if total_minutos < 60:
            return f"{total_minutos} min"

        horas = total_minutos // 60
        minutos = total_minutos % 60

        return f"{horas}h {minutos}min"

    except:
        return "--"


# ==========================
# DADOS DE EXEMPLO
# Depois vamos puxar do banco
# ==========================

def cor_por_prioridade(cor_prioridade, prioridade):
    if cor_prioridade == "Vermelho" or prioridade == "Emergência":
        return COR_VERMELHO

    if cor_prioridade == "Amarelo" or prioridade == "Urgente":
        return COR_AMARELO

    if cor_prioridade == "Verde" or prioridade == "Pouco Urgente":
        return COR_VERDE

    return COR_TEXTO_SUAVE


def ordem_prioridade(prioridade):
    if prioridade == "Emergência":
        return 1

    if prioridade == "Urgente":
        return 2

    if prioridade == "Pouco Urgente":
        return 3

    return 4


def carregar_pacientes_fila():
    pacientes_db = buscar_pacientes_fila()
    pacientes_fila = []

    for paciente in pacientes_db:
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
            data_hora_finalizacao
        ) = paciente

        codigo = gerar_codigo_atendimento(id_paciente, prioridade_ia)

        paciente_formatado = {
            "id": id_paciente,
            "codigo": codigo,
            "nome": nome,
            "idade": f"{idade} anos",
            "genero": genero,
            "prioridade": prioridade_ia or "Pouco Urgente",
            "cor": cor_por_prioridade(cor_prioridade, prioridade_ia),
            "sintomas": sintomas or "Não informado",
            "descricao": descricao_livre or justificativa_ia or "Sem descrição informada.",
            "chegada": formatar_horario_chegada(data_hora_chegada),
            "espera": calcular_tempo_espera(data_hora_chegada),
            "status": status or "AGUARDANDO"
        }

        pacientes_fila.append(paciente_formatado)

    pacientes_fila.sort(
        key=lambda p: (
            ordem_prioridade(p["prioridade"]),
            p["id"]
        )
    )

    return pacientes_fila

# ==========================
# FUNÇÕES VISUAIS
# ==========================

def criar_card_resumo(master, titulo, valor, descricao, cor_valor):
    card = ctk.CTkFrame(
        master,
        width=260,
        height=110,
        fg_color=COR_CARD,
        corner_radius=14,
        border_width=1,
        border_color="#444444"
    )
    card.pack(side="left", padx=(0, 15))
    card.pack_propagate(False)

    label_titulo = ctk.CTkLabel(
        card,
        text=titulo,
        font=("Arial", 11, "bold"),
        text_color=COR_TEXTO_SUAVE
    )
    label_titulo.pack(anchor="w", padx=18, pady=(15, 0))

    label_valor = ctk.CTkLabel(
        card,
        text=valor,
        font=("Arial", 24, "bold"),
        text_color=cor_valor
    )
    label_valor.pack(anchor="w", padx=18, pady=(5, 0))

    label_desc = ctk.CTkLabel(
        card,
        text=descricao,
        font=("Arial", 12),
        text_color=COR_TEXTO_SUAVE
    )
    label_desc.pack(anchor="w", padx=18, pady=(0, 10))


def criar_badge(master, texto, cor):
    badge = ctk.CTkLabel(
        master,
        text=texto,
        font=("Arial", 11, "bold"),
        text_color=cor,
        fg_color="#242424",
        corner_radius=8,
        padx=8,
        pady=3
    )
    return badge


def criar_linha_tabela(master, paciente, linha, ao_apagar=None, ao_atualizar=None):
    cor_linha = "#2a2a2a" if linha % 2 == 0 else "#262626"

    frame_linha = ctk.CTkFrame(
        master,
        width=1120,
        height=120,
        fg_color=cor_linha,
        corner_radius=0
    )

    frame_linha.grid(
        row=linha,
        column=0,
        sticky="ew"
    )

    frame_linha.grid_propagate(False)

    for indice, (texto_coluna, largura) in enumerate(COLUNAS_TABELA):
        frame_linha.grid_columnconfigure(indice, minsize=largura)

    # POSIÇÃO
    posicao = ctk.CTkLabel(
        frame_linha,
        text="—",
        width=COLUNAS_TABELA[0][1],
        font=("Arial", 13, "bold"),
        text_color=COR_TEXTO_SUAVE,
        anchor="center"
    )
    posicao.grid(row=0, column=0, sticky="nsew", padx=5, pady=15)

    # CÓDIGO
    codigo = ctk.CTkLabel(
        frame_linha,
        text=paciente["codigo"],
        width=COLUNAS_TABELA[1][1],
        font=("Consolas", 13, "bold"),
        text_color="#5b5bff",
        anchor="center"
    )
    codigo.grid(row=0, column=1, sticky="nsew", padx=5, pady=15)

    # PACIENTE / IDADE
    bloco_paciente = ctk.CTkFrame(
        frame_linha,
        fg_color="transparent",
        width=COLUNAS_TABELA[2][1],
        height=90
    )
    bloco_paciente.grid(row=0, column=2, sticky="nsew", padx=5, pady=15)
    bloco_paciente.pack_propagate(False)

    nome = ctk.CTkLabel(
        bloco_paciente,
        text=paciente["nome"],
        font=("Arial", 14, "bold"),
        text_color=COR_TEXTO,
        wraplength=190,
        justify="left"
    )
    nome.pack(anchor="w")

    info = ctk.CTkLabel(
        bloco_paciente,
        text=f'{paciente["idade"]} • {paciente["genero"]}',
        font=("Arial", 12),
        text_color=COR_TEXTO_SUAVE
    )
    info.pack(anchor="w", pady=(8, 0))

    # PRIORIDADE
    bloco_prioridade = ctk.CTkFrame(
        frame_linha,
        fg_color="transparent",
        width=COLUNAS_TABELA[3][1],
        height=90
    )
    bloco_prioridade.grid(row=0, column=3, sticky="nsew", padx=5, pady=15)
    bloco_prioridade.pack_propagate(False)

    badge_prioridade = ctk.CTkLabel(
        bloco_prioridade,
        text=paciente["prioridade"],
        font=("Arial", 11, "bold"),
        text_color=paciente["cor"],
        fg_color="#202020",
        corner_radius=8,
        padx=10,
        pady=4
    )
    badge_prioridade.pack(anchor="w", pady=(5, 0))

    # SINTOMAS / INFORMAÇÃO
    bloco_sintomas = ctk.CTkFrame(
        frame_linha,
        fg_color="transparent",
        width=COLUNAS_TABELA[4][1],
        height=90
    )
    bloco_sintomas.grid(row=0, column=4, sticky="nsew", padx=5, pady=15)
    bloco_sintomas.pack_propagate(False)

    sintomas = ctk.CTkLabel(
        bloco_sintomas,
        text=paciente["sintomas"],
        font=("Arial", 13, "bold"),
        text_color=COR_TEXTO,
        wraplength=300,
        justify="left"
    )
    sintomas.pack(anchor="w")

    descricao = ctk.CTkLabel(
        bloco_sintomas,
        text=paciente["descricao"],
        font=("Arial", 12, "italic"),
        text_color=COR_TEXTO_SUAVE,
        wraplength=300,
        justify="left"
    )
    descricao.pack(anchor="w", pady=(5, 0))

    # CHEGADA
    chegada = ctk.CTkLabel(
        frame_linha,
        text=paciente["chegada"],
        width=COLUNAS_TABELA[5][1],
        font=("Arial", 13),
        text_color=COR_TEXTO,
        anchor="center"
    )
    chegada.grid(row=0, column=5, sticky="nsew", padx=5, pady=15)

    # ESPERA
    espera = ctk.CTkLabel(
        frame_linha,
        text=paciente["espera"],
        width=COLUNAS_TABELA[6][1],
        font=("Arial", 13),
        text_color=COR_TEXTO,
        anchor="center"
    )
    espera.grid(row=0, column=6, sticky="nsew", padx=5, pady=15)

    # STATUS
    bloco_status = ctk.CTkFrame(
        frame_linha,
        fg_color="transparent",
        width=COLUNAS_TABELA[7][1],
        height=90
    )
    bloco_status.grid(row=0, column=7, sticky="nsew", padx=5, pady=15)
    bloco_status.pack_propagate(False)

    status = ctk.CTkLabel(
        bloco_status,
        text=paciente["status"],
        width=120,
        height=28,
        font=("Arial", 11, "bold"),
        text_color="#c084fc",
        fg_color="#42205f",
        corner_radius=8
    )
    status.pack(anchor="center", pady=(25, 0))

    # AÇÃO
    # AÇÃO
    bloco_acao = ctk.CTkFrame(
        frame_linha,
        fg_color="transparent",
        width=COLUNAS_TABELA[8][1],
        height=90
    )
    bloco_acao.grid(row=0, column=8, sticky="nsew", padx=5, pady=15)
    bloco_acao.pack_propagate(False)


    def finalizar_paciente():
        confirmar = messagebox.askyesno(
            "Confirmar finalização",
            f"Confirmar que o paciente foi atendido?\n\n{paciente['nome']}"
        )

        if confirmar:
            atualizar_status_paciente(
                paciente["id"],
                "FINALIZADO"
            )

            messagebox.showinfo(
                "Atendimento finalizado",
                "Paciente marcado como FINALIZADO."
            )

            if ao_atualizar:
                ao_atualizar()


    botao_finalizar = ctk.CTkButton(
        bloco_acao,
        text="Finalizar",
        width=80,
        height=30,
        corner_radius=8,
        fg_color="#15803d",
        hover_color="#166534",
        text_color="white",
        font=("Arial", 12, "bold"),
        command=finalizar_paciente
    )

    botao_finalizar.pack(anchor="center", pady=(25, 0))

# ==========================
# TELA PRINCIPAL DA FILA
# ==========================

def criar_tela_fila(master,painel_espera=None):
    def recarregar_fila():
        for widget in master.winfo_children():
            widget.destroy()

        criar_tela_fila(master, painel_espera)
        
    pacientes_fila = carregar_pacientes_fila()

    pacientes_ativos = []

    for paciente in pacientes_fila:
        if paciente["status"] != "FINALIZADO":
            pacientes_ativos.append(paciente)


    pacientes_finalizados = []

    for paciente in pacientes_fila:
        if paciente["status"] == "FINALIZADO":
            pacientes_finalizados.append(paciente)

    master.grid_columnconfigure(0, weight=1)

    container = ctk.CTkFrame(
        master,
        fg_color="transparent"
    )
    container.grid(row=0, column=0, sticky="n", padx=20, pady=20)

    # Topo
    topo = ctk.CTkFrame(
        container,
        width=1150,
        height=95,
        fg_color=COR_CARD,
        corner_radius=18
    )
    topo.grid(row=0, column=0, sticky="ew", pady=(0, 20))
    topo.pack_propagate(False)

    bloco_titulo = ctk.CTkFrame(topo, fg_color="transparent")
    bloco_titulo.pack(side="left", padx=25, pady=18)

    titulo = ctk.CTkLabel(
        bloco_titulo,
        text="Fila Eletrônica de Prioridades",
        font=("Arial", 22, "bold"),
        text_color=COR_TEXTO
    )
    titulo.pack(anchor="w")

    subtitulo = ctk.CTkLabel(
        bloco_titulo,
        text="Gerencie e chame pacientes organizados rigorosamente pela severidade clínica das queixas.",
        font=("Segoe UI Light", 15),
        text_color=COR_TEXTO_SUAVE
    )
    subtitulo.pack(anchor="w", pady=(5, 0))

    def chamar_proximo():
        pacientes_aguardando = []

        for paciente in pacientes_fila:
            if paciente["status"] == "AGUARDANDO":
                pacientes_aguardando.append(paciente)

        if len(pacientes_aguardando) == 0:
            messagebox.showinfo(
                "Fila vazia",
                "Não há pacientes aguardando para chamar."
            )
            return

        proximo = pacientes_aguardando[0]

        atualizar_status_paciente(
            proximo["id"],
            "EM ATENDIMENTO"
        )

        if painel_espera is not None:
            painel_espera.chamar_paciente(
                proximo,
                duracao=60
            )

        recarregar_fila()

    botao_chamar = ctk.CTkButton(
        topo,
        text="🔔  Chamar Próximo Paciente",
        width=240,
        height=48,
        corner_radius=12,
        fg_color=COR_ROSA,
        hover_color="#d93d70",
        text_color="white",
        font=("Arial", 15, "bold"),
        command=chamar_proximo
    )
    botao_chamar.pack(side="right", padx=25, pady=22)

    # Cards de resumo
    resumo = ctk.CTkFrame(container, fg_color="transparent")
    resumo.grid(row=1, column=0, sticky="w", pady=(10, 20))

    criar_card_resumo(
        resumo,
        "OCUPAÇÃO DA FILA",
        f"{len(pacientes_ativos)} ativos",
        "Aguardando atendimento médico.",
        COR_TEXTO
    )

    criar_card_resumo(
        resumo,
        "ATENDIDOS HOJE",
        f"{len(pacientes_finalizados)} pacientes",
        "Sessões concluídas com sucesso.",
        COR_VERDE
    )

    alerta = ctk.CTkFrame(
        resumo,
        width=330,
        height=110,
        fg_color="#302d20",
        border_width=1,
        border_color="#7a6415",
        corner_radius=14
    )
    alerta.pack(side="left")
    alerta.pack_propagate(False)

    alerta_titulo = ctk.CTkLabel(
        alerta,
        text="PAINEL DINÂMICO DE ALERTAS CLÍNICOS",
        font=("Arial", 11, "bold"),
        text_color="#f6b000"
    )
    alerta_titulo.pack(anchor="w", padx=18, pady=(18, 0))

    alerta_texto = ctk.CTkLabel(
        alerta,
        text="✓ Fila operando sob limites seguros.\nNenhum alerta crítico ativo.",
        font=("Arial", 12, "bold"),
        text_color="#22c55e",
        justify="left"
    )
    alerta_texto.pack(anchor="w", padx=18, pady=(10, 0))

    # Tabela
    tabela_card = ctk.CTkFrame(
        container,
        width=1150,
        fg_color=COR_CARD,
        corner_radius=18
    )
    tabela_card.grid(row=2, column=0, sticky="ew", pady=(10, 20))

    tabela_titulo = ctk.CTkFrame(tabela_card, fg_color="transparent")
    tabela_titulo.pack(fill="x", padx=25, pady=(20, 10))

    titulo_ordem = ctk.CTkLabel(
        tabela_titulo,
        text=f"ORDEM DE FILA UNIFICADA ({len(pacientes_ativos)} AGUARDANDO/ATENDIMENTO)",
        font=("Arial", 17, "bold"),
        text_color=COR_TEXTO
    )
    titulo_ordem.pack(side="left")

    tempo_real = ctk.CTkLabel(
        tabela_titulo,
        text="GERADO EM TEMPO REAL",
        font=("Consolas", 12, "bold"),
        text_color=COR_TEXTO_SUAVE
    )
    tempo_real.pack(side="right")

    linha_divisoria = ctk.CTkFrame(
        tabela_card,
        height=1,
        fg_color="#3a3a3a"
    )
    linha_divisoria.pack(fill="x", padx=25, pady=(0, 10))

    # Cabeçalho da tabela
    cabecalho = ctk.CTkFrame(tabela_card, fg_color="#2f2f2f")
    cabecalho.pack(fill="x", padx=25)

    colunas = [
        ("POSIÇÃO", 80),
        ("CÓD.", 80),
        ("PACIENTE / IDADE", 210),
        ("PRIORIDADE", 150),
        ("SINTOMAS / INFORMAÇÃO", 280),
        ("CHEGADA", 90),
        ("ESPERA", 90),
        ("STATUS", 130),
        ("AÇÃO", 170)
    ]

    for indice, (texto, largura) in enumerate(COLUNAS_TABELA):
        cabecalho.grid_columnconfigure(indice, minsize=largura)

        label = ctk.CTkLabel(
            cabecalho,
            text=texto,
            width=largura,
            font=("Arial", 12, "bold"),
            text_color=COR_TEXTO_SUAVE,
            anchor="w"
        )

        label.grid(
            row=0,
            column=indice,
            sticky="w",
            padx=5,
            pady=12
        )

    # Linhas da tabela
    corpo = ctk.CTkFrame(tabela_card, fg_color="transparent")
    corpo.pack(fill="x", padx=25, pady=(0, 25))

    corpo.grid_columnconfigure(0, weight=1)

    if len(pacientes_ativos) == 0:
        vazio = ctk.CTkLabel(
            corpo,
            text="Nenhum paciente cadastrado na fila.",
            font=("Arial", 16, "bold"),
            text_color=COR_TEXTO_SUAVE
        )
        vazio.pack(pady=30)
    else:
        for indice, paciente in enumerate(pacientes_ativos):
            criar_linha_tabela(
                corpo,
                paciente,
                indice,
                ao_apagar=recarregar_fila,
                ao_atualizar=recarregar_fila
            )