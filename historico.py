import customtkinter as ctk
from datetime import datetime

from database import buscar_pacientes_fila, gerar_codigo_atendimento


# ==========================
# CORES
# ==========================

COR_FUNDO = "#242424"
COR_HEADER = "#323232"
COR_CARD = "#2b2b2b"
COR_CARD_CLARO = "#303030"
COR_INPUT = "#242424"
COR_BORDA = "#444444"

COR_TEXTO = "#ffffff"
COR_TEXTO_SUAVE = "#b8bec9"
COR_TEXTO_APAGADO = "#94a3b8"

COR_AZUL = "#5b5bff"
COR_ROSA = "#ef4f83"
COR_VERDE = "#00a878"
COR_AMARELO = "#f6b000"
COR_VERMELHO = "#ef3b6d"
COR_ROXO = "#c084fc"
COR_ROXO_FUNDO = "#42205f"

LARGURA_CARD = 1130
LARGURA_TABELA = 1080

COLUNAS_HISTORICO = [
    ("CÓDIGO", 85),
    ("PACIENTE", 170),
    ("IDADE", 65),
    ("SINTOMAS / DESCRIÇÃO", 300),
    ("CHEGADA\n(DATA/HORA)", 120),
    ("PRIORIDADE", 130),
    ("TEMPO\nDE ESPERA", 95),
    ("STATUS FINAL", 115)
]


# ==========================
# FUNÇÕES AUXILIARES
# ==========================

def formatar_data_hora(data_iso):
    if not data_iso:
        return "--"

    try:
        data = datetime.fromisoformat(data_iso)
        return data.strftime("%d/%m/%Y\n%H:%M")
    except:
        return "--"


def calcular_tempo_espera(data_iso, status, data_finalizacao=None):
    if not data_iso:
        return "—"

    try:
        chegada = datetime.fromisoformat(data_iso)

        if status == "FINALIZADO" and data_finalizacao:
            fim = datetime.fromisoformat(data_finalizacao)
        else:
            fim = datetime.now(chegada.tzinfo) if chegada.tzinfo else datetime.now()

        diferenca = fim - chegada
        minutos = int(diferenca.total_seconds() // 60)

        if minutos < 0:
            minutos = 0

        if minutos < 60:
            return f"{minutos} min"

        horas = minutos // 60
        resto = minutos % 60

        return f"{horas}h {resto}min"

    except:
        return "—"


def cor_prioridade(prioridade):
    if prioridade == "Emergência":
        return COR_VERMELHO

    if prioridade == "Urgente":
        return COR_AMARELO

    if prioridade == "Pouco Urgente":
        return COR_VERDE

    return COR_TEXTO_SUAVE


def preparar_pacientes():
    pacientes_db = buscar_pacientes_fila()
    pacientes = []

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
            cor_prioridade_db,
            justificativa_ia,
            data_hora_chegada,
            status,
            data_hora_finalizacao
        ) = paciente

        prioridade = prioridade_ia or "Pouco Urgente"
        status_final = status or "AGUARDANDO"

        pacientes.append({
            "id": id_paciente,
            "codigo": gerar_codigo_atendimento(id_paciente, prioridade),
            "nome": nome or "",
            "idade": idade or "",
            "genero": genero or "",
            "documento": documento or "",
            "telefone": telefone or "",
            "sintomas": sintomas or "",
            "descricao": descricao_livre or "",
            "prioridade": prioridade,
            "status": status_final,
            "data_hora_chegada": data_hora_chegada,
            "chegada_formatada": formatar_data_hora(data_hora_chegada),
            "tempo_espera": calcular_tempo_espera(data_hora_chegada, status_final, data_hora_finalizacao),
            "justificativa": justificativa_ia or ""
        })

    return pacientes


# ==========================
# COMPONENTES VISUAIS
# ==========================

def criar_badge(master, texto, cor_texto, cor_fundo="#202020"):
    badge = ctk.CTkLabel(
        master,
        text=texto,
        font=("Arial", 10, "bold"),
        text_color=cor_texto,
        fg_color=cor_fundo,
        corner_radius=6,
        padx=8,
        pady=3
    )

    return badge


