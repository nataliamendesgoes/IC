from maspy import *

from random import randint

class Initiator(Agent):
    def __init__(self, agt_name=None):
        super().__init__(agt_name)
        self.add(Goal("iniciar_leilao"))
        self.add(Belief("estado", "verde"))  # Adicionando crença para o Iniciador
    
    @pl(gain, Goal("iniciar_leilao"))
    def iniciar_leilao(self, src, *args):
        value = randint(15, 30)
        self.add(Belief("valor_inicial", value))
        self.print(f"Broadcasting initial value {value} to all participants")
        self.send(broadcast, tell, Goal("fazer_proposta"))
    
    @pl(gain, Goal("proposta_recebida"), Belief("valor_inicial", Any))
    def processar_proposta(self, src, proposta, *args):
        if proposta > self.get(Belief, "valor_inicial"):
            self.print(f"Received higher proposal {proposta} from {src}")
            self.add(Belief("melhor_proposta", proposta))
        else:
            self.print(f"Proposal {proposta} from {src} is not better")
    
    def on_idle(self):
        pass

class Participante(Agent):
    def __init__(self, agt_name=None):
        super().__init__(agt_name)
        self.add(Goal("fazer_proposta"))
        self.proposta = randint(10, 25)  # Valor distinto para cada participante
        self.add(Belief("estado", "verde"))  # Adicionando crença para os Participantes
    
    @pl(gain, Goal("fazer_proposa"))
    def fazer_proposa(self, src, *args):
        valor_inicial = self.get(Belief, "valor_inicial")
        if self.proposta > 1.5 * valor_inicial:
            self.print(f"Refusing initial value {valor_inicial}")
        else:
            self.print(f"Offering ({self.proposta}) for the initial value")
            self.send(src, achieve, Goal("proposta_recebida", self.proposta))
    
    def on_idle(self):
        pass

if __name__ == "__main__":
    Admin().console_settings(True)
    # Instanciando agentes e canais/ambientes
    iniciador = Initiator("Initiator")
    participante_a = Participante("Participante")
    participante_b = Participante("Participante")
    
    canal = Channel()
    ambiente1 = Ambiente("Ambiente")
    
    # Conectando agentes e canais/ambientes
    Admin().connect_to([iniciador, participante_a, participante_b], [Channel(), canal])
    Admin().start_system()