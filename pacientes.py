import customtkinter as ctk

from database import buscar_pacientes


def abrir_janela_pacientes(janela):
    pacientes = buscar_pacientes()

    janela_pacientes = ctk.CTkToplevel(janela)
    janela_pacientes.title("Pacientes Salvos")
    janela_pacientes.geometry("750x500")
    janela_pacientes.configure(fg_color="#242424")

    titulo = ctk.CTkLabel(
        janela_pacientes,
        text="Pacientes Salvos",
        font=("Arial", 22, "bold"),
        text_color="white"
    )
    titulo.pack(pady=15)

    caixa = ctk.CTkTextbox(
        janela_pacientes,
        width=700,
        height=400,
        corner_radius=12,
        fg_color="#1f1f1f",
        text_color="white",
        font=("Arial", 14)
    )
    caixa.pack(padx=20, pady=10)

    if len(pacientes) == 0:
        caixa.insert("end", "Nenhum paciente salvo ainda.")
    else:
        for paciente in pacientes:
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
                justificativa_ia
            ) = paciente

            texto = f"""
        ID: {id_paciente}
        Nome: {nome}
        Idade: {idade}
        Gênero: {genero}
        Documento: {documento}
        Telefone: {telefone}

        Sintomas selecionados:
        {sintomas}

        Descrição livre:
        {descricao_livre}

        Sinais físicos:
        {sinais_fisicos}

        Observações:
        {observacoes}

        Classificação da IA:
        {prioridade_ia} - {cor_prioridade}

        Justificativa da IA:
        {justificativa_ia}

        ----------------------------------------

        """
            caixa.insert("end", texto)