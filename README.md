# 📚 Acompanhamento de Atividades e Notas

Aplicação para centralizar o controle acadêmico: disciplinas por período, atividades com prazo e peso, notas e desempenho parcial — sem planilhas. Desenvolvida com apoio do **GitHub Copilot** (veja `.github/copilot-instructions.md`).

## ✨ Funcionalidades
- **Gestão de disciplinas** por período/semestre, com média mínima configurável.
- **Controle de atividades**: pendente, em andamento e concluída, com prazo e peso.
- **Registro de notas** com média ponderada automática e **nota necessária** nas avaliações restantes.
- **Painel de desempenho**: cabeçalho de boas-vindas, cartões por disciplina com barra de média parcial (marca na média mínima) e situação por cor (Aprovado, No caminho, Atenção, Em risco, Reprovado), próximos prazos e sugestões de estudo/reforço.
- **CRUD completo** persistido em banco relacional (SQLite).
- **Temas (versão web)**: padrão *Azul*, além de Preto e branco, Verde, Roxo, Rosa e cor personalizada, cada um em **modo claro e escuro**, escolhidos na barra lateral.
- **Sugestões de estudo** para todas as disciplinas (não só as em alerta), com atrasos e prazos da semana.

## 📚 Tabela

> **Critério de Aprovação:** Nota mínima `6.0` por disciplina.

| Disciplina | Atividade | Tipo | Data de Entrega | Status | Peso | Nota |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| Compiladores | Análise Léxica e Sintática | Projeto | 23/11/2026 | ⏳ Em andamento | 3.0 | - |
| Compiladores | Lista de Gramáticas Livres de Contexto | Lista | 30/11/2026 | 📅 Pendente | 2.0 | - |
| Inteligência Artificial | Algoritmos de Busca (A* e Heurísticas) | Trabalho | 26/11/2026 | 📅 Pendente | 2.5 | - |
| Inteligência Artificial | Redes Neurais e Classificação | Projeto | 04/12/2026 | 📅 Pendente | 2.5 | - |

### 📊 Painel de Indicadores
* **Atividades em Aberto:** `4`
* **Disciplinas em Alerta (Nota < 6.0):** `0`
* **Próximo Prazo:** `23/11/2026` *(Compiladores - Análise Léxica e Sintática)*
* **Nota Mínima Exigida:** `6.0`
* **Legenda de Status:** ✅ Concluído | ⏳ Em andamento | 📅 Pendente | ⚠️ Atrasado

## 🛠️ Tecnologias
Python 3.10+ · Streamlit · Pandas · SQLite · Tkinter (versão desktop) · Git & GitHub

## ▶️ Como executar
```bash
git clone https://github.com/josiellycosta/Acompanhamento.git
cd Acompanhamento
pip install -r requirements.txt
streamlit run streamlit_app.py
```
No Linux, se faltar o Tkinter: `sudo apt install python3-tk`. O banco `academico.db` é criado automaticamente na primeira execução.


## 🌐 Versão web (Streamlit)
A versão web roda no navegador (`streamlit_app.py`) e compartilha as regras de cálculo e a camada SQLite com a versão desktop.

**No seu computador**
```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

**Dentro do GitHub (Codespaces)** — Code → Codespaces → *Create codespace on main*. O ambiente instala tudo e abre o app sozinho (porta 8501).

**Publicar online (Streamlit Community Cloud)** — em [share.streamlit.io](https://share.streamlit.io) escolha este repositório e o arquivo `streamlit_app.py`.

> ⚠️ O GitHub Pages não executa Python. No Streamlit Community Cloud, o armazenamento local não deve ser tratado como permanente: o arquivo `academico.db` pode ser perdido quando o ambiente for recriado. Para uso contínuo online, configure um banco externo persistente (por exemplo, PostgreSQL). Esta versão não possui autenticação: não publique dados acadêmicos pessoais em um app público. No computador e no Codespace, os dados ficam no arquivo local `academico.db`.

## 🧪 Testes
```bash
python -m unittest discover -s tests -t . -v
```

## ⚙️ Esquema do banco
| Tabela | Campos principais |
|---|---|
| `alunos` | id, nome, email |
| `disciplinas` | id, aluno_id → alunos, nome, periodo, media_minima |
| `atividades` | id, disciplina_id → disciplinas, titulo, descricao, prazo, peso, status |
| `notas` | id, atividade_id → atividades (única), valor (0–10) |

Todas as relações usam `ON DELETE CASCADE`.

## 🧮 Regras de cálculo
- **Média parcial** = Σ(nota × peso) ÷ Σ(peso das atividades já avaliadas).
- **Nota necessária** = (média mínima × Σ peso total − Σ pontos obtidos) ÷ Σ peso das atividades sem nota.
- Os pesos de todas as atividades cadastradas formam o total da disciplina; cadastre todas as avaliações previstas para a projeção ficar correta.
- **Em risco**: nota necessária > 10 · **Atenção**: nota necessária > 8 ou média parcial abaixo da mínima.

## 📁 Estrutura
```
main.py        ponto de entrada
ui.py          interface desktop (Tkinter)
streamlit_app.py  interface web (Streamlit, com temas claro/escuro)
.streamlit/config.toml  tema base (Azul)
database.py    esquema e CRUD (SQLite)
calculos.py    médias, nota necessária e situação
tests/         testes unitários
.github/       CI (Actions) e instruções do Copilot
```
