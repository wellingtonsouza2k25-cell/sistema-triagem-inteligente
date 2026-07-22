import sys
import customtkinter as ctk


COR_FUNDO = "#071a2d"
COR_TOPO = "#0d2b47"
COR_DESTAQUE = "#19c3ff"
COR_DESTAQUE_2 = "#43e3a1"
COR_TEXTO = "#ffffff"
COR_TEXTO_SUAVE = "#b8d2e8"
COR_CARD = "#0b2239"
COR_BORDA = "#1d5277"


def _emitir_bip(janela):
    """Emite um alerta sonoro no Windows e usa o sino do Tk como alternativa."""
    try:
        if sys.platform.startswith("win"):
            import winsound

            winsound.Beep(1250, 180)
        else:
            janela.bell()
    except Exception:
        try:
            janela.bell()
        except Exception:
            pass


def abrir_painel_chamada(master, paciente, destino="SALA DE ATENDIMENTO", tempo_exibicao=20):
    """Abre um painel em tela cheia com nome, código e alerta sonoro."""
    janela_principal = master.winfo_toplevel()

    painel = ctk.CTkToplevel(janela_principal)
    painel.title("Painel de Chamada de Pacientes")
    painel.configure(fg_color=COR_FUNDO)
    painel.protocol("WM_DELETE_WINDOW", painel.destroy)

    # Primeiro maximiza; depois tenta ativar tela cheia. O fallback evita erro
    # em ambientes onde o atributo fullscreen não está disponível.
    try:
        painel.state("zoomed")
    except Exception:
        largura = painel.winfo_screenwidth()
        altura = painel.winfo_screenheight()
        painel.geometry(f"{largura}x{altura}+0+0")

    try:
        painel.attributes("-fullscreen", True)
        painel.attributes("-topmost", True)
    except Exception:
        pass

    painel.lift()
    painel.focus_force()

    painel.grid_rowconfigure(1, weight=1)
    painel.grid_columnconfigure(0, weight=1)

    faixa_topo = ctk.CTkFrame(
        painel,
        height=95,
        corner_radius=0,
        fg_color=COR_TOPO,
    )
    faixa_topo.grid(row=0, column=0, sticky="ew")
    faixa_topo.grid_propagate(False)

    titulo_topo = ctk.CTkLabel(
        faixa_topo,
        text="PAINEL DE CHAMADA",
        font=("Arial", 30, "bold"),
        text_color=COR_TEXTO,
    )
    titulo_topo.pack(side="left", padx=40, pady=24)

    subtitulo_topo = ctk.CTkLabel(
        faixa_topo,
        text="TRIAGEM E ATENDIMENTO",
        font=("Arial", 18, "bold"),
        text_color=COR_TEXTO_SUAVE,
    )
    subtitulo_topo.pack(side="right", padx=40, pady=30)

    conteudo = ctk.CTkFrame(painel, fg_color="transparent")
    conteudo.grid(row=1, column=0, sticky="nsew", padx=50, pady=35)
    conteudo.grid_columnconfigure(0, weight=1)
    conteudo.grid_rowconfigure(0, weight=1)

    card = ctk.CTkFrame(
        conteudo,
        fg_color=COR_CARD,
        border_width=2,
        border_color=COR_BORDA,
        corner_radius=28,
    )
    card.grid(row=0, column=0, sticky="nsew")
    card.grid_columnconfigure(0, weight=1)
    card.grid_rowconfigure(3, weight=1)

    ctk.CTkLabel(
        card,
        text="🔔  PACIENTE CHAMADO",
        font=("Arial", 28, "bold"),
        text_color=COR_DESTAQUE_2,
    ).grid(row=0, column=0, pady=(38, 12))

    codigo = str(paciente.get("codigo", "---"))
    nome = str(paciente.get("nome", "PACIENTE"))
    prioridade = str(paciente.get("prioridade", ""))

    ctk.CTkLabel(
        card,
        text=codigo,
        font=("Consolas", 92, "bold"),
        text_color=COR_DESTAQUE,
    ).grid(row=1, column=0, pady=(0, 5))

    ctk.CTkLabel(
        card,
        text=nome.upper(),
        font=("Arial", 52, "bold"),
        text_color=COR_TEXTO,
        wraplength=max(painel.winfo_screenwidth() - 180, 800),
        justify="center",
    ).grid(row=2, column=0, padx=45, pady=(0, 25))

    bloco_destino = ctk.CTkFrame(
        card,
        fg_color="#0e304e",
        corner_radius=18,
        border_width=1,
        border_color="#276589",
    )
    bloco_destino.grid(row=3, column=0, sticky="n", padx=80, pady=(5, 25))

    ctk.CTkLabel(
        bloco_destino,
        text="DIRIJA-SE À",
        font=("Arial", 20, "bold"),
        text_color=COR_TEXTO_SUAVE,
    ).pack(padx=70, pady=(18, 4))

    ctk.CTkLabel(
        bloco_destino,
        text=destino.upper(),
        font=("Arial", 34, "bold"),
        text_color=COR_TEXTO,
    ).pack(padx=70, pady=(0, 18))

    if prioridade:
        ctk.CTkLabel(
            card,
            text=f"CLASSIFICAÇÃO: {prioridade.upper()}",
            font=("Arial", 16, "bold"),
            text_color=COR_TEXTO_SUAVE,
        ).grid(row=4, column=0, pady=(0, 18))

    rodape = ctk.CTkFrame(painel, height=85, fg_color=COR_TOPO, corner_radius=0)
    rodape.grid(row=2, column=0, sticky="ew")
    rodape.grid_propagate(False)

    label_tempo = ctk.CTkLabel(
        rodape,
        text="",
        font=("Arial", 14, "bold"),
        text_color=COR_TEXTO_SUAVE,
    )
    label_tempo.pack(side="left", padx=35, pady=28)

    botao_repetir = ctk.CTkButton(
        rodape,
        text="🔊  Repetir alerta",
        width=180,
        height=42,
        corner_radius=10,
        fg_color="#156c9b",
        hover_color="#115b83",
        text_color=COR_TEXTO,
        font=("Arial", 14, "bold"),
    )
    botao_repetir.pack(side="right", padx=(10, 20), pady=21)

    botao_fechar = ctk.CTkButton(
        rodape,
        text="Fechar painel  (ESC)",
        width=185,
        height=42,
        corner_radius=10,
        fg_color="#334155",
        hover_color="#475569",
        text_color=COR_TEXTO,
        font=("Arial", 14, "bold"),
        command=painel.destroy,
    )
    botao_fechar.pack(side="right", padx=(10, 0), pady=21)

    callbacks = []

    def agendar(delay, func):
        try:
            identificador = painel.after(delay, func)
            callbacks.append(identificador)
        except Exception:
            pass

    def tocar_sequencia():
        for indice in range(4):
            agendar(indice * 430, lambda: _emitir_bip(painel))

    def pulsar(estado=False):
        if not painel.winfo_exists():
            return

        faixa_topo.configure(fg_color=COR_DESTAQUE if estado else COR_TOPO)
        titulo_topo.configure(text_color=COR_FUNDO if estado else COR_TEXTO)
        subtitulo_topo.configure(
            text_color=COR_FUNDO if estado else COR_TEXTO_SUAVE
        )

        agendar(650, lambda: pulsar(not estado))

    segundos_restantes = max(int(tempo_exibicao or 0), 0)

    def atualizar_contagem(segundos):
        if not painel.winfo_exists():
            return

        if segundos <= 0:
            painel.destroy()
            return

        label_tempo.configure(
            text=f"Este painel fechará automaticamente em {segundos}s"
        )
        agendar(1000, lambda: atualizar_contagem(segundos - 1))

    botao_repetir.configure(command=tocar_sequencia)
    painel.bind("<Escape>", lambda event: painel.destroy())
    painel.bind("<F5>", lambda event: tocar_sequencia())

    tocar_sequencia()
    pulsar()

    if segundos_restantes > 0:
        atualizar_contagem(segundos_restantes)
    else:
        label_tempo.configure(text="Pressione ESC para fechar o painel")

    return painel
