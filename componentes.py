import customtkinter as ctk
from PIL import Image


COR_TEXTO = "#ffffff"
COR_BORDA = "#dce1e7"
COR_INPUT = "#242424"


def criar_label(master, texto, tamanho=15, tipo_fonte="Arial", peso="bold", icone=None):
    if icone:
        imagem = ctk.CTkImage(
            light_image=Image.open(icone),
            dark_image=Image.open(icone),
            size=(24, 24)
        )

        label = ctk.CTkLabel(
            master=master,
            text="  " + texto,
            image=imagem,
            compound="left",
            font=(tipo_fonte, tamanho, peso),
            text_color=COR_TEXTO
        )

        label.image = imagem

    else:
        label = ctk.CTkLabel(
            master=master,
            text=texto,
            font=(tipo_fonte, tamanho, peso),
            text_color=COR_TEXTO
        )

    return label

def texto_com_label(master, texto, placeholder, largura, altura):
    bloco = ctk.CTkFrame(master, fg_color="transparent")

    label = ctk.CTkLabel(
        bloco,
        text=texto,
        font=("Arial", 12, "bold"),
        text_color=COR_TEXTO
    )
    label.pack(anchor="w", pady=(0, 5))

    campo = ctk.CTkTextbox(
        bloco,
        width=largura,
        height=altura,
        corner_radius=14,
        border_width=1,
        border_color=COR_BORDA,
        fg_color=COR_INPUT,
        text_color="#b8bec9",
        font=("Arial", 15)
    )
    campo.pack(anchor="w")

    campo.insert("1.0", placeholder)

    def ao_focar(event):
        texto_atual = campo.get("1.0", "end").strip()

        if texto_atual == placeholder:
            campo.delete("1.0", "end")
            campo.configure(text_color="white")

    def ao_sair(event):
        texto_atual = campo.get("1.0", "end").strip()

        if texto_atual == "":
            campo.insert("1.0", placeholder)
            campo.configure(text_color="#b8bec9")

    campo.bind("<FocusIn>", ao_focar)
    campo.bind("<FocusOut>", ao_sair)

    return bloco, campo

def campo_com_label(master, texto, placeholder, largura, altura=40):
    bloco = ctk.CTkFrame(master, fg_color="transparent")

    label = ctk.CTkLabel(
        bloco,
        text=texto,
        font=("Arial", 12, "bold"),
        text_color=COR_TEXTO
    )
    label.pack(anchor="w", pady=(0, 5))

    campo = ctk.CTkEntry(
        bloco,
        width=largura,
        height=altura,
        corner_radius=14,
        border_width=1,
        border_color=COR_BORDA,
        fg_color=COR_INPUT,
        text_color="white",
        placeholder_text=placeholder,
        font=("Arial", 15)
    )
    campo.pack(anchor="w")

    return bloco, campo


def select_com_label(master, texto, largura):
    bloco = ctk.CTkFrame(master, fg_color="transparent")

    label = ctk.CTkLabel(
        bloco,
        text=texto,
        font=("Arial", 12, "bold"),
        text_color=COR_TEXTO
    )
    label.pack(anchor="w", pady=(0, 5))

    campo = ctk.CTkComboBox(
        bloco,
        values=["Masculino", "Feminino", "Outro"],
        width=largura,
        height=40,
        corner_radius=14,
        border_width=1,
        border_color=COR_BORDA,
        fg_color=COR_INPUT,
        text_color="white",
        font=("Arial", 15)
    )
    campo.set("Masculino")
    campo.pack(anchor="w")

    return bloco, campo


def criar_botao(master, texto, comando, cor="#1f6feb", hover="#174ea6"):
    botao = ctk.CTkButton(
        master,
        text=texto,
        width=220,
        height=45,
        command=comando,
        corner_radius=12,
        fg_color=cor,
        hover_color=hover,
        text_color="#ffffff",
        font=("Arial", 14, "bold")
    )

    return botao

def criar_busca(master, linha, coluna, distancia):
    campo_busca = ctk.CTkEntry(
        master,
        width=300,
        height=40,
        corner_radius=12,
        placeholder_text="Buscar sintoma...",
        fg_color="#242424",
        border_color="#dce1e7",
        text_color="white",
        font=("Arial", 14)
    )

    campo_busca.grid(row=linha, column=coluna, padx=distancia, pady=20)

    return campo_busca