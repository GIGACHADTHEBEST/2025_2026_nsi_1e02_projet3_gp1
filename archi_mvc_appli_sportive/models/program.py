class Program:

    PROGRAMS = {
        "perte de poids": {
            "name": "Cardio + Full Body",
            "duration": 20,
            "exercises": [
                ("Jumping Jacks", 30),
                ("Squats", 15),
                ("Mountain Climbers", 30),
                ("Gainage", 30)
            ]
        },
        "prise de muscle": {
            "name": "Renforcement musculaire",
            "duration": 30,
            "exercises": [
                ("Pompes", 10),
                ("Squats", 15),
                ("Fentes", 10),
                ("Gainage", 45)
            ]
        },
        "cardio": {
            "name": "Course + HIIT",
            "duration": 25,
            "exercises": [
                ("Course rapide", 60),
                ("Marche", 60),
                ("Sprint", 30),
                ("Repos", 30)
            ]
        }
    }

    @staticmethod
    def get_program(goal):
        return Program.PROGRAMS.get(goal, None)