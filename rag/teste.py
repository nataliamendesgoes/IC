from maspy import *

class SimpleAgent(Agent):
    def __init__(self):
        super().__init__()
        self.name = "Simple Agent"
        self.age = 25
        self.state = State("dormindo")
        self.action = Action("dizer_olá", ())
        self.transition = Transition(self.state, self.action)
        self.reward = Reward(10)
        self.condition = Condition(lambda: self.state == "despertado")
        self.start_action = StartAction("dizer_olá", ())
        self.end_action = EndAction("desligar", ())