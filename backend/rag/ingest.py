import os
import shutil
import sys
from typing import List

# Adiciona raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ===== Imports com Fallbacks =====
try:
    from langchain.schema import Document
except Exception:
    from langchain_core.documents import Document

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
    from langchain_community.document_loaders.generic import GenericLoader
    from langchain_community.document_loaders.parsers.language.language_parser import LanguageParser
except Exception:
    try:
        from langchain.document_loaders.generic import GenericLoader
        from langchain.document_loaders.parsers import LanguageParser
    except Exception:
        GenericLoader = None
        LanguageParser = None

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter, Language
except Exception:
    try:
        from langchain.text_splitter import RecursiveCharacterTextSplitter, Language
    except Exception:
        RecursiveCharacterTextSplitter = None
        Language = None

try:
    from langchain_ollama import OllamaEmbeddings
except Exception:
    try:
        from langchain_community.embeddings import OllamaEmbeddings
    except Exception:
        try:
            from langchain.embeddings import OllamaEmbeddings
        except Exception:
            OllamaEmbeddings = None

# Importa as regras de domínio
try:
    from rag.domain import detectar_entidades_no_codigo
except ImportError:
    # Fallback simples se domain.py não existir (mas crie ele!)
    def detectar_entidades_no_codigo(x): return []

from rag.config import (
    SOURCE_DIR, EMBEDDING_DIR, EMBEDDING_MODEL, OLLAMA_BASE_URL
)

def main():
    print(f"--- INGESTÃO INTELIGENTE MASPY ---")
    
    # Verificações rápidas de disponibilidade de dependências
    missing = []
    if GenericLoader is None or LanguageParser is None:
        missing.append("GenericLoader/LanguageParser")
    if Language is None:
        missing.append("Language")
    if RecursiveCharacterTextSplitter is None:
        missing.append("RecursiveCharacterTextSplitter")
    if Chroma is None:
        missing.append("Chroma")
    if OllamaEmbeddings is None:
        missing.append("OllamaEmbeddings")

    if missing:
        print(f"❌ ERRO: Dependências ausentes: {', '.join(missing)}")
        print("   Execute: pip install -r requirements.txt")
        return
    
    # 1. Limpeza (Remove banco antigo para criar o novo com metadados)
    if os.path.exists(EMBEDDING_DIR):
        print("🗑️  Removendo banco antigo...")
        try:
            shutil.rmtree(EMBEDDING_DIR)
        except Exception as e:
            print(f"⚠️  Aviso: Não foi possível apagar pasta automaticamente ({e}). Apague manualmente se der erro.")

    # 2. Carregar Código
    print(f"📂 Lendo arquivos de: {SOURCE_DIR}")
    loader = GenericLoader.from_filesystem(
        SOURCE_DIR,
        glob="**/*",
        suffixes=[".py"],
        parser=LanguageParser(language=Language.PYTHON, parser_threshold=500),
    )
    docs = loader.load()

    # 3. Splitter
    splitter = RecursiveCharacterTextSplitter.from_language(
        language=Language.PYTHON, 
        chunk_size=800,       # Chunks maiores para pegar funções inteiras
        chunk_overlap=100
    )
    chunks = splitter.split_documents(docs)
    
    print(f"🧩 Processando {len(chunks)} trechos de código...")

    # 4. ENRIQUECIMENTO DE METADADOS
    chunks_enriquecidos = []
    stats = {}

    for doc in chunks:
        # Detecta entidades (Agent, Plan, Belief, etc)
        entidades = detectar_entidades_no_codigo(doc.page_content)
        
        # Adiciona aos metadados (Join com vírgula para salvar no Chroma)
        if entidades:
            doc.metadata["maspy_entities"] = ",".join(entidades)
            for ent in entidades:
                stats[ent] = stats.get(ent, 0) + 1
        
        chunks_enriquecidos.append(doc)

    print("\n📊 Estatísticas de Entidades Detectadas:")
    for ent, count in stats.items():
        print(f"   - {ent}: {count} chunks")

    # 5. Salvar no Banco
    print("\n💾 Salvando Embeddings...")
    embedding_model = OllamaEmbeddings(
        model=EMBEDDING_MODEL,
        base_url=OLLAMA_BASE_URL
    )

    Chroma.from_documents(
        documents=chunks_enriquecidos,
        embedding=embedding_model,
        persist_directory=EMBEDDING_DIR,
        collection_name="maspy_codes"
    )
    
    print(f"✅ Sucesso! Banco salvo em {EMBEDDING_DIR}")

if __name__ == "__main__":
    main()