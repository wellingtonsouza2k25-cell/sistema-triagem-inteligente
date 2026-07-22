import customtkinter as ctk
from componentes import criar_label, campo_com_label, texto_com_label

COR_CARD = "#242424"
COR_CARD_HOVER = "#333333"
COR_CARD_SELECIONADO = "#eef4ff"
COR_BORDA = "#dce1e7"
COR_TEXTO = "#ffffff"
COR_TEXTO_ESCURO = "#0f2544"

COR_VERMELHO = "#ef3b6d"
COR_AMARELO = "#f6b000"
COR_VERDE = "#22c55e"

lista_sintomas = [
    {"nome": "Dor no peito", "cor": COR_VERMELHO},
    {"nome": "Falta de ar", "cor": COR_VERMELHO},
    {"nome": "Falta de ar intensa", "cor": COR_VERMELHO},
    {"nome": "Desmaio", "cor": COR_VERMELHO},
    {"nome": "Sangramento", "cor": COR_AMARELO},
    {"nome": "Sangramento intenso", "cor": COR_VERMELHO},
    {"nome": "Dor forte", "cor": COR_AMARELO},
    {"nome": "Dor de cabeça forte", "cor": COR_AMARELO},
    {"nome": "Dor de cabeça", "cor": COR_VERDE},
    {"nome": "Dor de garganta", "cor": COR_VERDE},
    {"nome": "Dor abdominal", "cor": COR_AMARELO},
    {"nome": "Dor abdominal intensa", "cor": COR_AMARELO},
    {"nome": "Tosse", "cor": COR_VERDE},
    {"nome": "Vômito", "cor": COR_AMARELO},
    {"nome": "Vômitos persistentes", "cor": COR_AMARELO},
    {"nome": "Tontura", "cor": COR_VERDE},
    {"nome": "Coriza", "cor": COR_VERDE},
    {"nome": "Tontura forte", "cor": COR_AMARELO},
    {"nome": "Náusea", "cor": COR_AMARELO},
    {"nome": "Febre", "cor": COR_AMARELO},
]

sintomas_selecionados = []


