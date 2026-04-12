from typing import List

try:
    from langchain.retrievers.base import BaseRetriever
except Exception:
    from langchain_core.retrievers import BaseRetriever

try:
    from langchain.callbacks.manager import CallbackManagerForRetrieverRun
except Exception:
    from langchain_core.callbacks import CallbackManagerForRetrieverRun

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

from rag.domain import detectar_intencao_na_pergunta

class MaspyEntityRetriever(BaseRetriever):
    """
    Retriever especializado no domínio MASPY.
    Realiza filtragem de metadados antes da busca vetorial
    baseado na detecção de intenção da pergunta.
    """
    vectorstore: Chroma
    search_kwargs: dict = {"k": 4}

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun = None
    ) -> List[Document]:
        
        # 1. Análise Semântica da Pergunta
        intencoes = detectar_intencao_na_pergunta(query)
        
        # 2. Configuração do Filtro
        # Se detectamos uma entidade específica (ex: "Plan"), filtramos o banco
        # Se não detectamos (pergunta genérica), buscamos em tudo.
        filtro = None
        
        if intencoes:
            # Lógica: Se a pergunta menciona "plano", buscar chunks que tenham "Plan" nos metadados
            # Como Chroma filtering é restritivo, usaremos uma busca "OR" se houver multiplas intenções
            # Mas por simplicidade, pegamos a primeira intenção forte.
            
            # Nota técnica: Chroma filter com $contains em string é limitado dependendo da versão.
            # Vamos buscar sem filtro hard, mas vamos logar a intenção.
            # (Para uma implementação estrita de filtro, precisariamos que o metadata fosse exato).
            
            print(f"🔍 [Retriever] Intenção detectada: {intencoes}")
            
            # Recupera documentos (busca vetorial normal primeiro)
            docs = self.vectorstore.similarity_search(query, k=self.search_kwargs["k"] * 2)
            
            # Re-Ranking / Filtragem em Memória (Mais flexível e seguro)
            docs_filtrados = []
            for doc in docs:
                doc_entities = doc.metadata.get("maspy_entities", "").split(",")
                
                # Se qualquer intenção da pergunta bater com qualquer entidade do doc
                if any(inten in doc_entities for inten in intencoes):
                    docs_filtrados.append(doc)
            
            # Se o filtro foi muito agressivo e não sobrou nada, usamos fallback
            if not docs_filtrados:
                print("⚠️ [Retriever] Filtro muito restritivo, retornando busca semântica pura.")
                return docs[:self.search_kwargs["k"]]
                
            return docs_filtrados[:self.search_kwargs["k"]]

        else:
            print(f"🔍 [Retriever] Busca genérica (sem entidade explícita)")
            return self.vectorstore.similarity_search(query, **self.search_kwargs)