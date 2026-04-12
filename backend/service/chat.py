import sys
import os
import re
import time
import threading

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ==============================================================================
# 1. IMPORTAÇÕES E CONFIGURAÇÃO
# ==============================================================================

try:
    from langchain_chroma import Chroma
except Exception:
    try:
        from langchain_community.vectorstores import Chroma
    except Exception:
        from langchain.vectorstores import Chroma

try:
    from langchain_ollama import OllamaLLM as ChatOllama, OllamaEmbeddings
except Exception:
    try:
        from langchain_community.llms import Ollama as ChatOllama
        from langchain_community.embeddings import OllamaEmbeddings
    except Exception:
        ChatOllama = None
        OllamaEmbeddings = None

try:
    from service.rag.retriever import MaspyEntityRetriever
    USAR_CUSTOM = True
except ImportError:
    USAR_CUSTOM = False

from service.config import (
    EMBEDDING_DIR, LLM_MODEL, EMBEDDING_MODEL, OLLAMA_BASE_URL
)


# Visual de carregamento simples para melhorar a experiência do usuário durante a geração de código, que pode levar alguns segundos. O spinner é interrompido assim que a resposta é recebida.


stop_spinner = False

def _spinner():
    chars = ['|', '/', '-', '\\']
    i = 0
    while not stop_spinner:
        print(f"\r{chars[i % len(chars)]}", end='', flush=True)
        time.sleep(0.1)
        i += 1

# Pós processamento de código gerado para garantir conformidade com as regras do MASPY e evitar erros comuns.


def extract_code_block(text: str) -> str:
    if not text: return ""
    match = re.search(r'```python\s*(.*?)\s*```', text, re.DOTALL)
    if match: return match.group(1).strip()
    
    if 'from maspy' in text:
        lines = text.split('\n')
        start_idx = -1
        for i, line in enumerate(lines):
            if 'from maspy' in line:
                start_idx = i
                break
        if start_idx != -1:
            return '\n'.join(lines[start_idx:]).strip()
    return text.strip()

def pos_processar(code: str) -> str:
    """Aplica regras gramaticais universais do framework MASPY baseadas nos 22 exemplos."""
    if not code: return code
    fixes = []

    def fix_src_arg(m):
        header = m.group(1)
        indent = m.group(2)
        func_name = m.group(3)
        args_raw = m.group(4).strip()
        
        args_list = [a.strip() for a in args_raw.split(',')]
        if 'src' not in args_list:
            if 'self' in args_list:
                idx = args_list.index('self')
                args_list.insert(idx + 1, 'src')
            else:
                args_list.insert(0, 'self')
                args_list.insert(1, 'src')
            fixes.append(f"Injetado 'src' em {func_name}")
            return f"{header}{indent}def {func_name}({', '.join(args_list)}):"
        return m.group(0)

    code = re.sub(r'(@pl\(.*?\)\s*\n)(\s*)def\s+(\w+)\s*\((.*?)\):', fix_src_arg, code, flags=re.DOTALL)


    before = code
    code = re.sub(r'\w+\.self\.print\(', 'self.print(', code)
    code = re.sub(r'(?<!self\.)(?<!\w)print\(', 'self.print(', code)
    if code != before: fixes.append("Normalizado self.print()")

    code = re.sub(r'\bself\.name\b', 'self.my_name', code)
    code = re.sub(r'\.add_goal\(', '.add(', code)
    code = re.sub(r'\.add_belief\(', '.add(', code)


    if 'Channel(' in code and 'self.send(' in code:
        if not re.search(r'self\.send\(.*?,.*?,.*?,.*?\)', code):
            code = re.sub(r'Channel\(".*?"\)', 'Channel()', code)
            fixes.append("Simplificado Channel para evitar erro de roteamento")

    code = re.sub(r'Goal\((.*?),\s*(True|False)\)', r'Goal(\1, "\2")', code)
    code = re.sub(r'Belief\((.*?),\s*(True|False)\)', r'Belief(\1, "\2")', code)

    if 'from maspy' in code:
        code = code.replace('Admin().start_system()', '')
        if 'if __name__ == "__main__":' in code:
            code = re.sub(r'(if __name__ == "__main__":.*?)\s*$', r'\1\n    Admin().start_system()', code, flags=re.DOTALL)
        else:
            code += '\n\nif __name__ == "__main__":\n    Admin().start_system()'
        fixes.append("Finalizado com Admin().start_system()")

    if fixes:
        print(f"[POST-PROCESS] 🔧 {', '.join(set(fixes))}")
    return code.strip()


# Prompts para geração e incremento de código, incluindo um modelo de sucesso baseado nos exemplos fornecidos, e instruções claras para garantir que o código gerado esteja em conformidade com as regras do framework MASPY. O prompt de geração inclui também um contexto técnico extraído dos códigos existentes para auxiliar o LLM na criação de código relevante e funcional. O prompt de incremento foca em modificar o código existente conforme as novas instruções, garantindo a continuidade e correção do sistema.


