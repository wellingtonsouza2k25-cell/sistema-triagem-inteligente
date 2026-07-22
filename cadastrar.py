from tkinter import messagebox

from componentes import criar_label, campo_com_label, select_com_label, criar_botao
from database import salvar_paciente_db
from gemini_triagem import avaliar_triagem_gemini


def criar_tela_cadastro(janela, campos_sintomas=None, campos_textos=None):
    titulo = criar_label(
        janela,
        "Dados de Admissão Básica",
        tamanho=20,
        icone="imagens/user.png"
    )
    titulo.grid(row=0, column=0, sticky="w", padx=15, pady=(10, 0))

    linha_1 = criar_linha(janela, 1, pady=(10, 0))
    linha_2 = criar_linha(janela, 2, pady=(20, 0))

    bloco_nome, campo_nome = campo_com_label(
        linha_1,
        "NOME COMPLETO DO PACIENTE",
        "Ex: João da Silva Santos",
        300
    )
    bloco_nome.pack(side="left", padx=(10, 25))

    bloco_idade, campo_idade = campo_com_label(
        linha_1,
        "IDADE",
        "Ex: 34",
        120
    )
    bloco_idade.pack(side="left", padx=(0, 25))

    bloco_genero, campo_sexo = select_com_label(
        linha_1,
        "GÊNERO",
        170
    )
    bloco_genero.pack(side="left", padx=(0, 0))

    bloco_documento, campo_identificacao = campo_com_label(
        linha_2,
        "DOCUMENTO / IDENTIFICAÇÃO (CPF/RG)",
        "000.000.000-00",
        300
    )
    bloco_documento.pack(side="left", padx=(10, 25))

    bloco_telefone, campo_contato = campo_com_label(
        linha_2,
        "TELEFONE DE CONTATO",
        "(83) 98888-7777",
        300
    )
    bloco_telefone.pack(side="left", padx=(0, 25))

    def salvar_paciente():
        nome = campo_nome.get().strip()
        idade = campo_idade.get().strip()
        genero = campo_sexo.get().strip()
        documento = campo_identificacao.get().strip()
        telefone = campo_contato.get().strip()

        sintomas = ""

        if campos_sintomas:
            sintomas = ", ".join(campos_sintomas["sintomas_selecionados"])

        descricao_livre = ""
        sinais_fisicos = ""
        observacoes = ""

        if campos_textos:
            descricao_livre = campos_textos["campo_descricao"].get("1.0", "end").strip()
            sinais_fisicos = campos_textos["campo_sinais"].get("1.0", "end").strip()
            observacoes = campos_textos["campo_observacoes"].get("1.0", "end").strip()

            if descricao_livre == campos_textos["placeholder_descricao"]:
                descricao_livre = ""

            if sinais_fisicos == campos_textos["placeholder_sinais"]:
                sinais_fisicos = ""

            if observacoes == campos_textos["placeholder_observacoes"]:
                observacoes = ""

        if nome == "":
            messagebox.showerror("Erro", "Digite o nome do paciente.")
            return

        if idade == "":
            messagebox.showerror("Erro", "Digite a idade do paciente.")
            return
        
        resultado_ia = avaliar_triagem_gemini(
            sintomas,
            descricao_livre,
            sinais_fisicos,
            observacoes
        )

        prioridade_ia = resultado_ia["prioridade"]
        cor_prioridade = resultado_ia["cor"]
        justificativa_ia = resultado_ia["justificativa"]

        registro_salvo = salvar_paciente_db(
            nome, idade, genero, documento, telefone, sintomas,
            descricao_livre, sinais_fisicos, observacoes,
            prioridade_ia, cor_prioridade, justificativa_ia
        )
        codigo_atendimento = registro_salvo["codigo"]

        messagebox.showinfo(
            "Paciente salvo com IA",
            f"Paciente salvo com sucesso!\n\n"
            f"CÓDIGO DE ATENDIMENTO: {codigo_atendimento}\n\n"
            f"Classificação da IA: {prioridade_ia} - {cor_prioridade}\n\n"
            f"Justificativa:\n{justificativa_ia}"
        )

        campo_nome.delete(0, "end")
        campo_idade.delete(0, "end")
        campo_identificacao.delete(0, "end")
        campo_contato.delete(0, "end")
        campo_sexo.set("Masculino")

    botao_salvar = criar_botao(
        janela,
        "Salvar Informações",
        salvar_paciente,
    )
    botao_salvar.grid(row=9, column=0, padx=15, pady=(25, 5))


def criar_linha(janela, linha, pady):
    import customtkinter as ctk

    frame = ctk.CTkFrame(janela, fg_color="transparent")
    frame.grid(row=linha, column=0, sticky="w", padx=5, pady=pady)

    return frame