import sys
import os
import pickle

# Adiciona raiz ao path para encontrar config.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# --- IMPORTAÇÕES DE PARCEIROS ---
from langchain_chroma import Chroma
try:
    from langchain_ollama import ChatOllama, OllamaEmbeddings
except ImportError:
    from langchain_community.chat_models import ChatOllama
    from langchain_community.embeddings import OllamaEmbeddings

# --- IMPORTAÇÕES CORE E UTILS ---
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from rag.config import EMBEDDING_DIR, DOCSTORE_DIR, LLM_MODEL, EMBEDDING_MODEL, OLLAMA_BASE_URL

def carregar_sistema():
    # 1. Embeddings
    embedding_model = OllamaEmbeddings(
        model=EMBEDDING_MODEL,
        base_url=OLLAMA_BASE_URL
    )
    
    # 2. Vector Store
    vectorstore = Chroma(
        collection_name="maspy_codes",
        embedding_function=embedding_model,
        persist_directory=EMBEDDING_DIR
    )
    
    # 3. Simple retriever from vectorstore
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    
    return retriever

def main():
    if not os.path.exists(EMBEDDING_DIR):
        print("ERRO: Execute o ingest.py primeiro.")
        return

    print(f"Carregando {LLM_MODEL}...")
    llm = ChatOllama(
        model=LLM_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=0,
    )
    
    retriever = carregar_sistema()
    
    template = """
    Você é um especialista em Python e no framework MASPY.
    Responda à pergunta com base APENAS no contexto abaixo.
    Se houver código no contexto, use-o como exemplo.

    Contexto:
    {context}

    Pergunta: {question}
    """
    
    prompt = PromptTemplate.from_template(template)
    
    # Modern RAG chain using LCEL (LangChain Expression Language)
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)
    
    qa_chain = (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough()
        }
        | prompt
        | llm
        | StrOutputParser()
    )
    
    print("--- Chat Iniciado (Digite 'sair' para fechar) ---")
    while True:
        query = input("\nVocê: ")
        if query.lower() in ["sair", "exit"]:
            break
        
        try:
            result = qa_chain.invoke(query)
            print(f"\nAI: {result}")
            
            # Get source documents
            docs = retriever.invoke(query)
            if docs:
                src = docs[0].metadata.get('source', 'Desconhecido')
                print(f"[Fonte: {os.path.basename(src)}]")
        except Exception as e:
            print(f"Erro: {e}")

if __name__ == "__main__":
    main()