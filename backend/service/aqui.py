from maspy import *

class Semaforo(Agent):
    def __init__(self, agt_name):
        super().__init__(agt_name)
        self.add(Belief("estado", "vermelho"))
        self.add(Goal("iniciar_ciclo"))

    @pl(gain, Goal("iniciar_ciclo"), Belief("estado", "vermelho"))
    def iniciar_ciclo(self, src, *args):
        self.print("Sinal Vermelho!")
        self.send("CarroNorte_1", achieve, Goal("parar"))
        self.send("CarroSul_1", achieve, Goal("parar"))
        self.stop_cycle()

class CarroNorte(Agent):
    def __init__(self, agt_name):
        super().__init__(agt_name)

    @pl(gain, Goal("parar"))
    def parar(self, src, *args):
        self.print("Travando o veículo!")
        self.stop_cycle()

class CarroSul(Agent):
    def __init__(self, agt_name):
        super().__init__(agt_name)

    @pl(gain, Goal("parar"))
    def parar(self, src, *args):
        self.print("Travando o veículo!")
        self.stop_cycle()

if __name__ == "__main__":
    Admin().console_settings(True)
    semaforo = Semaforo("Semaforo")
    carro_norte = CarroNorte("CarroNorte")
    carro_sul = CarroSul("CarroSul")

    Admin().connect_to([semaforo, carro_norte, carro_sul], [Channel()])

    semaforo.start_cycle()

    Admin().start_system()
