from model.user import User
from controller.workout_controller import WorkoutController

class app_controller:

    def onboarding(self):
        print("=== Onboarding rapide ===")

        name = input("Nom : ")
        gender = input("Genre (H/F) : ")
        age = int(input("Age : "))
        height = int(input("Taille (cm) : "))
        weight = int(input("Poids (kg) : "))

        goal = input("Objectif (perte de poids / prise de muscle / cardio) : ")
        level = input("Niveau (debutant / intermediaire) : ")
        equipment = input("Matériel (aucun / basique / salle) : ")

        user = User(name, gender, age, height, weight, goal, level, equipment)
        User.save_user(user)

        return user

    def run(self):
        user = self.onboarding()
        workout = WorkoutController(user)

        program = workout.generate_today_workout()

        print("\n=== Séance du jour ===")
        print(f"{program['name']} - {program['duration']} min")

        start = input("\nCommencer ? (oui/non) : ")

        if start == "oui":
            workout.start_workout()
            workout.end_workout()