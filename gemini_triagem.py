import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()


def avaliar_triagem_gemini(sintomas, descricao_livre, sinais_fisicos, observacoes):
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return {
            "prioridade": "Pouco Urgente",
            "cor": "Verde",
            "justificativa": "A chave da API Gemini não foi configurada. Classificação automática padrão aplicada."
        }

    client = genai.Client(api_key=api_key)

    prompt = f"""
Você é uma IA de apoio à triagem hospitalar.

Sua função é analisar apenas as informações fornecidas e sugerir o grau de prioridade do atendimento.

Você NÃO deve:
- Dar diagnóstico médico.
- Indicar medicamentos ou tratamentos.
- Substituir a avaliação de um profissional de saúde.
- Inventar sintomas ou informações que não foram fornecidas.

Classifique obrigatoriamente em apenas uma destas opções:
- Emergência
- Urgente
- Pouco Urgente

CRITÉRIOS DE CLASSIFICAÇÃO

1. EMERGÊNCIA — COR VERMELHA

Classifique como Emergência somente quando houver indicação clara de risco imediato à vida ou instabilidade grave, como:

- Inconsciência ou dificuldade para acordar.
- Desmaio atual ou repetido acompanhado de sinais graves.
- Falta de ar intensa ou incapacidade de falar normalmente.
- Dor no peito acompanhada de falta de ar, suor frio, desmaio ou alteração de consciência.
- Sangramento intenso ou que não para.
- Convulsão.
- Confusão mental grave.
- Sinais evidentes de choque ou deterioração rápida.
- Qualquer informação que demonstre risco imediato à vida.

Não classifique como Emergência apenas porque aparecem palavras como “forte” ou “intensa”.

2. URGENTE — COR AMARELA

Classifique como Urgente quando os sintomas forem importantes e precisarem de atendimento rápido, mas o paciente estiver consciente, respirando normalmente e sem indicação clara de risco imediato à vida.

Exemplos:

- Dor abdominal forte ou intensa, mas paciente consciente e estável.
- Febre alta persistente.
- Vômitos repetidos, sem perda de consciência.
- Dor forte que dificulta as atividades.
- Ferimento com sangramento controlado.
- Dor de cabeça forte sem alteração de consciência.
- Sintomas que estão piorando, mas sem sinais de instabilidade grave.
- Combinação de sintomas moderados ou importantes.

Um sintoma intenso não deve ser classificado automaticamente como Emergência quando não houver sinal claro de risco imediato.

3. POUCO URGENTE — COR VERDE

Classifique como Pouco Urgente quando os sintomas forem leves, estáveis e sem sinais de agravamento.

Exemplos:

- Coriza.
- Tosse leve.
- Dor de garganta leve.
- Dor de cabeça leve.
- Sintomas de resfriado.
- Pequenas dores sem piora.
- Paciente consciente, comunicativo e sem dificuldade respiratória.

REGRAS IMPORTANTES

1. Analise somente as informações fornecidas.
2. Não presuma que existe risco imediato sem evidências no texto.
3. A presença da palavra “forte” ou “intensa” não é suficiente para classificar como Emergência.
4. Para classificar como Emergência, deve existir pelo menos um sinal claro de risco imediato.
5. Quando o paciente apresentar sintomas importantes, mas estiver consciente, orientado, respirando normalmente e sem sinais graves, classifique como Urgente.
6. Quando os sintomas forem leves e estáveis, classifique como Pouco Urgente.
7. Se houver sintomas de níveis diferentes, utilize o maior nível que esteja claramente comprovado pelas informações.
8. A prioridade e a cor devem corresponder exatamente:
   - Emergência = Vermelho
   - Urgente = Amarelo
   - Pouco Urgente = Verde

DADOS DO PACIENTE

Sintomas selecionados:
{sintomas}

Descrição livre do caso:
{descricao_livre}

Sinais físicos observados:
{sinais_fisicos}

Observações adicionais:
{observacoes}

Responda somente com um JSON válido, sem texto antes ou depois:

{{
  "prioridade": "Emergência",
  "cor": "Vermelho",
  "justificativa": "Explicação objetiva baseada somente nas informações fornecidas."
}}

O campo "prioridade" deve conter exatamente um destes valores:
"Emergência", "Urgente" ou "Pouco Urgente".

O campo "cor" deve conter exatamente um destes valores:
"Vermelho", "Amarelo" ou "Verde".
"""

    try:
        resposta = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )

        dados = json.loads(resposta.text)

        prioridade = dados.get("prioridade", "Pouco Urgente")
        cor = dados.get("cor", "Verde")
        justificativa = dados.get("justificativa", "Classificação gerada pela IA.")

        return {
            "prioridade": prioridade,
            "cor": cor,
            "justificativa": justificativa
        }

    except Exception as erro:
        return {
            "prioridade": "Pouco Urgente",
            "cor": "Verde",
            "justificativa": f"Não foi possível consultar o Gemini. Classificação padrão aplicada. Erro: {erro}"
        }