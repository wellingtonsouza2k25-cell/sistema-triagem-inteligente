import threading
import time
from datetime import datetime

import customtkinter as ctk
from screeninfo import get_monitors

from database import buscar_pacientes_fila

try:
    import winsound
except ImportError:
    winsound = None


COR_FUNDO = "#0f172a"
COR_CARD = "#1e293b"
COR_TEXTO = "#ffffff"
COR_TEXTO_SUAVE = "#cbd5e1"

TEMPO_MEDIO_ATENDIMENTO = 15  # minutos por paciente


def ordem_prioridade(prioridade):
    if prioridade == "Emergência":
        return 1

    if prioridade == "Urgente":
        return 2

    return 3


def gerar_codigo(id_paciente, prioridade):
    if prioridade == "Emergência":
        return f"E-{id_paciente:03d}"

    if prioridade == "Urgente":
        return f"U-{id_paciente:03d}"

    return f"P-{id_paciente:03d}"


def cor_prioridade(prioridade):
    if prioridade == "Emergência":
        return "#ef4444"

    if prioridade == "Urgente":
        return "#f6b000"

    return "#22c55e"


class PainelEspera:
    def __init__(self, janela_principal):
        self.janela_principal = janela_principal
        self.token_chamada = 0
        self.overlay_chamada = None

        self.janela = ctk.CTkToplevel(janela_principal)
        self.janela.title("Painel da Sala de Espera")
        self.janela.configure(fg_color=COR_FUNDO)

        self.posicionar_no_segundo_monitor()
        self.montar_tela()
        self.atualizar_lista()

    def posicionar_no_segundo_monitor(self):
        monitores = get_monitors()

        if len(monitores) >= 2:
            monitor = monitores[1]
        else:
            monitor = monitores[0]

        self.janela.geometry(
            f"{monitor.width}x{monitor.height}"
            f"+{monitor.x}+{monitor.y}"
        )

    def montar_tela(self):
        cabecalho = ctk.CTkFrame(
            self.janela,
            height=120,
            fg_color="#020617",
            corner_radius=0
        )
        cabecalho.pack(fill="x")
        cabecalho.pack_propagate(False)

        ctk.CTkLabel(
            cabecalho,
            text="PAINEL DE ATENDIMENTO",
            font=("Arial", 34, "bold"),
            text_color=COR_TEXTO
        ).pack(pady=(22, 2))

        ctk.CTkLabel(
            cabecalho,
            text="Acompanhe sua posição e aguarde ser chamado",
            font=("Arial", 18),
            text_color=COR_TEXTO_SUAVE
        ).pack()

        self.area_lista = ctk.CTkScrollableFrame(
            self.janela,
            fg_color=COR_FUNDO,
            corner_radius=0
        )
        self.area_lista.pack(
            fill="both",
            expand=True,
            padx=40,
            pady=25
        )

        self.rodape = ctk.CTkLabel(
            self.janela,
            text="",
            height=50,
            font=("Arial", 15),
            text_color=COR_TEXTO_SUAVE
        )
        self.rodape.pack(fill="x")

    def obter_pacientes_aguardando(self):
        pacientes = []

        for paciente in buscar_pacientes_fila():
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
                prioridade,
                cor_prioridade_db,
                justificativa,
                data_chegada,
                status,
                data_finalizacao
            ) = paciente

            if (status or "AGUARDANDO") != "AGUARDANDO":
                continue

            prioridade = prioridade or "Pouco Urgente"

            pacientes.append({
                "id": id_paciente,
                "codigo": gerar_codigo(id_paciente, prioridade),
                "nome": nome,
                "idade": idade,
                "prioridade": prioridade
            })

        pacientes.sort(
            key=lambda paciente: (
                ordem_prioridade(paciente["prioridade"]),
                paciente["id"]
            )
        )

        return pacientes

    def atualizar_lista(self):
        if not self.janela.winfo_exists():
            return

        for widget in self.area_lista.winfo_children():
            widget.destroy()

        pacientes = self.obter_pacientes_aguardando()

        if not pacientes:
            ctk.CTkLabel(
                self.area_lista,
                text="Nenhum paciente aguardando atendimento.",
                font=("Arial", 28, "bold"),
                text_color=COR_TEXTO_SUAVE
            ).pack(expand=True, pady=100)

        for posicao, paciente in enumerate(pacientes, start=1):
            card = ctk.CTkFrame(
                self.area_lista,
                height=100,
                fg_color=COR_CARD,
                corner_radius=15
            )
            card.pack(fill="x", pady=7)
            card.pack_propagate(False)

            ctk.CTkLabel(
                card,
                text=str(posicao),
                width=80,
                font=("Arial", 30, "bold"),
                text_color=COR_TEXTO
            ).pack(side="left", padx=20)

            ctk.CTkLabel(
                card,
                text=paciente["codigo"],
                width=130,
                font=("Consolas", 24, "bold"),
                text_color="#60a5fa"
            ).pack(side="left")

            bloco_nome = ctk.CTkFrame(card, fg_color="transparent")
            bloco_nome.pack(
                side="left",
                fill="both",
                expand=True,
                padx=20,
                pady=15
            )

            ctk.CTkLabel(
                bloco_nome,
                text=paciente["nome"],
                font=("Arial", 24, "bold"),
                text_color=COR_TEXTO
            ).pack(anchor="w")

            ctk.CTkLabel(
                bloco_nome,
                text=f"{paciente['idade']} anos",
                font=("Arial", 15),
                text_color=COR_TEXTO_SUAVE
            ).pack(anchor="w")

            if posicao == 1:
                previsao = "PRÓXIMO PACIENTE"
            else:
                minutos = (posicao - 1) * TEMPO_MEDIO_ATENDIMENTO
                previsao = f"Previsão aproximada: {minutos} min"

            ctk.CTkLabel(
                card,
                text=previsao,
                width=290,
                font=("Arial", 18, "bold"),
                text_color=cor_prioridade(paciente["prioridade"])
            ).pack(side="right", padx=25)

        horario = datetime.now().strftime("%H:%M:%S")

        self.rodape.configure(
            text=(
                f"{len(pacientes)} paciente(s) aguardando  •  "
                f"Atualizado às {horario}  •  "
                "A ordem pode mudar conforme a prioridade clínica"
            )
        )

        self.janela.after(3000, self.atualizar_lista)

    def chamar_paciente(self, paciente, duracao=60):
        self.token_chamada += 1
        token_atual = self.token_chamada

        self.janela.deiconify()
        self.janela.lift()

        if self.overlay_chamada is not None:
            self.overlay_chamada.destroy()

        prioridade = paciente["prioridade"]
        cor = cor_prioridade(prioridade)

        self.overlay_chamada = ctk.CTkFrame(
            self.janela,
            fg_color=COR_FUNDO,
            corner_radius=0
        )
        self.overlay_chamada.place(
            relx=0,
            rely=0,
            relwidth=1,
            relheight=1
        )

        def voltar_para_fila(event=None):
            self.encerrar_chamada(token_atual)

        botao_fechar = ctk.CTkButton(
            self.overlay_chamada,
            text="✕  Voltar para a fila  (ESC)",
            width=230,
            height=48,
            corner_radius=10,
            fg_color="#334155",
            hover_color="#475569",
            text_color="#ffffff",
            font=("Arial", 14, "bold"),
            command=voltar_para_fila
        )

        botao_fechar.place(
            relx=0.98,
            rely=0.03,
            anchor="ne"
        )

        self.janela.bind("<Escape>", voltar_para_fila)
        self.janela.focus_force()

        ctk.CTkLabel(
            self.overlay_chamada,
            text="PACIENTE CHAMADO",
            font=("Arial", 38, "bold"),
            text_color="#facc15"
        ).pack(pady=(80, 25))

        ctk.CTkLabel(
            self.overlay_chamada,
            text=paciente["nome"].upper(),
            font=("Arial", 64, "bold"),
            text_color=COR_TEXTO,
            wraplength=1200
        ).pack(pady=20)

        ctk.CTkLabel(
            self.overlay_chamada,
            text=paciente["codigo"],
            font=("Consolas", 72, "bold"),
            text_color=cor
        ).pack(pady=15)

        ctk.CTkLabel(
            self.overlay_chamada,
            text="DIRIJA-SE À SALA DE ATENDIMENTO",
            font=("Arial", 34, "bold"),
            text_color=COR_TEXTO
        ).pack(pady=35)

        ctk.CTkLabel(
            self.overlay_chamada,
            text=f"Prioridade: {prioridade}",
            font=("Arial", 22),
            text_color=COR_TEXTO_SUAVE
        ).pack()

        self.iniciar_som(token_atual)

        self.janela.after(
            duracao * 1000,
            lambda: self.encerrar_chamada(token_atual)
        )

    def iniciar_som(self, token):
        if token != self.token_chamada:
            return

        if winsound:
            threading.Thread(
                target=self.executar_bipes,
                daemon=True
            ).start()
        else:
            self.janela.bell()

        self.janela.after(
            2000,
            lambda: self.iniciar_som(token)
        )

    @staticmethod
    def executar_bipes():
        winsound.Beep(1200, 350)
        time.sleep(0.15)
        winsound.Beep(1200, 350)

    def encerrar_chamada(self, token):
        if token != self.token_chamada:
            return

        self.token_chamada += 1

        try:
            self.janela.unbind("<Escape>")
        except Exception:
            pass

        if self.overlay_chamada is not None:
            self.overlay_chamada.destroy()
            self.overlay_chamada = None

        self.atualizar_lista()