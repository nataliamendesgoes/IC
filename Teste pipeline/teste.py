
from maspy import *

class Patient(Agent):
    @pl(gain, Goal("send_info", Any), Belief("sender"))
    def send_info(self, src, msg):
        agents_list = self.list_agents("Patient")
        for agent in agents_list:
            if agent == self.my_name:
                continue
            self.print(f"Sending> {msg} to {agent}")
            self.send(agent, achieve, Goal("receive_diagnosis", Any))

    @pl(gain, Belief("diagnosis"))
    def receive_diagnosis(self, src):
        self.print(f"Patient received diagnosis: {src}")

class Doctor(Agent):
    @pl(gain, Goal("print"), Belief("patient_name"))
    def print_patient_info(self, src):
        agents_list = self.list_agents("Doctor")
        for agent in agents_list:
            if agent == self.my_name:
                continue
            patient_name = self.get_belief(src, "patient_name").value
            self.print(f"Patient name: {patient_name}")

    @pl(gain, Goal("send_diagnosis", Any), Belief("diagnosis"))
    def send_diagnosis(self, src, msg):
        agents_list = self.list_agents("Doctor")
        for agent in agents_list:
            if agent == self.my_name:
                continue
            patient_name = self.get_belief(src, "patient_name").value
            self.print(f"Sending diagnosis to {patient_name}: {msg}")
            self.send(patient_name, achieve, Goal("receive_diagnosis", Any))

    @pl(gain, Belief("diagnosis"))
    def receive_diagnosis(self, src):
        agents_list = self.list_agents("Doctor")
        for agent in agents_list:
            if agent == self.my_name:
                continue
            diagnosis = self.get_belief(src, "diagnosis").value
            self.print(f"Received diagnosis: {diagnosis}")

if __name__ == "__main__":
    patient = Patient("Patient", [Belief("patient_name","John Doe"), Belief("sintoma","Fever")], Goal("send_info", Any))
    doctor = Doctor("Doctor", [], Goal("print_diagnosis", Any))

    Admin().start_system()