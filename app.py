import customtkinter as ctk

from database import criar_tabela
from cadastrar import criar_tela_cadastro
from pacientes import abrir_janela_pacientes
from sintomas import criar_tela_sintomas, descricao_livre
from fila_de_atendimento import criar_tela_fila
from historico import criar_tela_historico
from relatorios import criar_tela_relatorios
from painel_espera import PainelEspera

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

criar_tabela()


janela = ctk.CTk()
janela.title("Sistema de Triagem Inteligente")
janela.geometry("1200x750")
janela.configure(fg_color="#242424")

painel_espera = PainelEspera(janela)


# ==========================
# CORES
# ==========================

COR_HEADER = "#323232"
COR_TEXTO_ESCURO = "#111827"
COR_TEXTO_CLARO = "#6b7280"
COR_BOTAO_ATIVO = "#0f172a"
COR_BOTAO_NORMAL = "#ffffff"
COR_HOVER = "#e5e7eb"
COR_CONTEUDO = "#242424"


# ==========================
# CABEÇALHO
# ==========================

header = ctk.CTkFrame(
    janela,
    height=80,
    fg_color=COR_HEADER,
    corner_radius=0
)
header.pack(fill="x", side="top")
header.pack_propagate(False)

menu_header = ctk.CTkFrame(
    header,
    fg_color="transparent"
)

menu_header.place(
    relx=0.5,
    rely=0.5,
    anchor="center"
)

# ==========================
# ÁREA DE CONTEÚDO
# ==========================

area_conteudo = ctk.CTkScrollableFrame(
    janela,
    fg_color=COR_CONTEUDO,
    corner_radius=0
)
area_conteudo.pack(fill="both", expand=True)


# ==========================
# FUNÇÕES PARA TROCAR TELAS
# ==========================

botoes_menu = []


def limpar_conteudo():
    for widget in area_conteudo.winfo_children():
        widget.destroy()


def atualizar_botao_ativo(botao_ativo):
    for botao in botoes_menu:
        botao.configure(
            fg_color=COR_BOTAO_NORMAL,
            hover_color=COR_HOVER,
            text_color="#4b5563"
        )

    botao_ativo.configure(
        fg_color=COR_BOTAO_ATIVO,
        hover_color=COR_BOTAO_ATIVO,
        text_color="#ffffff"
    )


def mostrar_cadastro(botao):
    limpar_conteudo()
    atualizar_botao_ativo(botao)

    area_conteudo.grid_columnconfigure(0, weight=1)

    frame_central = ctk.CTkFrame(
        area_conteudo,
        fg_color="transparent"
    )

    frame_central.grid(
        row=0,
        column=0,
        sticky="n",
        pady=(20, 40)
    )

    campos_sintomas = criar_tela_sintomas(frame_central)
    campos_textos = descricao_livre(frame_central)

    criar_tela_cadastro(
        frame_central,
        campos_sintomas,
        campos_textos
    )



def mostrar_fila(botao):
    limpar_conteudo()
    atualizar_botao_ativo(botao)

    criar_tela_fila(area_conteudo, painel_espera)


def mostrar_historico(botao):
    limpar_conteudo()
    atualizar_botao_ativo(botao)

    criar_tela_historico(area_conteudo)


def mostrar_relatorios(botao):
    limpar_conteudo()
    atualizar_botao_ativo(botao)
    area_conteudo.configure(fg_color="#242424")

    criar_tela_relatorios(area_conteudo)


# ==========================
# BOTÕES DO MENU
# ==========================

def criar_botao_menu(texto):
    botao = ctk.CTkButton(
        menu_header,
        text=texto,
        width=150,
        height=55,
        corner_radius=9,
        fg_color=COR_BOTAO_NORMAL,
        hover_color=COR_HOVER,
        text_color="#4b5563",
        font=("Arial", 14, "bold")
    )
    botao.pack(side="left", padx=8, pady=12)

    botoes_menu.append(botao)

    return botao


botao_cadastro = criar_botao_menu("Cadastrar\nPaciente")
botao_fila = criar_botao_menu("Fila de\nAtendimento")
botao_historico = criar_botao_menu("Histórico de\nAtendimentos")
botao_relatorios = criar_botao_menu("Relatórios &\nEstatísticas")


botao_cadastro.configure(command=lambda: mostrar_cadastro(botao_cadastro))
botao_fila.configure(command=lambda: mostrar_fila(botao_fila))
botao_historico.configure(command=lambda: mostrar_historico(botao_historico))
botao_relatorios.configure(command=lambda: mostrar_relatorios(botao_relatorios))


# Tela inicial
mostrar_cadastro(botao_cadastro)


janela.mainloop()