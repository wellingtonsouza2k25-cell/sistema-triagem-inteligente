# Documentação de Endpoints — Sistema de Triagem Inteligente

## 1. Objetivo

Este documento descreve as rotas planejadas para a API REST da versão web do Sistema de Triagem Inteligente.

As rotas abaixo representam o planejamento inicial. Elas deverão ser ajustadas conforme a tecnologia escolhida e a implementação realizada.

## 2. Cadastro e consulta de pacientes

| Método | Rota | Entrada | Resposta esperada | Erros possíveis |
|---|---|---|---|---|
| POST | /pacientes | Nome, idade e demais dados definidos para o cadastro | 201 — Paciente cadastrado | 400 — Dados inválidos |
| GET | /pacientes | Nenhuma | 200 — Lista de pacientes | 500 — Erro interno |
| GET | /pacientes/{id} | Identificador do paciente na rota | 200 — Dados do paciente | 404 — Paciente não encontrado |

## 3. Registro de sintomas e atendimentos

| Método | Rota | Entrada | Resposta esperada | Erros possíveis |
|---|---|---|---|---|
| POST | /atendimentos | Identificador do paciente e sintomas relatados | 201 — Atendimento registrado | 400 — Dados inválidos; 404 — Paciente não encontrado |
| GET | /atendimentos | Filtros opcionais | 200 — Lista de atendimentos e respectivos status | 500 — Erro interno |

## 4. Sugestão de prioridade pela IA

| Método | Rota | Entrada | Resposta esperada | Erros possíveis |
|---|---|---|---|---|
| POST | /atendimentos/{id}/sugerir-prioridade | Identificador do atendimento | 200 — Sugestão de prioridade e resultado da análise | 404 — Atendimento não encontrado; 503 — Serviço de IA indisponível |

A prioridade retornada pela IA é apenas uma sugestão de apoio. Ela deverá ser avaliada por um profissional responsável e não substituirá a avaliação clínica.

## 5. Atualização do status

| Método | Rota | Entrada | Resposta esperada | Erros possíveis |
|---|---|---|---|---|
| PATCH | /atendimentos/{id}/status | Novo status do atendimento | 200 — Status atualizado | 400 — Status inválido; 404 — Atendimento não encontrado |

## 6. Observações

- As rotas são propostas para o planejamento e ainda precisam ser implementadas e testadas.
- Os códigos de resposta descritos são os resultados esperados.
- Os campos definitivos de entrada deverão corresponder ao modelo de dados do projeto.
- Os testes deverão utilizar dados fictícios.
- A implementação deverá tratar erros sem classificar automaticamente um paciente como pouco urgente quando a IA estiver indisponível.
