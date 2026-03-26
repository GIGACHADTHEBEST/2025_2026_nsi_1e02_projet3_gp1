class Session:

    def __init__(self, program):
        self.program = program
        self.completed = False
        self.feedback = None

    def complete(self, feedback):
        self.completed = True
        self.feedback = feedback