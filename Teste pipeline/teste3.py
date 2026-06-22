from maspy import *
import random

class Initiator(Agent):
    def __init__(self, agt_name=None):
        super().__init__(agt_name)
        self.add(Belief("estado", "iniciar_leilao"))
        self.add(Goal("iniciar_leilao"))

    @pl(gain, Goal("iniciar_leilao"))
    def iniciar_leilao(self, src, *args):
        self.print(f"Iniciando leilão")
        self.send("ParticipanteA_1", achieve, Goal("fazer_proposta"))
        self.send("ParticipanteB_1", achieve, Goal("fazer_proposta"))

    @pl(gain, Belief("proposta", Any), Goal("iniciar_leilao"))
    def receber_proposta(self, src, valor, *args):
        self.print(f"Recebido valor {valor} de {src}")
        if not hasattr(self, 'melhor_proposta') or valor > self.melhor_proposta:
            self.melhor_proposta = valor
            self.print(f"Novo melhor valor: {self.melhor_proposta}")

class ParticipanteA(Agent):
    def __init__(self, agt_name=None):
        super().__init__(agt_name)
        self.add(Belief("estado", "fazer_proposta"))
        self.add(Goal("fazer_proposta"))

    @pl(gain, Goal("fazer_proposta"))
    def fazer_proposta(self, src, *args):
        valor = random.randint(1, 100)
        self.print(f"ParticipanteA fez proposta: {valor}")
        self.send(src, tell, Belief("proposta", valor))

class ParticipanteB(Agent):
    def __init__(self, agt_name=None):
        super().__init__(agt_name)
        self.add(Belief("estado", "fazer_proposta"))
        self.add(Goal("fazer_proposta"))

    @pl(gain, Goal("fazer_proposta"))
    def fazer_proposa(self, src, *args):
        valor = random.randint(1, 100)
        self.print(f"ParticipanteB fez proposta: {valor}")
        self.send(src, tell, Belief("proposta", valor))

if __name__ == "__main__":
    Admin().console_settings(True)
    initiator = Initiator("Initiator")
    participante_a = ParticipanteA("ParticipanteA")
    participante_b = ParticipanteB("ParticipanteB")

    Admin().connect_to([initiator, participante_a, participante_b], [Channel()])
    
    initiator.stop_cycle()
    Admin().start_system()