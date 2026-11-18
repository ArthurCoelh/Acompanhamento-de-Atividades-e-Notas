# Acompanhamento de Atividades e Notas

![Logo Acompanhamento de Atividades e Notas](./caminho/para/sua/imagem.jpg)

# Sobre
O Acompanhamento de Atividades e Notas é uma aplicação inteligente desenvolvida com o suporte do GitHub Copilot. Além de organizar tarefas acadêmicas, prazos e notas ponderadas, o projeto integra prompts e fluxos assistidos por IA para ajudar estudantes a otimizarem seus cronogramas de estudo e anteciparem necessidades de reforço escolar.
# 📚 Breve Resumo

> Sistema desenvolvido para centralizar o controle acadêmico, eliminar a redundância de planilhas e otimizar a visualização de prazos, entregas e desempenho escolar/universitário.

---

## 🚀 Sobre o Projeto

O **Acompanhamento de Atividades e Notas** nasceu da necessidade de criar uma solução prática e eficiente para o gerenciamento da vida acadêmica. O projeto foca em organizar o fluxo de tarefas, trabalhos e avaliações, permitindo um acompanhamento transparente e ágil do progresso nas disciplinas.

---

## ✨ Funcionalidades Principais

* **Gestão de Disciplinas:** Cadastro e organização de matérias por período/semestre.
* **Controle de Atividades:** Acompanhamento de tarefas pendentes, em andamento e concluídas.
* **Registro de Notas:** Lançamento e cálculo automatizado de médias e desempenho parcial.
* **Persistência de Dados:** Operações completas de CRUD via banco de dados relacional.
* **Interface Intuitiva:** Foco na agilidade de consulta e experiência do usuário.

---

## 📊 Tabela

### 1. Mapeamento de Telas e Componentes

| Seção / Aba | Componentes Principais | Funcionalidades |
| :--- | :--- | :--- |
| **Painel** | Banner de boas-vindas (`Olá, João`), 4 Cards de Resumo (`Disciplinas`, `Atividades em aberto`, `Próximo prazo`, `Disciplinas em alerta`), `Desempenho por disciplina`, `Próximos prazos` e `Sugestões de estudo` | Exibe visão geral do semestre, barras de progresso de notas, tabela cronológica de entregas e recomendações automáticas de estudo. |
| **Disciplinas** | Formulário de cadastro (`Disciplina`, `Período`, `Média mínima`), Tabela de disciplinas cadastradas e seção `incluir ou excluir` | Permite adicionar novas matérias com suas respectivas médias de corte e gerenciar registros existentes. |
| **Atividades e notas** | Seletor de disciplina, 3 Cards de Indicadores (`Média parcial`, `Nota necessária`, `Situação`), Tabela de atividades, Formulário de nova atividade e `incluir ou excluir` | Calcula médias em tempo real, lista tarefas com prazos/pesos/notas e permite cadastrar ou avaliar atividades. |

---

### 2. Regras de Negócio e Estados de Situação

| Estado / Indicador | Condição / Lógica Aplicada | Comportamento na Interface |
| :--- | :--- | :--- |
| **Sem notas** | Nenhuma atividade da disciplina possui nota lançada (`Status: Pendente`) | `Média parcial` exibe `—`; `Nota necessária` exibe o valor da média mínima (`6,0`); card de sugestão orienta a priorizar a próxima entrega. |
| **Aprovado** | `Média parcial >= Média mínima` (ex: Compiladores com `8,0 >= 6,0` ou IA com `(9,0 + 3,0) / 2 = 6,0`) | `Nota necessária` exibe `—`; badge verde `Aprovado` é exibido; sugestão recomenda revisão leve e foco nas demais matérias. |
| **Reprovado** | Todas as atividades concluídas e `Média parcial < Média mínima` (ex: IA com `(9,0 + 2,0) / 2 = 5,5 < 6,0`) | `Situação` exibe `Reprovado`; `Nota necessária` exibe `—`. |
| **Próximos 7 dias** | Atividades pendentes com vencimento em até 7 dias a partir da data atual (`18/11/2026`) | Destaca alertas no topo de `Sugestões de estudo` listando as tarefas urgentes. |

---

### 3. Dados de Exemplo (Seed / Testes — Período `2026.2`)

| Disciplina | Período | Média Mínima | Atividade | Descrição | Prazo | Peso | Status | Nota (Cenários) |
| :--- | :---: | :---: | :--- | :--- | :---: | :---: | :---: | :---: |
| **Compiladores** | 2026.2 | 6,0 | Atividade 1 – Análise Léxica e Sintática | Compreender como um compilador identificar os tokens e verificar a estrutura sintática de um programa. | 23/11/2026 | 1,00 | Pendente | `—` |
| **Compiladores** | 2026.2 | 6,0 | Atividade 2 – Construção de um Analisador Léxico Simples | Desenvolver um pequeno programa capaz de refletir os principais elementos de uma linguagem de programação. | 27/11/2026 | 1,00 | Pendente | `—` |
| **Inteligência artificial** | 2026.2 | 6,0 | Atividade 1 – Fundamentos da Inteligência Artificial | Compreender os conceitos fundamentais da Inteligência Artificial e suas aplicações na sociedade. | 24/11/2026 | 1,00 | Concluída | `9,0` |
| **Inteligência artificial** | 2026.2 | 6,0 | Atividade 2 – Criando uma Inteligência Artificial na Prática | Explorar o funcionamento de uma aplicação de Inteligência Artificial e compreender como ela pode resolver problemas reais. | 26/11/2026 | 1,00 | Concluída | `3,0` (Aprovado) / `2,0` (Reprovado) |

---

## Estrutura do Site / Projeto

| Arquitetura / Componente | Descrição / Elementos |
| :--- | :--- |
| **Painel Acadêmico** | Visão geral com cartões de resumo (disciplinas, atividades em aberto, próximos prazos, alertas), desempenho por disciplina, próximos prazos cronológicos e sugestões de estudo[cite: 1, 6]. |
| **Gestão de Disciplinas** | Cadastro de matérias informando período letivo (ex: `2026.2`) e média mínima exigida (`6,0`). |
| **Gestão de Atividades e Notas** | Listagem de tarefas por disciplina com descrição, prazos, pesos, status (`Pendente` / `Concluída`) e notas parciais para cálculo automático de aprovação. |
| **Barra Lateral e Perfil** | Configurações de tema (claro/escuro e cores), seletor de alunos ativos (ex: `João (#1)`) e opções de cadastro/exclusão de perfis. |

![WhatsApp Image 2026-11-18 at 00.33.59 (1).jpeg](assets/print.png)

---

## 🛠️ Tecnologias e Ferramentas

Este projeto foi construído utilizando as seguintes tecnologias:

* **Linguagem:** Python 🐍
* **Banco de Dados:** SQL (SQLite / MySQL)
* **Interface Gráfica (Desktop):** Tkinter
* **Controle de Versão:** Git & GitHub

---

## ⚙️ Arquitetura do Banco de Dados (Schema)

O sistema utiliza um modelo relacional estruturado para garantir a integridade dos dados acadêmicos. As principais entidades englobam:
1. **Alunos/Usuários:** Informações básicas de cadastro.
2. **Disciplinas:** Matérias cursadas no período.
3. **Atividades/Avaliações:** Prazos, pesos, descrições e status de entrega.
4. **Notas:** Vínculo direto entre avaliações e o aproveitamento obtido.

---

## 👥 Colaboradores

- **Cauã Paiva**
- **Arthur Ferreira**
- **Josielly Macedo**