def criar_campo_filtro(master, titulo, placeholder, largura):
    bloco = ctk.CTkFrame(master, fg_color="transparent")

    label = ctk.CTkLabel(
        bloco,
        text=titulo,
        font=("Arial", 11, "bold"),
        text_color=COR_TEXTO_SUAVE
    )
    label.pack(anchor="w", pady=(0, 5))

    campo = ctk.CTkEntry(
        bloco,
        width=largura,
        height=36,
        corner_radius=12,
        border_width=1,
        border_color=COR_BORDA,
        fg_color=COR_INPUT,
        text_color=COR_TEXTO,
        placeholder_text=placeholder,
        font=("Arial", 13)
    )
    campo.pack(anchor="w")

    return bloco, campo


def criar_select_filtro(master, titulo, opcoes, largura):
    bloco = ctk.CTkFrame(master, fg_color="transparent")

    label = ctk.CTkLabel(
        bloco,
        text=titulo,
        font=("Arial", 11, "bold"),
        text_color=COR_TEXTO_SUAVE
    )
    label.pack(anchor="w", pady=(0, 5))

    campo = ctk.CTkComboBox(
        bloco,
        values=opcoes,
        width=largura,
        height=36,
        corner_radius=12,
        border_width=1,
        border_color=COR_BORDA,
        fg_color=COR_INPUT,
        button_color="#54595f",
        button_hover_color="#61676e",
        text_color=COR_TEXTO,
        dropdown_fg_color=COR_CARD,
        dropdown_text_color=COR_TEXTO,
        dropdown_hover_color=COR_CARD_CLARO,
        font=("Arial", 13)
    )
    campo.set(opcoes[0])
    campo.pack(anchor="w")

    return bloco, campo