def montar_prompt_geracao(question: str, context: str) -> str:
    instructions = """
1. CANAL DE COMUNICAÇÃO: Se criar um Channel("Nome") no main, os agentes DEVEM usar esse nome no self.send(..., "Nome"). Caso contrário, use apenas Channel() sem nome para usar o canal padrão.
2. SINCRONIA DE CRENÇAS: Se o Armazém tem a crença "inventário", o método self.get() deve usar EXATAMENTE "inventário". 
3. GATILHO INICIAL: O Cliente precisa de um @pl para o objetivo que você adiciona no main (ex: Goal("iniciar")).
4. ARIDADE DE GOALS: Se o @pl espera (self, src, item), o Goal deve ser enviado como Goal("nome", item). Se enviar uma tupla (item, valor), o @pl deve ser (self, src, item, valor).
5. ESTRUTURA DO __main__: Atribua instâncias a variáveis, conecte via connect_to e finalize com UM Admin().start_system().
"""
    gold_standard = """
class Cliente(Agent):
    @pl(gain, Goal("iniciar", Any))
    def iniciar(self, src, item):
        self.print(f"Pedindo {item}")
        self.send("Armazem", achieve, Goal("verificar", item))

if __name__ == "__main__":
    Admin().console_settings(True)
    armazem = Armazem("Arm")
    cliente = Cliente("Cli")
    # Use Channel() sem nome para evitar erros de conexão se o LLM esquecer o parâmetro no send
    Admin().connect_to([armazem, cliente], [Channel()])
    cliente.add(Goal("iniciar", "produto1")) 
    Admin().start_system()
"""
    return (
        "Você é o Arquiteto MASPY Universal. Gere código Python funcional seguindo as regras do framework BDI.\n"
        "REGRAS DE OURO:\n" + instructions + "\n\n"
        "MODELO DE SUCESSO:\n" + gold_standard + "\n\n"
        "CONTEXTO TÉCNICO (RAG):\n" + context + "\n\n"
        "PEDIDO DO UTILIZADOR: " + question + "\n\nCÓDIGO:\n"
    )

def montar_prompt_incremento(question: str, codigo_atual: str) -> str:
    return (
        "Modifique o código MASPY abaixo. Garanta a conexão correta dos canais no __main__.\n"
        "- Certifique-se de que o nome das crenças em 'self.get' bate com o 'self.add'.\n"
        "- Retorne o código COMPLETO.\n\n"
        "PEDIDO: " + question + "\n\n"
        "CÓDIGO ATUAL:\n" + codigo_atual + "\n\nCÓDIGO MODIFICADO:\n"
    )

def montar_prompt_condense(history: str, question: str) -> str:
    return (
        "Reformule a pergunta para ser uma instrução MASPY independente.\n\n"
        "Histórico:\n" + history + "\n\n"
        "Pergunta: " + question + "\nReescrita:"
    )

# Sistema de chat interativo que utiliza um modelo LLM para gerar ou modificar código MASPY com base em perguntas do usuário, contexto técnico relevante e um modelo de sucesso. O sistema inclui um spinner de carregamento para melhorar a experiência do usuário durante a geração de código, e um pós-processamento para garantir que o código gerado esteja em conformidade com as regras do framework MASPY, evitando erros comuns e garantindo a funcionalidade do código. O histórico de interações é mantido para permitir perguntas contextuais e incrementais, e o sistema é projetado para ser robusto, fornecendo feedback claro em caso de falhas no processamento.


def main():
    if not os.path.exists(EMBEDDING_DIR):
        print("❌ ERRO: Banco de dados não encontrado.")
        return

    print("=" * 60)
    print(f"🔧 MOTOR MASPY CHAT - ENGINE: {LLM_MODEL}")
    print("=" * 60)

    llm = ChatOllama(model=LLM_MODEL, base_url=OLLAMA_BASE_URL, temperature=0.1, num_predict=2048)
    embedding_model = OllamaEmbeddings(model=EMBEDDING_MODEL, base_url=OLLAMA_BASE_URL)
    vectorstore = Chroma(collection_name="maspy_codes", embedding_function=embedding_model, persist_directory=EMBEDDING_DIR)
    retriever = MaspyEntityRetriever(vectorstore=vectorstore, search_kwargs={"k": 4}) if USAR_CUSTOM else vectorstore.as_retriever(search_kwargs={"k": 4})

    print("\n✅ SISTEMA PRONTO. Digite 'sair' para encerrar.")
    historico = []

    while True:
        query = input("\n[MASPY] > ").strip()
        if not query or query.lower() in ["sair", "exit"]: break
        start_time = time.time()
        is_inc = any(kw in query.lower() for kw in ["adicione", "mude", "altere", "agora", "também", "incrementa", "modifica"])

        try:
            q = query
            if historico and not is_inc:
                hist_txt = "\n".join([f"U: {u}\nA: {a[:100]}..." for u, a in historico[-2:]])
                resp = llm.invoke(montar_prompt_condense(hist_txt, query))
                q = (resp.content if hasattr(resp, 'content') else str(resp)).strip()

            context = ""
            if not is_inc:
                docs = retriever.invoke(q)
                trechos = [f"# Fonte: {os.path.basename(d.metadata.get('source','?'))}\n{d.page_content[:1200]}" for d in docs]
                context = "\n\n---\n\n".join(trechos)

            prompt = montar_prompt_incremento(query, historico[-1][1]) if is_inc and historico else montar_prompt_geracao(q, context)
            
            global stop_spinner
            stop_spinner = False
            th = threading.Thread(target=_spinner, daemon=True)
            th.start()

            response = llm.invoke(prompt)

            stop_spinner = True
            th.join()
            print("\r", end='', flush=True)

            raw_output = response.content if hasattr(response, 'content') else str(response)
            answer = extract_code_block(raw_output)
            answer = pos_processar(answer)

            print(f"\n{'='*60}\n💡 CÓDIGO MASPY GERADO:\n")
            print(answer)
            print(f"\n{'='*60}\n⏱️ Tempo: {time.time()-start_time:.2f}s")

            if len(answer) > 50:
                historico.append((query, answer))

        except Exception as e:
            print(f"❌ Falha no processamento: {e}")

if __name__ == "__main__":
    main()