import sys
import os

# Fix para encoding UTF-8 no Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Adiciona raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ==============================================================================
# 1. IMPORTAÇÕES CORRIGIDAS
# ==============================================================================

# A. Armazenamento (compatibilidade com várias versões)
try:
    from langchain.storage import LocalFileStore
except Exception:
    try:
        from langchain.storage.file_system import LocalFileStore
    except Exception:
        try:
            from langchain.document_stores import LocalFileStore
        except Exception:
            try:
                from langchain_community.storage import LocalFileStore
            except Exception:
                LocalFileStore = None

# B. Chains e Memória (Requer 'pip install langchain')
# Nota: Versões modernas de langchain removeram ConversationalRetrievalChain
# Usaremos abordagem manual com histórico em memória
ConversationalRetrievalChain = None
ConversationBufferMemory = None

# C. Integrações (Chroma e Ollama)
try:
    from langchain_chroma import Chroma
except Exception:
    try:
        from langchain_community.vectorstores import Chroma
    except Exception:
        try:
            from langchain.vectorstores import Chroma
        except Exception:
            Chroma = None

try:
    from langchain_ollama import OllamaLLM as ChatOllama, OllamaEmbeddings
except Exception:
    try:
        from langchain_community.llms import Ollama as ChatOllama
        from langchain_community.embeddings import OllamaEmbeddings
    except Exception:
        try:
            from langchain.llms import Ollama as ChatOllama  # type: ignore
            from langchain.embeddings import OllamaEmbeddings
        except Exception:
            ChatOllama = None
            OllamaEmbeddings = None

# D. Core e Utils
try:
    from langchain.retrievers import ParentDocumentRetriever
except Exception:
    try:
        from langchain_community.retrievers import ParentDocumentRetriever
    except Exception:
        ParentDocumentRetriever = None

try:
    from langchain.storage import LocalFileStore
except Exception:
    try:
        from langchain_community.storage import LocalFileStore
    except Exception:
        try:
            from langchain.storage.file_system import LocalFileStore
        except Exception:
            LocalFileStore = None

try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter, Language
except Exception:
    try:
        from langchain_text_splitters import RecursiveCharacterTextSplitter, Language
    except Exception:
        RecursiveCharacterTextSplitter = None
        Language = None

try:
    from langchain.prompts import PromptTemplate
except Exception:
    try:
        from langchain_core.prompts import PromptTemplate
    except Exception:
        PromptTemplate = None

# E. Retriever Customizado (Se existir)
try:
    from rag.retriever import MaspyEntityRetriever
    USAR_CUSTOM = True
except ImportError:
    USAR_CUSTOM = False

# Configurações
from rag.config import (
    EMBEDDING_DIR, DOCSTORE_DIR, LLM_MODEL, EMBEDDING_MODEL, OLLAMA_BASE_URL
)

# ==============================================================================
# 2. PROMPTS MASPY
# ==============================================================================

MASPY_CONDENSE_PROMPT = """
Reescreva a pergunta a seguir para ser uma frase independente, mantendo o contexto de programação em MASPY.
Histórico: {chat_history}
Pergunta: {question}
Pergunta Reformulada:"""

MASPY_QA_PROMPT = """
Você é o ESPECIALISTA TÉCNICO sênior do framework MASPY.
Sua missão é gerar código Python FUNCIONAL e ARQUITETURALMENTE CORRETO.

REGRAS RÍGIDAS DE ARQUITETURA (BDI):
1. **Planos (@pl):** Toda lógica de execução DEVE estar em um método decorado com `@pl`.
   A assinatura é `@pl(change, data)`.
   - Você DEVE passar 2 argumentos posicionais.
   - ✅ CORRETO (Objetivo): `@pl(gain, Goal("nome"))`
   - ✅ CORRETO (Crença):   `@pl(gain, Belief("nome"))`
   - 🚫 ERRADO: `@pl(trigger=...)`, `@pl(gain=...)` ou `@pl(Goal(...))` (falta o change).
2. **Ciclo de Vida (__init__):** - O `__init__` serve APENAS para `self.add_belief(...)` ou `self.add_goal(...)`.
   - 🚫 PROIBIDO: NUNCA coloque `self.print()`, `self.send()` ou lógica de execução dentro do `__init__`. O agente ainda não está rodando!
3. **Sintaxe:** Use `self.print()` (não print) e herde de `Agent`.
4. **Inicialização:** Sempre mostre o `Admin().start_system()` no final.
5. **Consistência de Gatilho:** Se você criar um plano com `@pl(trigger=Goal("X"))`, você OBRIGATORIAMENTE deve adicionar `self.add_goal(Goal("X"))` no `__init__`. Caso contrário, o plano nunca roda.

CONTEXTO RECUPERADO:
{context}

HISTÓRICO:
{chat_history}

PERGUNTA DO USUÁRIO: {question}

RESPOSTA (Código + Breve Explicação):
"""
# ==============================================================================
# 3. SISTEMA
# ==============================================================================