def criar_linha_historico(master, paciente, linha):
    cor_linha = "#2a2a2a" if linha % 2 == 0 else "#262626"

    frame = ctk.CTkFrame(
        master,
        width=LARGURA_TABELA,
        height=125,
        fg_color=cor_linha,
        corner_radius=0
    )
    frame.grid(
        row=linha,
        column=0,
        sticky="ew"
    )
    frame.grid_propagate(False)
    frame.grid_rowconfigure(0, weight=1)

    for indice, (_, largura) in enumerate(COLUNAS_HISTORICO):
        frame.grid_columnconfigure(
            indice,
            minsize=largura
        )

    # ==========================
    # CÓDIGO
    # ==========================

    codigo = ctk.CTkLabel(
        frame,
        text=paciente["codigo"],
        width=COLUNAS_HISTORICO[0][1],
        font=("Consolas", 12, "bold"),
        text_color=COR_AZUL,
        anchor="center"
    )
    codigo.grid(
        row=0,
        column=0,
        padx=5,
        pady=20,
        sticky="nsew"
    )

    # ==========================
    # PACIENTE
    # ==========================

    bloco_paciente = ctk.CTkFrame(
        frame,
        fg_color="transparent",
        width=COLUNAS_HISTORICO[1][1],
        height=100
    )
    bloco_paciente.grid(
        row=0,
        column=1,
        padx=5,
        pady=12,
        sticky="nsew"
    )
    bloco_paciente.pack_propagate(False)

    nome = ctk.CTkLabel(
        bloco_paciente,
        text=paciente["nome"],
        font=("Arial", 13, "bold"),
        text_color=COR_TEXTO,
        wraplength=155,
        justify="center"
    )
    nome.pack(
        anchor="center",
        fill="x",
        pady=(12, 5)
    )

    documento = ctk.CTkLabel(
        bloco_paciente,
        text=f"DOC: {paciente['documento']}",
        font=("Consolas", 10),
        text_color=COR_TEXTO_SUAVE,
        wraplength=155,
        justify="center"
    )
    documento.pack(
        anchor="center",
        fill="x"
    )

    # ==========================
    # IDADE
    # ==========================

    idade = ctk.CTkLabel(
        frame,
        text=paciente["idade"],
        width=COLUNAS_HISTORICO[2][1],
        font=("Arial", 13, "bold"),
        text_color=COR_TEXTO,
        anchor="center"
    )
    idade.grid(
        row=0,
        column=2,
        padx=5,
        pady=20,
        sticky="nsew"
    )

    # ==========================
    # SINTOMAS E DESCRIÇÃO
    # ==========================

    bloco_sintomas = ctk.CTkFrame(
        frame,
        fg_color="transparent",
        width=COLUNAS_HISTORICO[3][1],
        height=100
    )
    bloco_sintomas.grid(
        row=0,
        column=3,
        padx=5,
        pady=12,
        sticky="nsew"
    )
    bloco_sintomas.pack_propagate(False)

    sintomas_lista = paciente["sintomas"].split(",")

    linha_badges = ctk.CTkFrame(
        bloco_sintomas,
        fg_color="transparent"
    )
    linha_badges.pack(
        anchor="center",
        pady=(5, 4)
    )

    for sintoma in sintomas_lista[:2]:
        sintoma = sintoma.strip()

        if sintoma:
            badge = criar_badge(
                linha_badges,
                sintoma,
                COR_TEXTO_SUAVE,
                "#202020"
            )
            badge.pack(
                side="left",
                padx=3
            )

    descricao_texto = paciente["descricao"]

    if len(descricao_texto) > 100:
        descricao_texto = descricao_texto[:100] + "..."

    descricao = ctk.CTkLabel(
        bloco_sintomas,
        text=descricao_texto or "Sem descrição informada.",
        font=("Arial", 11, "italic"),
        text_color=COR_TEXTO_SUAVE,
        wraplength=280,
        justify="center"
    )
    descricao.pack(
        anchor="center",
        fill="x",
        padx=8,
        pady=(4, 0)
    )

    # ==========================
    # CHEGADA
    # ==========================

    chegada = ctk.CTkLabel(
        frame,
        text=paciente["chegada_formatada"],
        width=COLUNAS_HISTORICO[4][1],
        font=("Consolas", 12),
        text_color=COR_TEXTO_SUAVE,
        justify="center",
        anchor="center"
    )
    chegada.grid(
        row=0,
        column=4,
        padx=5,
        pady=20,
        sticky="nsew"
    )

    # ==========================
    # PRIORIDADE
    # ==========================

    bloco_prioridade = ctk.CTkFrame(
        frame,
        fg_color="transparent",
        width=COLUNAS_HISTORICO[5][1],
        height=80
    )
    bloco_prioridade.grid(
        row=0,
        column=5,
        padx=5,
        pady=20,
        sticky="nsew"
    )
    bloco_prioridade.pack_propagate(False)

    badge_prioridade = criar_badge(
        bloco_prioridade,
        paciente["prioridade"].upper(),
        cor_prioridade(paciente["prioridade"]),
        "#202020"
    )
    badge_prioridade.pack(
        anchor="center",
        pady=25
    )

    # ==========================
    # TEMPO DE ESPERA
    # ==========================

    espera = ctk.CTkLabel(
        frame,
        text=paciente["tempo_espera"],
        width=COLUNAS_HISTORICO[6][1],
        font=("Arial", 12, "bold"),
        text_color=COR_TEXTO_SUAVE,
        anchor="center"
    )
    espera.grid(
        row=0,
        column=6,
        padx=5,
        pady=20,
        sticky="nsew"
    )

    # ==========================
    # STATUS
    # ==========================

    status_cor = "#202020"
    status_texto = COR_TEXTO_SUAVE

    if paciente["status"] == "FINALIZADO":
        status_cor = "#123524"
        status_texto = COR_VERDE

    elif paciente["status"] == "EM ATENDIMENTO":
        status_cor = COR_ROXO_FUNDO
        status_texto = COR_ROXO

    elif paciente["status"] == "AGUARDANDO":
        status_cor = "#3a244d"
        status_texto = COR_ROXO

    bloco_status = ctk.CTkFrame(
        frame,
        fg_color="transparent",
        width=COLUNAS_HISTORICO[7][1],
        height=80
    )
    bloco_status.grid(
        row=0,
        column=7,
        padx=5,
        pady=20,
        sticky="nsew"
    )
    bloco_status.pack_propagate(False)

    status = ctk.CTkLabel(
        bloco_status,
        text=paciente["status"],
        font=("Arial", 10, "bold"),
        text_color=status_texto,
        fg_color=status_cor,
        corner_radius=7,
        width=105,
        height=32
    )
    status.pack(
        anchor="center",
        pady=24
    )
    
