class Agent:
    def __init__(self, name: str, logic_callback, data_input_callback, commands: dict):
        self.name = name
        self.logic_callback = logic_callback
        self.data_input_callback = data_input_callback
        self.commands = commands

    def run(self):
        self.logic_callback(self.commands, self.data_input_callback)
