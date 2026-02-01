import sys
import os

# Correção de importação para garantir que achamos o config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain.storage import LocalFileStore
from langchain_chroma import Chroma
from langchain.retrievers import ParentDocumentRetriever
from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import OllamaEmbeddings
from langchain.chains import RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter, Language
from langchain.prompts import PromptTemplate

from rag.config import EMBEDDING_DIR, DOCSTORE_DIR, LLM_MODEL, EMBEDDING_MODEL, OLLAMA_BASE_URL

def carregar_sistema_rag():
    print("Conectando ao banco de dados...")
    
    # 1. Carregar o mesmo Embedding usado na ingestão
    embedding_model = OllamaEmbeddings(
        model=EMBEDDING_MODEL,
        base_url=OLLAMA_BASE_URL
    )
    
    # 2. Carregar VectorStore persistido
    vectorstore = Chroma(
        collection_name="maspy_codes",
        embedding_function=embedding_model,
        persist_directory=EMBEDDING_DIR
    )
    
    # 3. Carregar DocStore persistido
    fs_store = LocalFileStore(DOCSTORE_DIR)
    
    # 4. Recriar o Retriever
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
    # Verifica se o banco existe antes de começar
    if not os.path.exists(EMBEDDING_DIR) or not os.listdir(EMBEDDING_DIR):
        print("ERRO: Banco de dados não encontrado.")
        print("Por favor, execute 'python rag/ingest.py' primeiro.")
        return

    retriever = carregar_sistema_rag()
    
    print(f"Iniciando modelo de chat: {LLM_MODEL}...")
    llm = ChatOllama(
        model=LLM_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=0, # Temperatura 0 para respostas técnicas e precisas
    )
    
    # --- PROMPT PERSONALIZADO PARA MASPY ---
    template = """
    Você é um especialista no framework Python chamado 'MASPY' (Multi-Agent System).
    
    Sua tarefa é responder perguntas sobre implementação e conceitos do MASPY.
    Use estritamente os trechos de código fornecidos abaixo como contexto para formular sua resposta.
    
    Se o contexto contiver código, use-o como exemplo na sua explicação.
    Se você não souber a resposta com base no contexto, diga honestamente que não sabe.
    
    CONTEXTO RECUPERADO:
    {context}
    
    PERGUNTA DO USUÁRIO: 
    {question}
    
    RESPOSTA (Em Português, com exemplos de código em Python):
    """
    
    QA_CHAIN_PROMPT = PromptTemplate.from_template(template)

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": QA_CHAIN_PROMPT}
    )
    
    print("\n" + "="*40)
    print(f" ASSISTENTE MASPY - ({LLM_MODEL} + {EMBEDDING_MODEL})")
    print(" Digite 'sair' para encerrar.")
    print("="*40)
    
    while True:
        query = input("\nNatália > ")
        if query.lower() in ["sair", "exit", "quit"]:
            break
        
        print(f"🔍 Buscando nos códigos com {EMBEDDING_MODEL} e gerando resposta...")
        
        try:
            resposta = qa_chain.invoke({"query": query})
            
            print(f"\n🤖 CodeLlama:\n{resposta['result']}")
            
            # Exibir metadados (quais arquivos foram usados)
            if resposta['source_documents']:
                print("\n" + "-"*30)
                print("📚 Fontes consultadas:")
                fontes_unicas = set()
                for doc in resposta['source_documents']:
                    caminho_arquivo = doc.metadata.get('source', 'Desconhecido')
                    # Simplifica o caminho para ficar legível
                    nome_arquivo = os.path.basename(caminho_arquivo)
                    fontes_unicas.add(nome_arquivo)
                
                for fonte in fontes_unicas:
                    print(f"   • {fonte}")
                print("-"*30)
                
        except Exception as e:
            print(f"\n❌ Ocorreu um erro: {e}")

if __name__ == "__main__":
    main()