# ==========================
# TELA PRINCIPAL
# ==========================

def criar_tela_historico(master):
    master.configure(fg_color="#242424")
    master.grid_columnconfigure(0, weight=1)

    todos_pacientes = preparar_pacientes()

    container = ctk.CTkFrame(
        master,
        fg_color="transparent"
    )
    container.grid(row=0, column=0, sticky="n", padx=20, pady=20)

    # TOPO
    topo = ctk.CTkFrame(
        container,
        width=LARGURA_CARD,
        height=95,
        fg_color=COR_CARD,
        corner_radius=18,
        border_width=1,
        border_color="#3a3a3a"
    )
    topo.grid(row=0, column=0, sticky="ew", pady=(0, 25))
    topo.pack_propagate(False)

    titulo = ctk.CTkLabel(
        topo,
        text="▱  Prontuário e Histórico de Atendimentos",
        font=("Arial", 22, "bold"),
        text_color=COR_TEXTO
    )
    titulo.pack(anchor="w", padx=25, pady=(20, 0))

    subtitulo = ctk.CTkLabel(
        topo,
        text="Filtre, pesquise e audite todos os prontuários registrados no sistema, com cópias de auditoria integradas.",
        font=("Segoe UI Light", 15),
        text_color=COR_TEXTO_SUAVE
    )
    subtitulo.pack(anchor="w", padx=25, pady=(5, 0))

    # FILTROS
    card_filtros = ctk.CTkFrame(
        container,
        width=LARGURA_CARD,
        height=180,
        fg_color=COR_CARD,
        corner_radius=18,
        border_width=1,
        border_color="#3a3a3a"
    )
    card_filtros.grid(row=1, column=0, sticky="ew", pady=(0, 25))
    card_filtros.pack_propagate(False)

    titulo_filtros = ctk.CTkLabel(
        card_filtros,
        text="☷  FILTROS AVANÇADOS DE PRONTUÁRIOS",
        font=("Arial", 14, "bold"),
        text_color=COR_TEXTO
    )
    titulo_filtros.pack(anchor="w", padx=25, pady=(20, 10))

    linha = ctk.CTkFrame(card_filtros, fg_color="transparent")
    linha.pack(anchor="w", padx=25, pady=(5, 0))

    bloco_busca, campo_busca = criar_campo_filtro(
        linha,
        "BUSCA POR NOME / DOCUMENTO",
        "Nome ou documento...",
        190
    )
    bloco_busca.pack(side="left", padx=(0, 12))

    bloco_prioridade, campo_prioridade = criar_select_filtro(
        linha,
        "GRAU DE PRIORIDADE",
        ["Todas no sistema", "Emergência", "Urgente", "Pouco Urgente"],
        170
    )
    bloco_prioridade.pack(side="left", padx=(0, 12))

    bloco_status, campo_status = criar_select_filtro(
        linha,
        "STATUS DO PACIENTE",
        ["Todos os status", "AGUARDANDO", "EM ATENDIMENTO", "FINALIZADO"],
        170
    )
    bloco_status.pack(side="left", padx=(0, 12))

    bloco_data, campo_data = criar_campo_filtro(
        linha,
        "DATA DE CHEGADA",
        "dd/mm/aaaa",
        150
    )
    bloco_data.pack(side="left", padx=(0, 12))

    bloco_profissional, campo_profissional = criar_campo_filtro(
        linha,
        "PROFISSIONAL / RESPONSÁVEL",
        "Nome do enfermeiro/recep",
        180
    )
    bloco_profissional.pack(side="left", padx=(0, 12))

    bloco_sintoma, campo_sintoma = criar_campo_filtro(
        linha,
        "FILTRAR POR SINTOMA",
        "Ex: febre, dor no peito...",
        180
    )
    bloco_sintoma.pack(side="left")

    rodape_filtros = ctk.CTkFrame(card_filtros, fg_color="transparent")
    rodape_filtros.pack(fill="x", padx=90, pady=(5, 0))

    contador = ctk.CTkLabel(
        rodape_filtros,
        text=f"Encontrados: {len(todos_pacientes)} prontuários (Total: {len(todos_pacientes)})",
        font=("Arial", 13, "bold"),
        text_color=COR_TEXTO_SUAVE
    )
    contador.pack(side="left")

    botao_limpar = ctk.CTkButton(
        rodape_filtros,
        text="↻ Limpar Filtros",
        width=130,
        height=32,
        fg_color=COR_CARD_CLARO,
        hover_color="#3a3a3a",
        border_width=1,
        border_color=COR_BORDA,
        text_color=COR_TEXTO,
        font=("Arial", 12, "bold")
    )
    botao_limpar.pack(side="right")

    # TABELA
    card_tabela = ctk.CTkFrame(
        container,
        width=LARGURA_CARD,
        fg_color=COR_CARD,
        corner_radius=18,
        border_width=1,
        border_color="#3a3a3a"
    )
    card_tabela.grid(row=2, column=0, sticky="ew", pady=(0, 25))

    cabecalho = ctk.CTkFrame(
        card_tabela,
        width=LARGURA_TABELA,
        fg_color=COR_CARD_CLARO,
        height=70
    )
    cabecalho.pack(fill="x", padx=25, pady=(25, 0))
    cabecalho.pack_propagate(False)

    for indice, (texto, largura) in enumerate(COLUNAS_HISTORICO):
        cabecalho.grid_columnconfigure(indice, minsize=largura)

        label = ctk.CTkLabel(
            cabecalho,
            text=texto,
            width=largura,
            font=("Arial", 11, "bold"),
            text_color=COR_TEXTO_SUAVE,
            justify="center",
            anchor="center"
        )

        label.grid(
            row=0,
            column=indice,
            sticky="nsew",
            padx=5,
            pady=15
        )

    corpo = ctk.CTkFrame(card_tabela, width=LARGURA_TABELA, fg_color="transparent")
    corpo.pack(fill="x", padx=25, pady=(0, 25))
    corpo.grid_columnconfigure(0, weight=1)

    def filtrar_pacientes():
        termo = campo_busca.get().strip().lower()
        prioridade = campo_prioridade.get()
        status = campo_status.get()
        data = campo_data.get().strip()
        sintoma = campo_sintoma.get().strip().lower()

        filtrados = []

        for paciente in todos_pacientes:
            passou = True

            if termo:
                texto_busca = f"{paciente['nome']} {paciente['documento']}".lower()

                if termo not in texto_busca:
                    passou = False

            if prioridade != "Todas no sistema":
                if paciente["prioridade"] != prioridade:
                    passou = False

            if status != "Todos os status":
                if paciente["status"] != status:
                    passou = False

            if data:
                if data not in paciente["chegada_formatada"].replace("\n", " "):
                    passou = False

            if sintoma:
                if sintoma not in paciente["sintomas"].lower():
                    passou = False

            if passou:
                filtrados.append(paciente)

        return filtrados

    def renderizar_tabela(event=None):
        for widget in corpo.winfo_children():
            widget.destroy()

        pacientes_filtrados = filtrar_pacientes()

        contador.configure(
            text=f"Encontrados: {len(pacientes_filtrados)} prontuários (Total: {len(todos_pacientes)})"
        )

        if len(pacientes_filtrados) == 0:
            vazio = ctk.CTkLabel(
                corpo,
                text="Nenhum prontuário encontrado com os filtros aplicados.",
                font=("Arial", 15, "bold"),
                text_color=COR_TEXTO_SUAVE
            )
            vazio.pack(pady=35)
            return

        for indice, paciente in enumerate(pacientes_filtrados):
            criar_linha_historico(corpo, paciente, indice)

    def limpar_filtros():
        campo_busca.delete(0, "end")
        campo_data.delete(0, "end")
        campo_profissional.delete(0, "end")
        campo_sintoma.delete(0, "end")
        campo_prioridade.set("Todas no sistema")
        campo_status.set("Todos os status")
        renderizar_tabela()

    campo_busca.bind("<KeyRelease>", renderizar_tabela)
    campo_data.bind("<KeyRelease>", renderizar_tabela)
    campo_sintoma.bind("<KeyRelease>", renderizar_tabela)

    campo_prioridade.configure(command=lambda valor: renderizar_tabela())
    campo_status.configure(command=lambda valor: renderizar_tabela())

    botao_limpar.configure(command=limpar_filtros)

    renderizar_tabela()