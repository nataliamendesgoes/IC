import os
import shutil
from langchain.storage import LocalFileStore
from langchain_chroma import Chroma
from langchain.retrievers import ParentDocumentRetriever
from langchain.text_splitter import RecursiveCharacterTextSplitter, Language
from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers import LanguageParser
from langchain_community.embeddings import OllamaEmbeddings

# Importa configurações do seu arquivo config.py
from config import SOURCE_DIR, EMBEDDING_DIR, DOCSTORE_DIR, EMBEDDING_MODEL, OLLAMA_BASE_URL

def main():
    print(f"--- INICIANDO INGESTÃO DE DADOS ---")
    print(f"Lendo arquivos de: {SOURCE_DIR}")
    
    # 1. Carregar arquivos Python
    loader = GenericLoader.from_filesystem(
        SOURCE_DIR,
        glob="**/*",
        suffixes=[".py"],
        parser=LanguageParser(language=Language.PYTHON, parser_threshold=500),
    )
    original_docs = loader.load()
    print(f"Total de arquivos encontrados: {len(original_docs)}")

    # 2. Limpar banco antigo (Para evitar duplicatas ou conflito de modelos)
    if os.path.exists(EMBEDDING_DIR):
        print("Removendo banco vetorial antigo...")
        shutil.rmtree(EMBEDDING_DIR)
    
    if os.path.exists(DOCSTORE_DIR):
        print("Removendo docstore antigo...")
        shutil.rmtree(DOCSTORE_DIR)

    # 3. Configurar o Modelo de Embedding (BGE-M3)
    print(f"Carregando modelo de embedding: {EMBEDDING_MODEL}")
    embedding_model = OllamaEmbeddings(
        model=EMBEDDING_MODEL,
        base_url=OLLAMA_BASE_URL
    )

    # 4. Inicializar Bancos de Dados
    # VectorStore: Guarda os vetores dos 'Filhos' (chunks pequenos)
    vectorstore = Chroma(
        collection_name="maspy_codes",
        embedding_function=embedding_model,
        persist_directory=EMBEDDING_DIR
    )
    
    # DocStore: Guarda o texto dos 'Pais' (código completo)
    # Usamos LocalFileStore para persistir no disco
    fs_store = LocalFileStore(DOCSTORE_DIR)

    # 5. Configurar Splitters (A Estratégia Parent/Child)
    
    # Splitter FILHO: Pedaços pequenos para busca precisa
    child_splitter = RecursiveCharacterTextSplitter.from_language(
        language=Language.PYTHON, 
        chunk_size=400, 
        chunk_overlap=50
    )
    
    # Splitter PAI: Pedaços grandes (Classes/Funções inteiras) para contexto do LLM
    parent_splitter = RecursiveCharacterTextSplitter.from_language(
        language=Language.PYTHON, 
        chunk_size=2000, 
        chunk_overlap=0
    )

    # 6. Criar o Retriever e Indexar
    retriever = ParentDocumentRetriever(
        vectorstore=vectorstore,
        docstore=fs_store,
        child_splitter=child_splitter,
        parent_splitter=parent_splitter,
    )

    print("Processando documentos e criando vetores (isso pode demorar dependendo da qtd de arquivos)...")
    retriever.add_documents(original_docs, ids=None)
    
    print("--- SUCESSO! ---")
    print(f"Banco vetorial salvo em: {EMBEDDING_DIR}")
    print(f"Documentos pais salvos em: {DOCSTORE_DIR}")

if __name__ == "__main__":
    main()