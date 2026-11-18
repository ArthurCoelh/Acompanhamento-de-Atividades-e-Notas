# Acompanhamento-de-Atividades-e-Notas
O Acompanhamento de Atividades e Notas é uma aplicação inteligente desenvolvida com o suporte do GitHub Copilot. Além de organizar tarefas acadêmicas, prazos e notas ponderadas, o projeto integra prompts e fluxos assistidos por IA para ajudar estudantes a otimizarem seus cronogramas de estudo e anteciparem necessidades de reforço escolar.
# 📚 Acompanhamento de Atividades e Notas

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

## 📚 Tabela

| Disciplina / Módulo | Atividade | Tipo | Data de Entrega | Status | Peso | Nota |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| Engenharia de Software | Levantamento de Requisitos | Trabalho | 10/11/2026 | ✅ Concluído | 2.0 | 9.5 |
| Banco de Dados | Modelagem ER e Normalização | Lista | 18/11/2026 | ⏳ Em andamento | 1.5 | - |
| Estrutura de Dados | Implementação de Árvores | Projeto | 25/11/2026 | 📅 Pendente | 3.0 | - |
| Arquitetura de Computadores | Avaliação Bimestral | Prova | 02/12/2026 | 📅 Pendente | 3.5 | - |

### 📊 Resumo de Desempenho
* **Média Parcial:** `9.5`
* **Atividades Concluídas:** `1 / 4`
* **Legenda de Status:** ✅ Concluído | ⏳ Em andamento | 📅 Pendente | ⚠️ Atrasado

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
