# ==========================================================
# CÓDIGO MASPY GERADO (V5.1 - PREVENÇÃO DE AMNÉSIA DE CONTEXTO)
# ==========================================================
from maspy import *

class Sender(Agent):
    def __init__(self, name):
        super().__init__(name)
        self.add(Goal("send_message", Any))

    @pl(gain, Goal("send_message", Any))
    def send_message(self, src, msg, *args):
        self.print(f"Sending message '{msg}' to Receiver")
        self.send("Recv_1", achieve, Goal("receive_message", msg)) 

class Receiver(Agent):
    def __init__(self, name):
        super().__init__(name)
        self.add(Goal("receive_message", Any))
        self.add(Belief("Receiver", True))

    @pl(gain, Goal("receive_message", Any), Belief("Receiver"))
    def recv_message(self, src, msg, *args):
        self.print(f"Received message: '{msg}' from {src}")

if __name__ == "__main__":
    Admin().console_settings(True)
    sender = Sender("Sender")
    receiver = Receiver("Receiver")

    Admin().connect_to([sender], [Channel()])
    
    sender.send_message("Recv", "Hello, Receiver!")

    Admin().start_system()