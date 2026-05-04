from model.program import Program
from model.session import Session

class WorkoutController:

    def __init__(self, user):
        self.user = user
        self.session = None

    def generate_today_workout(self):
        program = Program.get_program(self.user.goal)
        self.session = Session(program)
        return program

    def start_workout(self):
        program = self.session.program
        print(f"\nAujourd'hui : {program['name']} - {program['duration']} min\n")

        for ex, reps in program["exercises"]:
            print(f"{ex} -> {reps}")
            input("Appuie sur Entrée pour continuer...")

    def end_workout(self):
        feedback = input("Difficulté (facile / ok / difficile) : ")
        self.session.complete(feedback)
        print("\n✅ Séance terminée !")