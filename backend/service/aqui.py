
from maspy import *
from random import choice

class Armazem(Agent):
    def __init__(self, agt_name):
        super().__init__(agt_name)
        self.add(Belief("inventário", {"produto1": 10, "produto2": 5}))

    @pl(gain, Goal("verificar", Any), Belief("inventário"))
    def verificar_stock(self, src, item):
        stock = self.get(Belief("inventário")).values.get(item, 0)
        if stock > 0:
            self.print(f"Há {stock} unidades de {item} em stock")
            self.send(src, achieve, Goal("responder", (item, "True")))
        else:
            self.print(f"Não há stock de {item}")
            self.send(src, achieve, Goal("responder", (item, "False")))

class Cliente(Agent):
    @pl(gain, Goal("iniciar", Any))
    def iniciar(self, src, item):
        self.print(f"Pedindo stock de {item}")
        self.send("Armazem", achieve, Goal("verificar", item))

if __name__ == "__main__":
    Admin().console_settings(True)
    armazem = Armazem("Arm")
    cliente = Cliente("Cli")
    Admin().connect_to([armazem, cliente], [Channel("Comunicacao")])
    cliente.add(Goal("iniciar", "produto1"))
    Admin().start_system()