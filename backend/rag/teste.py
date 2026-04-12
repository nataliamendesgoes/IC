from maspy import *

class HelloAgent(Agent):
    @pl(gain, Belief("hello"))
    def func(self):
        print("Olá, Mundo!")

if __name__ == "__main__":
    ag = HelloAgent()
    Admin().start_system()