def carregar_sistema():
    print(f"   ... Conectando ao Banco Vetorial ...")
    # Verificações rápidas de disponibilidade de dependências importadas
    missing = []
    if OllamaEmbeddings is None:
        missing.append("OllamaEmbeddings")
    if Chroma is None:
        missing.append("Chroma")
    if RecursiveCharacterTextSplitter is None or Language is None:
        missing.append("text splitter (RecursiveCharacterTextSplitter/Language)")

    if missing:
        raise Exception(
            "Dependências ausentes: " + ", ".join(missing) + ".\n"
            "Verifique sua instalação/versões do langchain e integrações (langchain-chroma, langchain-ollama)."
        )

    embedding_model = OllamaEmbeddings(
        model=EMBEDDING_MODEL,
        base_url=OLLAMA_BASE_URL
    )

    vectorstore = Chroma(
        collection_name="maspy_codes",
        embedding_function=embedding_model,
        persist_directory=EMBEDDING_DIR
    )
    
    # Lógica de seleção do Retriever
    if USAR_CUSTOM:
        print("   Using: MaspyEntityRetriever 🚀")
        retriever = MaspyEntityRetriever(
            vectorstore=vectorstore,
            search_kwargs={"k": 5}
        )
    else:
        print("   Using: Standard Similarity Retriever 📁")
        # Se ParentDocumentRetriever não estiver disponível, usar retriever simples
        if ParentDocumentRetriever is None or LocalFileStore is None:
            print("   ⚠️ ParentDocumentRetriever não disponível, usando similarity search direto")
            retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
        else:
            fs_store = LocalFileStore(DOCSTORE_DIR)
            child_splitter = RecursiveCharacterTextSplitter.from_language(
                Language.PYTHON, chunk_size=400, chunk_overlap=50
            )
            retriever = ParentDocumentRetriever(
                vectorstore=vectorstore,
                docstore=fs_store,
                child_splitter=child_splitter, 
                parent_splitter=None
            )
        
    return retriever

def main():
    if not os.path.exists(EMBEDDING_DIR):
        print("❌ ERRO: Banco de dados não encontrado.")
        print("   Execute: python rag/ingest.py")
        return

    print("="*60)
    print(f"🔧 MASPY CHAT ({LLM_MODEL})")
    print("="*60)

    llm = ChatOllama(
        model=LLM_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=0.1,
    )
    
    try:
        retriever = carregar_sistema()
    except Exception as e:
        print(f"❌ Erro crítico ao carregar sistema: {e}")
        print("💡 DICA: Rode 'pip install -U langchain' se o erro for de importação.")
        return
    
    if ConversationBufferMemory is None:
        print("ℹ️  Usando implementação manual de conversação (ConversationalRetrievalChain não disponível)")

    condense_prompt = PromptTemplate.from_template(MASPY_CONDENSE_PROMPT)
    qa_prompt = PromptTemplate(
        template=MASPY_QA_PROMPT,
        input_variables=["context", "chat_history", "question"]
    )

    qa_chain = None  # Será tratado especialmente no loop
    
    print("\n✅ PRONTO. Digite 'sair'.")
    
    chat_history_list = []
    
    while True:
        query = input("\n[MASPY] > ")
        if query.lower() in ["sair", "exit"]: break
            
        print("🔍 Buscando...")
        try:
            if qa_chain is not None:
                # Usar ConversationalRetrievalChain se disponível
                result = qa_chain.invoke({"question": query})
                print(f"\n💡: {result['answer']}")
                source_documents = result.get('source_documents', [])
            else:
                # Fallback: implementação manual simples
                # Usar o método correto do retriever (invoke ao invés de get_relevant_documents)
                try:
                    docs = retriever.invoke(query)
                except:
                    # Se invoke não funcionar, tentar get_relevant_documents
                    try:
                        docs = retriever.get_relevant_documents(query)
                    except:
                        # Último recurso: usar similarity_search do vectorstore
                        docs = retriever.vectorstore.similarity_search(query, k=5)
                
                context = "\n\n".join([doc.page_content for doc in docs])
                
                # Formatar histórico de conversação
                history_text = ""
                if chat_history_list:
                    history_text = "\n".join([f"U: {q}\nA: {a}" for q, a in chat_history_list[-3:]])
                
                # Criar prompt manualmente
                final_prompt = qa_prompt.format(
                    context=context,
                    chat_history=history_text,
                    question=query
                )
                
                # Chamar LLM
                response = llm.invoke(final_prompt)
                answer = response.content if hasattr(response, 'content') else str(response)
                print(f"\n💡: {answer}")
                
                # Salvar no histórico
                chat_history_list.append((query, answer))
                source_documents = docs
            
            if source_documents:
                print("\n📂 Fontes:")
                for doc in source_documents:
                    meta = doc.metadata
                    name = os.path.basename(meta.get('source', 'Desconhecido'))
                    extra = meta.get('maspy_entities', '')
                    print(f"   - {name} {f'[{extra}]' if extra else ''}")

        except Exception as e:
            print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()