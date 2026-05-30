# 🤖 MASPy Code Generator — Sistema Multiagentes com RAG

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-Framework-1C3C3C?style=for-the-badge&logo=chainlink&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector%20Store-FF6B35?style=for-the-badge)
![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-000000?style=for-the-badge)
![License](https://img.shields.io/badge/Licença-MIT-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Em%20Desenvolvimento-yellow?style=for-the-badge)

**Iniciação Científica — Geração automática de código MASPy via RAG e arquitetura multiagentes**

</div>

---

## 📖 Sobre o Projeto

Este projeto é desenvolvido no contexto de uma **Iniciação Científica (IC)** e propõe um sistema inteligente capaz de **gerar código MASPy automaticamente** a partir de descrições em linguagem natural.

O sistema combina duas abordagens modernas de IA:

- **RAG (Retrieval-Augmented Generation):** recupera exemplos reais de código MASPy de um banco vetorial (ChromaDB) para embasar e guiar a geração.
- **Arquitetura Multiagentes:** diferentes agentes especializados colaboram no pipeline — um agente gerador, um agente revisor e um motor de pós-processamento — garantindo que o código produzido seja funcional e aderente à sintaxe da framework.

> **MASPy** é um framework Python para programação de Sistemas Multiagentes (SMA), com conceitos de agentes BDI (Beliefs, Desires, Intentions), planos, crenças, objetivos e comunicação entre agentes.

---

## 🏗️ Arquitetura

```
Pergunta em linguagem natural
          │
          ▼
┌─────────────────────┐
│   MaspyEntityRetriever  │  ←── ChromaDB (banco vetorial de exemplos MASPy)
│  (Busca semântica)  │        Embeddings: BGE-M3 (multilíngue)
└─────────┬───────────┘
          │  k=3 documentos mais relevantes
          ▼
┌─────────────────────┐
│   Agente Gerador    │  ←── LLM: qwen2.5-coder:7b (via Ollama)
│  (Code Generator)  │
└─────────┬───────────┘
          │  código gerado
          ▼
┌─────────────────────┐
│   Agente Revisor    │  ←── LLM: llama3 (via Ollama)
│   (Code Reviewer)  │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│   MaspySanitizer    │  Pipeline de pós-processamento e correção automática
└─────────┬───────────┘
          │
          ▼
    Código MASPy final
```

---

## ✨ Funcionalidades

- 🔍 **Recuperação semântica** de exemplos MASPy via ChromaDB + embeddings multilíngues (BGE-M3)
- 🧠 **Detecção de intenção** na pergunta do usuário (Planos, Agentes, Comunicação, Crenças/Objetivos)
- ⚙️ **Pipeline multiagente**: Gerador → Revisor → Sanitizador
- 🛠️ **Motor de pós-processamento** (`MaspySanitizer`) que corrige automaticamente alucinações do LLM:
  - Limpeza de imports inválidos
  - Deduplicação de blocos `__main__`
  - Correção de assinaturas de planos
  - Sincronização de nomes de instâncias
  - Correção de alvos de `send` e canais indevidos
- 🗃️ **Ingestão de código-fonte** MASPy para criação do banco vetorial
- 🖥️ Interface de chat via **frontend** dedicado
- 🔒 **Blacklist** de arquivos irrelevantes para o domínio de comunicação entre agentes

---

## 🛠️ Tecnologias

| Tecnologia | Uso |
|---|---|
| **Python 3.10+** | Linguagem principal |
| **LangChain** | Orquestração do pipeline RAG e agentes |
| **ChromaDB** | Banco de dados vetorial (armazenamento dos embeddings) |
| **Ollama** | Execução local dos LLMs |
| **qwen2.5-coder:7b** | Modelo de geração de código |
| **llama3** | Modelo revisor |
| **BGE-M3** | Modelo de embeddings multilíngue (PT ↔ EN) |
| **tree-sitter** | Parser de código para análise sintática |

---

## 📁 Estrutura do Projeto

```
IC/
├── backend/
│   ├── requirements.txt          # Dependências do projeto
│   └── service/
│       ├── config.py             # Configurações (modelos, caminhos, URLs)
│       ├── domain.py             # Entidades do domínio MASPy e detecção de intenção
│       ├── retriever.py          # MaspyEntityRetriever (busca semântica customizada)
│       ├── chat.py               # Pipeline principal: geração, revisão e sanitização
│       ├── ingest.py             # Ingestão de exemplos MASPy no banco vetorial
│       └── ...
├── frontend/
│   └── ...                       # Interface de usuário (chat)
├── embedding/
│   ├── chroma_db/                # Banco vetorial (gerado pela ingestão)
│   └── doc_store/                # Documentos pai (gerados pela ingestão)
└── codigos_maspy/
    └── examples/                 # Exemplos de código MASPy (base de conhecimento)
```

---

## 🚀 Como Executar

### Pré-requisitos

- Python 3.10 ou superior
- [Ollama](https://ollama.com/) instalado e rodando localmente
- Modelos Ollama necessários:

```bash
ollama pull qwen2.5-coder:7b
ollama pull llama3
ollama pull bge-m3
```

### 1. Clone o repositório

```bash
git clone https://github.com/nataliamendesgoes/IC.git
cd IC
```

### 2. Instale as dependências

```bash
cd backend
pip install -r requirements.txt
```

### 3. Execute a ingestão dos exemplos MASPy

Este passo cria o banco vetorial a partir dos exemplos de código:

```bash
python -m service.ingest
```

### 4. Inicie o servidor Ollama

```bash
ollama serve
```

> Por padrão, o Ollama roda em `http://127.0.0.1:11434`

### 5. Execute o sistema

```bash
python -m service.chat
```

---

## ⚙️ Configuração

Edite `backend/service/config.py` para ajustar os modelos e caminhos:

```python
# Modelo de geração de código
LLM_MODEL = "qwen2.5-coder:7b"

# Modelo revisor (pode usar um modelo mais potente)
REVISOR_MODEL = "llama3"

# Modelo de embeddings multilíngue
EMBEDDING_MODEL = "bge-m3"

# URL do servidor Ollama
OLLAMA_BASE_URL = "http://127.0.0.1:11434"
```

---

## 🧪 Exemplos de Uso

O sistema aceita perguntas em português ou inglês sobre MASPy:

```
> Crie um agente que envia uma mensagem para outro agente ao receber uma crença.

> Create two agents that negotiate using the contract-net protocol.

> Como fazer um agente com um plano que reage a um objetivo?
```

---

## 📚 Sobre o MASPy

[MASPy](https://github.com/your-maspy-link) é um framework para desenvolvimento de Sistemas Multiagentes em Python. Os principais conceitos suportados são:

| Conceito | Descrição |
|---|---|
| `Agent` | Classe base para criação de agentes |
| `Plan` (`@pl`) | Decorator para definição de planos reativos |
| `Belief` | Crenças do agente (estado mental) |
| `Goal` | Objetivos do agente |
| `send` | Envio de mensagens entre agentes |


---

## 👩‍💻 Autora

Desenvolvido por **Natalia Mendes Goes** como parte de uma Iniciação Científica.

<div align="center">

[![GitHub](https://img.shields.io/badge/GitHub-nataliamendesgoes-181717?style=for-the-badge&logo=github)](https://github.com/nataliamendesgoes)

</div>
