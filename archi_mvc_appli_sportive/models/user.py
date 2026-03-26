import json

class User:
    def __init__(self, name, gender, age, height, weight, goal, level, equipment):
        self.name = name
        self.gender = gender
        self.age = age
        self.height = height
        self.weight = weight
        self.goal = goal
        self.level = level
        self.equipment = equipment

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def load_users(path="data/users.json"):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except:
            return []

    @staticmethod
    def save_user(user, path="data/users.json"):
        users = User.load_users(path)
        users.append(user.to_dict())
        with open(path, "w") as f:
            json.dump(users, f, indent=4)