def criar_tela_sintomas(janela):
    titulo = criar_label(
        janela,
        "Sintomas e Quadro de Sintomas",
        tamanho=20,
        icone="imagens/symptom.png"
    )
    titulo.grid(row=3, column=0, sticky="w", padx=15, pady=(20, 0))

    frame_topo = ctk.CTkFrame(janela, fg_color="transparent")
    frame_topo.grid(row=4, column=0, sticky="w", padx=15, pady=(10, 0))

    label_contador = ctk.CTkLabel(
        frame_topo,
        text="Selecione os sintomas informados (0 ativos)",
        font=("Arial", 14, "bold"),
        text_color=COR_TEXTO
    )
    label_contador.pack(side="left", padx=(0, 30))

    campo_busca = ctk.CTkEntry(
        frame_topo,
        width=250,
        height=36,
        corner_radius=10,
        border_width=1,
        border_color=COR_BORDA,
        fg_color="#242424",
        text_color="white",
        placeholder_text="Buscar sintoma...",
        font=("Arial", 14)
    )
    campo_busca.pack(side="left")

    area_cards = ctk.CTkScrollableFrame(
        master=janela,
        width=600,
        height=210,
        fg_color="#242424",
        border_width=1,
        border_color=COR_BORDA,
        corner_radius=12
    )
    area_cards.grid(row=5, column=0, sticky="w", padx=15, pady=(15, 20))

    def atualizar_contador():
        total = len(sintomas_selecionados)
        label_contador.configure(
            text=f"Selecione os sintomas informados ({total} ativos)"
        )

    def criar_card_sintoma(master, nome, cor, linha, coluna):
        selecionado = nome in sintomas_selecionados

        if selecionado:
            cor_fundo = COR_CARD_SELECIONADO
            cor_hover = COR_CARD_SELECIONADO
            cor_texto = COR_TEXTO_ESCURO
            cor_borda = "#1f6feb"
        else:
            cor_fundo = COR_CARD
            cor_hover = COR_CARD_HOVER
            cor_texto = "white"
            cor_borda = COR_BORDA

        card = ctk.CTkButton(
            master=master,
            text=nome,
            width=190,
            height=38,
            corner_radius=9,
            fg_color=cor_fundo,
            hover_color=cor_hover,
            border_width=1,
            border_color=cor_borda,
            text_color=cor_texto,
            font=("Arial", 14),
            anchor="w"
        )

        card.grid(row=linha, column=coluna, padx=5, pady=5, sticky="w")

        bolinha = ctk.CTkLabel(
            master=card,
            text="●",
            font=("Arial", 15, "bold"),
            text_color=cor,
            fg_color=cor_fundo,
            bg_color=cor_fundo
        )

        bolinha.place(relx=0.92, rely=0.5, anchor="center")

        def selecionar():
            if nome in sintomas_selecionados:
                sintomas_selecionados.remove(nome)

                card.configure(
                    fg_color=COR_CARD,
                    hover_color=COR_CARD_HOVER,
                    border_color=COR_BORDA,
                    text_color="white"
                )

                bolinha.configure(
                    fg_color=COR_CARD,
                    bg_color=COR_CARD
                )

            else:
                sintomas_selecionados.append(nome)

                card.configure(
                    fg_color=COR_CARD_SELECIONADO,
                    hover_color=COR_CARD_SELECIONADO,
                    border_color="#1f6feb",
                    text_color=COR_TEXTO_ESCURO
                )

                bolinha.configure(
                    fg_color=COR_CARD_SELECIONADO,
                    bg_color=COR_CARD_SELECIONADO
                )

            atualizar_contador()
            print(sintomas_selecionados)

        card.configure(command=selecionar)

        return card

    def renderizar_cards():
        for widget in area_cards.winfo_children():
            widget.destroy()

        termo = campo_busca.get().lower().strip()

        sintomas_filtrados = []

        for sintoma in lista_sintomas:
            if termo in sintoma["nome"].lower():
                sintomas_filtrados.append(sintoma)

        linha = 0
        coluna = 0

        for sintoma in sintomas_filtrados:
            criar_card_sintoma(
                area_cards,
                sintoma["nome"],
                sintoma["cor"],
                linha,
                coluna
            )

            coluna += 1

            if coluna == 3:
                coluna = 0
                linha += 1

    def buscar_sintoma(event=None):
        renderizar_cards()

    campo_busca.bind("<KeyRelease>", buscar_sintoma)

    renderizar_cards()
    atualizar_contador()

    return {
        "sintomas_selecionados": sintomas_selecionados,
        "campo_busca": campo_busca
    }

def descricao_livre(janela):
    placeholder_descricao = "Relate em detalhes a queixa do paciente. Ex: Paciente alega forte dor de cabeça com queimação nas costas iniciada há duas horas acompanhada de náusea."
    placeholder_sinais = "Ex: Palidez conjuntival, febre ao toque, tremores nas extremidades."
    placeholder_observacoes = "Ex: Histórico cardíaco familiar, toma medicação para pressão regularmente."

    bloco_descricao, campo_descricao = texto_com_label(
        janela,
        "Descrição Livre do Caso (Relato e Queixa)",
        placeholder_descricao,
        630,
        130
    )

    bloco_descricao.grid(
        row=6,
        column=0,
        sticky="w",
        padx=15,
        pady=(0, 0)
    )

    frame_campos_pequenos = ctk.CTkFrame(
        janela,
        fg_color="transparent"
    )

    frame_campos_pequenos.grid(
        row=7,
        column=0,
        sticky="w",
        padx=15,
        pady=(0, 0)
    )

    bloco_sinais, campo_sinais = texto_com_label(
        frame_campos_pequenos,
        "Sinais Físicos Observados",
        placeholder_sinais,
        305,
        120
    )

    bloco_sinais.pack(
        side="left",
        padx=(0, 20)
    )

    bloco_observacoes, campo_observacoes = texto_com_label(
        frame_campos_pequenos,
        "Observações Adicionais",
        placeholder_observacoes,
        305,
        120
    )

    bloco_observacoes.pack(
        side="left"
    )

    return {
        "campo_descricao": campo_descricao,
        "campo_sinais": campo_sinais,
        "campo_observacoes": campo_observacoes,
        "placeholder_descricao": placeholder_descricao,
        "placeholder_sinais": placeholder_sinais,
        "placeholder_observacoes": placeholder_observacoes
    }