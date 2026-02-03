import os
import shutil
import pickle

# --- IMPORTAÇÕES DE ARMAZENAMENTO E VECTORSTORE ---
from langchain_chroma import Chroma

# --- IMPORTAÇÕES DE EMBEDDINGS ---
try:
    from langchain_ollama import OllamaEmbeddings
except ImportError:
    from langchain_community.embeddings import OllamaEmbeddings

# --- IMPORTAÇÕES DE TEXTO E SPLITTERS ---
from langchain_text_splitters import RecursiveCharacterTextSplitter, Language

# --- IMPORTAÇÕES DE LOADERS ---
from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers import LanguageParser

# --- CONFIGURAÇÃO LOCAL ---
from config import SOURCE_DIR, EMBEDDING_DIR, DOCSTORE_DIR, EMBEDDING_MODEL, OLLAMA_BASE_URL

def main():
    print(f"--- INICIANDO INGESTÃO (Modular) ---")
    
    # 1. Carregar arquivos
    loader = GenericLoader.from_filesystem(
        SOURCE_DIR,
        glob="**/*",
        suffixes=[".py"],
        parser=LanguageParser(language=Language.PYTHON, parser_threshold=500),
    )
    original_docs = loader.load()
    print(f"Arquivos carregados: {len(original_docs)}")

    # 2. Limpeza
    if os.path.exists(EMBEDDING_DIR):
        shutil.rmtree(EMBEDDING_DIR)
    if os.path.exists(DOCSTORE_DIR):
        shutil.rmtree(DOCSTORE_DIR)
    
    os.makedirs(EMBEDDING_DIR, exist_ok=True)
    os.makedirs(DOCSTORE_DIR, exist_ok=True)

    # 3. Embeddings (Usando Ollama)
    embedding_model = OllamaEmbeddings(
        model=EMBEDDING_MODEL,
        base_url=OLLAMA_BASE_URL
    )

    # 4. Splitters (Parent/Child)
    child_splitter = RecursiveCharacterTextSplitter.from_language(
        language=Language.PYTHON, chunk_size=400, chunk_overlap=50
    )
    parent_splitter = RecursiveCharacterTextSplitter.from_language(
        language=Language.PYTHON, chunk_size=2000, chunk_overlap=0
    )
    
    # Split documents
    parent_docs = parent_splitter.split_documents(original_docs)
    child_docs = child_splitter.split_documents(original_docs)

    # 5. Vectorstore (Chroma)
    vectorstore = Chroma(
        collection_name="maspy_codes",
        embedding_function=embedding_model,
        persist_directory=EMBEDDING_DIR
    )
    
    print("Indexando documentos...")
    # Add documents to vectorstore
    vectorstore.add_documents(child_docs)
    
    # Save parent documents for reference
    with open(os.path.join(DOCSTORE_DIR, "parent_docs.pkl"), "wb") as f:
        pickle.dump(parent_docs, f)
    
    print("Sucesso!")


if __name__ == "__main__":
    main()