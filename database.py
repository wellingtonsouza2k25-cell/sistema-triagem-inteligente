import sqlite3
from datetime import datetime
from zoneinfo import ZoneInfo

conexao = sqlite3.connect("pacientes.db")
cursor = conexao.cursor()

FUSO_BRASILIA = ZoneInfo("America/Sao_Paulo")


def agora_brasilia_iso():
    return datetime.now(FUSO_BRASILIA).isoformat()


def gerar_codigo_atendimento(id_paciente, prioridade):
    """Gera um código estável a partir do ID e da classificação da triagem."""
    if prioridade == "Emergência":
        prefixo = "E"
    elif prioridade == "Urgente":
        prefixo = "U"
    else:
        prefixo = "P"

    return f"{prefixo}-{int(id_paciente):03d}"


def adicionar_coluna_se_nao_existir(nome_coluna, tipo):
    cursor.execute("PRAGMA table_info(pacientes)")
    colunas = cursor.fetchall()

    nomes_colunas = []

    for coluna in colunas:
        nomes_colunas.append(coluna[1])

    if nome_coluna not in nomes_colunas:
        cursor.execute(f"ALTER TABLE pacientes ADD COLUMN {nome_coluna} {tipo}")
        conexao.commit()


def criar_tabela():
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pacientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        idade TEXT,
        genero TEXT,
        documento TEXT,
        telefone TEXT,
        sintomas TEXT,
        descricao_livre TEXT,
        sinais_fisicos TEXT,
        observacoes TEXT,
        prioridade_ia TEXT,
        cor_prioridade TEXT,
        justificativa_ia TEXT,
        data_hora_chegada TEXT, 
        status TEXT,
        data_hora_finalizacao TEXT
    )
    """)

    conexao.commit()

    adicionar_coluna_se_nao_existir("sintomas", "TEXT")
    adicionar_coluna_se_nao_existir("descricao_livre", "TEXT")
    adicionar_coluna_se_nao_existir("sinais_fisicos", "TEXT")
    adicionar_coluna_se_nao_existir("observacoes", "TEXT")
    adicionar_coluna_se_nao_existir("prioridade_ia", "TEXT")
    adicionar_coluna_se_nao_existir("cor_prioridade", "TEXT")
    adicionar_coluna_se_nao_existir("justificativa_ia", "TEXT")
    adicionar_coluna_se_nao_existir("data_hora_chegada", "TEXT")
    adicionar_coluna_se_nao_existir("status", "TEXT")
    adicionar_coluna_se_nao_existir("data_hora_finalizacao", "TEXT")


def salvar_paciente_db(
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
    data_hora_chegada=None,
    status="AGUARDANDO"
):
    if data_hora_chegada is None:
        data_hora_chegada = agora_brasilia_iso()

    
    cursor.execute("""
    INSERT INTO pacientes (
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
        status
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
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
        status
    ))

    conexao.commit()

    id_paciente = cursor.lastrowid
    return {
        "id": id_paciente,
        "codigo": gerar_codigo_atendimento(id_paciente, prioridade_ia)
    }

def buscar_pacientes_fila():
    cursor.execute("""
    SELECT
        id,
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
    FROM pacientes
    ORDER BY id DESC
    """)

    return cursor.fetchall()


def buscar_pacientes():
    cursor.execute("""
    SELECT
        id,
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
    FROM pacientes
    ORDER BY id DESC
    """)

    return cursor.fetchall()

def deletar_paciente_db(id_paciente):
    cursor.execute("DELETE FROM pacientes WHERE id = ?", (id_paciente,))
    conexao.commit()

def atualizar_status_paciente(id_paciente, novo_status):
    if novo_status == "FINALIZADO":
        cursor.execute("""
        UPDATE pacientes
        SET status = ?, data_hora_finalizacao = ?
        WHERE id = ?
        """, (novo_status, agora_brasilia_iso(), id_paciente))

    else:
        cursor.execute("""
        UPDATE pacientes
        SET status = ?
        WHERE id = ?
        """, (novo_status, id_paciente))

    conexao.commit()

