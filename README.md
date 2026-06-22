# 🤖 MASPY Code Generator

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-Framework-1C3C3C?style=for-the-badge&logo=chainlink&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector%20Store-FF6B35?style=for-the-badge)
![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-000000?style=for-the-badge)
![Next.js](https://img.shields.io/badge/Next.js-Frontend-000000?style=for-the-badge&logo=next.js&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Status](https://img.shields.io/badge/Status-Em%20Desenvolvimento-yellow?style=for-the-badge)

**Iniciação Científica — Geração automática de código MASPy via arquitetura multiagentes com RAG**

</div>

---

## 📖 Sobre o Projeto

Este projeto é desenvolvido como parte de uma **Iniciação Científica (IC)** e tem como objetivo gerar código [MASPy](https://github.com/laca-is/maspy) automaticamente a partir de descrições em linguagem natural.

O sistema combina duas abordagens:

- **RAG (Retrieval-Augmented Generation):** recupera exemplos reais de código MASPy armazenados em um banco vetorial (ChromaDB) para embasar a geração.
- **Arquitetura Multiagentes:** três agentes LLM especializados colaboram em pipeline — Arquiteto, Integrador e Revisor — garantindo que o código gerado seja funcional e aderente à API do MASPy.

> **MASPy** é um framework Python para programação de Sistemas Multiagentes (SMA) com conceitos BDI (Beliefs, Desires, Intentions): agentes, planos reativos, crenças, objetivos e comunicação entre agentes.

---

## 🏗️ Arquitetura do Pipeline

```
Pergunta em linguagem natural
          │
          ▼
┌─────────────────────────┐
│   MaspyEntityRetriever  │  ← ChromaDB + Embeddings BGE-M3
│   (Busca Semântica)     │    Detecta intenção e seleciona k=3 exemplos
└──────────┬──────────────┘
           │ contexto RAG
           ▼
┌─────────────────────────┐
│   Agente Arquiteto      │  ← LLM: qwen2.5-coder:7b
│   (Gera as classes)     │    Define agentes, ambientes, planos e crenças
└──────────┬──────────────┘
           │ classes BDI
           ▼
┌─────────────────────────┐
│   Agente Integrador     │  ← LLM: qwen2.5-coder:7b
│   (Monta o __main__)    │    Instancia agentes e conecta a topologia
└──────────┬──────────────┘
           │ código combinado
           ▼
┌─────────────────────────┐
│   Agente Revisor        │  ← LLM: llama3
│   (Audita o código)     │    Verifica construtores, ciclos, API e topologia
└──────────┬──────────────┘
           │ código revisado
           ▼
┌─────────────────────────┐
│   MaspySanitizer        │    Pipeline de pós-processamento com 15 correções
│   (Pós-processamento)   │    automáticas para alucinações do LLM
└──────────┬──────────────┘
           │
           ▼
    Código MASPy final
```

---

## ✨ Funcionalidades

- 🔍 **Busca semântica** de exemplos MASPy via ChromaDB + embeddings multilíngues (BGE-M3)
- 🧠 **Detecção automática de intenção** na pergunta (Agent, Communication, Belief/Goal, Environment)
- ⚙️ **Pipeline de 3 agentes LLM**: Arquiteto → Integrador → Revisor
- 🛠️ **MaspySanitizer** com 15 correções automáticas de alucinações do LLM:
  - Limpeza de imports inválidos
  - Consolidação de blocos `__main__` duplicados
  - Correção de assinaturas de planos `@pl` (injeta `src` e `*args`)
  - Sincronização de nomes de instâncias
  - Correção de alvos de `self.send()`
  - Remoção de canais indevidos
  - Impedimento de envios BDI para Ambientes
  - Mapeamento de métodos incorretos (`remove` → `rm`, `add_belief` → `add`)
  - Correção de ações de ambiente encadeadas
  - Injeção de `stop_cycle()` ausente
  - Correção de `Belief`/`Percept` com argumentos errados
  - Injeção automática de `__init__` e crenças ausentes (V5.1)
  - Limpeza de instâncias órfãs
  - Reordenamento topológico no `connect_to`
  - Garantia de `Admin().start_system()` como última linha
- 🖥️ **Interface web** com chat via Next.js + FastAPI
- 💬 **Sugestões de exemplos** prontos para testar
- 📋 **Botão de copiar** o código gerado
- 🟢 **Status da API** em tempo real no frontend

---

## 🛠️ Tecnologias

| Tecnologia | Versão | Uso |
|---|---|---|
| **Python** | 3.10+ | Linguagem principal |
| **LangChain** | latest | Orquestração do pipeline RAG |
| **ChromaDB** | latest | Banco de dados vetorial |
| **Ollama** | latest | Execução local dos LLMs |
| **qwen2.5-coder:7b** | — | Agentes Arquiteto e Integrador |
| **llama3** | — | Agente Revisor |
| **BGE-M3** | — | Embeddings multilíngues (PT ↔ EN) |
| **tree-sitter** | latest | Parser de código |
| **FastAPI** | latest | API REST do backend |
| **Next.js** | 14+ | Interface web |
| **TypeScript** | 5+ | Tipagem do frontend |

---

## 📁 Estrutura do Projeto

```
IC/
├── backend/
│   ├── service/
│   │   ├── config.py         # Modelos, caminhos e URLs (edite aqui)
│   │   ├── domain.py         # Entidades MASPy e detecção de intenção
│   │   ├── retriever.py      # MaspyEntityRetriever (busca semântica)
│   │   ├── chat.py           # Pipeline principal + MaspySanitizer
│   │   └── ingest.py         # Ingestão de exemplos no banco vetorial
│   ├── main.py               # Servidor FastAPI (API REST)
│   ├── requirements.txt      # Dependências Python
│   └── .env.example
│
├── frontend/
│   └── chat_rag/             # Projeto Next.js
│       ├── app/
│       │   ├── layout.tsx    # Layout raiz com fontes IBM Plex
│       │   ├── page.tsx      # Página principal
│       │   └── globals.css   # Estilos globais
│       ├── components/
│       │   ├── ChatPage.tsx      # Layout do chat (sidebar + mensagens)
│       │   ├── Message.tsx       # Bolha de mensagem com syntax highlight
│       │   ├── ChatInput.tsx     # Input com auto-resize
│       │   └── TypingIndicator.tsx
│       ├── hooks/
│       │   └── useChat.ts    # Estado do chat
│       ├── lib/
│       │   └── api.ts        # Chamadas REST ao backend
│       └── .env.local        # NEXT_PUBLIC_API_URL
│
├── embedding/
│   ├── chroma_db/            # Banco vetorial (gerado pela ingestão)
│   └── doc_store/            # Documentos pai
│
├── codigos_maspy/
│   └── examples/             # Exemplos de código MASPy (base de conhecimento)
│
└── README.md
```

---

## 🚀 Instalação e Configuração

### Pré-requisitos

- [Python 3.12.10](https://www.python.org/downloads/release/python-31210/) — versão exata recomendada
- [Node.js 18+](https://nodejs.org/)
- [Ollama](https://ollama.com/) instalado

> ⚠️ **Atenção:** use exatamente o Python 3.12.10. Outras versões podem causar incompatibilidades com as dependências do projeto.

### 1. Clone o repositório

```bash
git clone https://github.com/nataliamendesgoes/IC.git
cd IC
```

### 2. Instale os modelos no Ollama

```bash
ollama pull qwen2.5-coder:7b
ollama pull llama3
ollama pull bge-m3
```

### 3. Crie e ative o ambiente virtual

O ambiente virtual isola as dependências do projeto do restante do sistema.

**Windows:**
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
```

**Linux/macOS:**
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
```

> Após ativar, o terminal mostrará `(.venv)` no início da linha. Para desativar quando quiser, use `deactivate`.

### 4. Instale as dependências do backend

Com o ambiente virtual ativo:

```bash
pip install -r requirements.txt
```

Verifique as configurações em `backend/service/config.py`:

```python
LLM_MODEL      = "qwen2.5-coder:7b"   # Agentes Arquiteto e Integrador
REVISOR_MODEL  = "llama3"             # Agente Revisor
EMBEDDING_MODEL = "bge-m3"            # Embeddings
OLLAMA_BASE_URL = "http://127.0.0.1:11434"
```

### 5. Execute a ingestão dos exemplos MASPy

Este passo cria o banco vetorial a partir dos exemplos em `codigos_maspy/examples/`. **Execute apenas uma vez** (ou sempre que adicionar novos exemplos).

```bash
cd IC
python -m backend.service.ingest
```

### 6. Configure o frontend

```bash
cd frontend/chat_rag
npm install
npm install react-markdown remark-gfm react-syntax-highlighter @types/react-syntax-highlighter
```

Crie o arquivo `frontend/chat_rag/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## ▶️ Como Rodar

Abra **2 terminais** na raiz do projeto:

**Terminal 1 — Backend (FastAPI)**
```bash
cd IC
uvicorn backend.main:app --reload --port 8000
```

**Terminal 2 — Frontend (Next.js)**
```bash
cd IC/frontend/chat_rag
npm run dev
```

Acesse **http://localhost:3000** no navegador.

> ⚠️ **Ordem importa:** suba o Ollama primeiro, depois o backend, depois o frontend.

---

## 💡 Como Usar

Na interface web, descreva em português o sistema multiagente que você quer criar. Exemplos:

```
Crie dois agentes que se comunicam via mensagem

Agente com plano reativo a um objetivo específico

Sistema de negociação com contract-net protocol

Agente que monitora um ambiente e reage a percepções
```

Ou use direto pelo terminal (sem o frontend):

```bash
cd IC
python -m backend.service.chat
```

---

## 🧪 Exemplo de Output

**Entrada:**
```
Crie dois agentes que se comunicam via mensagem
```

**Saída gerada:**
```python

from maspy import *

class Sender(Agent):
    def __init__(self, agt_name):
        super().__init__(agt_name)
        self.add(Goal("send_message", Any))

    @pl(gain, Goal("send_message", Any))
    def send_message(self, src, *args):
        self.send("Receiver_1", achieve, Goal("receive_message", "Hello!"))

class Receiver(Agent):
    def __init__(self, agt_name):
        super().__init__(agt_name)

    @pl(gain, Goal("receive_message", Any))
    def receive_message(self, src, message, *args):
        self.print(f"Mensagem recebida de {src}: {message}")
        self.stop_cycle()

if __name__ == "__main__":
    Admin().console_settings(True)
    sender = Sender("Sender")
    receiver = Receiver("Receiver")
    Admin().connect_to([sender, receiver], [Channel()])
    Admin().start_system()
```

---

## 📚 Sobre o MASPy

Os principais conceitos do MASPy usados na geração:

| Conceito | Sintaxe | Descrição |
|---|---|---|
| Agente | `class X(Agent):` | Unidade autônoma com planos e crenças |
| Plano | `@pl(gain, Goal(...))` | Comportamento reativo a eventos |
| Crença | `Belief("nome", valor)` | Estado mental do agente |
| Objetivo | `Goal("nome", valor)` | Meta a ser alcançada |
| Comunicação | `self.send("Alvo_1", achieve, Goal(...))` | Mensagem entre agentes |
| Ambiente | `class Y(Environment):` | Entidade não-autônoma com percepções |
| Ação | `self.action("Env").metodo(self.my_name)` | Agente age sobre o ambiente |
| Percepção | `Percept("nome", valor)` | Estado do ambiente percebido pelo agente |

---


<!-- ## 👩‍💻 Autora

Desenvolvido por **Natalia Mendes Goes** como Iniciação Científica.

<div align="center">

[![GitHub](https://img.shields.io/badge/GitHub-nataliamendesgoes-181717?style=for-the-badge&logo=github)](https://github.com/nataliamendesgoes)

</div>
-->
