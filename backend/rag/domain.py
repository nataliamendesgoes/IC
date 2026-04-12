import re

# Definição das Entidades do Domínio MASPY
MASPY_ENTITIES = {
    "Plan": {
        "keywords": ["plano", "plan", "@pl", "gatilho", "trigger"],
        "regex": [r"@pl", r"def\s+\w+\(.*\):\s*#.*plan", r"Plan"]
    },
    "Agent": {
        "keywords": ["agente", "agent", "criacao", "setup", "start"],
        "regex": [r"class\s+\w+\(Agent\):", r"super\(\)\.__init__"]
    },
    "Communication": {
        "keywords": ["mensagem", "enviar", "receber", "send", "msg", "comunicacao"],
        "regex": [r"self\.send", r"Message", r"acl="]
    },
    "Belief_Goal": {
        "keywords": ["crenca", "belief", "objetivo", "goal", "estado", "mental"],
        "regex": [r"Belief\(", r"Goal\(", r"add_belief", r"add_goal"]
    },
    "Output": {
        "keywords": ["print", "log", "saida", "escrever", "mostrar"],
        "regex": [r"self\.print", r"logger"]
    }
}

def detectar_entidades_no_codigo(codigo_chunk: str) -> list:
    """
    Analisa um trecho de código e retorna tags de quais entidades MASPY
    estão presentes nele (Ex: ['Plan', 'Communication']).
    """
    found_entities = set()
    for entity, rules in MASPY_ENTITIES.items():
        # Verifica Regex
        for pattern in rules["regex"]:
            if re.search(pattern, codigo_chunk, re.IGNORECASE):
                found_entities.add(entity)
                break
    
    # Se não achou nada específico, marca como Geral
    if not found_entities:
        found_entities.add("General")
        
    return list(found_entities)

def detectar_intencao_na_pergunta(pergunta: str) -> list:
    """
    Analisa a pergunta do usuário e estima quais entidades ele está procurando.
    """
    intencoes = set()
    pergunta = pergunta.lower()
    
    for entity, rules in MASPY_ENTITIES.items():
        for kw in rules["keywords"]:
            if kw in pergunta:
                intencoes.add(entity)
                break
                
    return list(intencoes)