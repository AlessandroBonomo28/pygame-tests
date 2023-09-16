
import json
import os
import uuid
import math
class Player:
    __constant_exp_multiplier : float = 11
    ID : str
    total_experience : float
    experience : float
    name : str
    level : int
    losses : int
    draws : int
    wins : int

    def __init__(self, name):
        self.ID = str(uuid.uuid4())
        self.name = name
        self.experience = 0
        self.draws = 0
        self.total_experience = 0
        self.level = 1
        self.losses = 0
        self.wins = 0
        if self.__exists():
            self.__load()
        self.__save()
    
    def change_name(self, new_name):
        self.name = new_name
        self.__save()

    def __exists(self) -> bool:
        return os.path.exists("data/player.json")

    def __load(self):
        # load from file
        with open("data/player.json", "r") as f:
            json_player = f.read()
            self.__dict__ = json.loads(json_player)

    def __save(self):
        json_player = json.dumps(self.__dict__)
        # save to file
        os.makedirs(os.path.dirname("data/player.json"), exist_ok=True)
        with open("data/player.json", "w") as f:
            f.write(json_player)
    
    def exp_limit_current_level(self):
        return self.__constant_exp_multiplier * math.sqrt(self.level)
    
    def add_win(self):
        self.wins += 1
        self.__save()
    
    def add_loss(self):
        self.losses += 1
        self.__save()
    
    def add_draw(self):
        self.draws += 1
        self.__save()

    def win_percent(self):
        if self.wins == 0:
            return 0
        return (self.wins / (self.wins + self.losses + self.draws))* 100
    
    def total_games(self):
        return self.wins + self.losses + self.draws

    def add_exp(self,exp):
        self.experience += exp
        self.total_experience += exp
        if int(self.experience) == int(self.exp_limit_current_level()):
            self.level += 1
            self.experience = 0
        while int(self.experience) > int(self.exp_limit_current_level()):
            self.experience -= self.exp_limit_current_level()
            self.level += 1
        self.__save()

    def __str__(self):
        return f"Player: {self.name} \
                \nLevel: {self.level} \
                \nExp: {int(self.experience)}/{int(self.exp_limit_current_level())} \
                \nWin percentage: {self.win_percent()}%"    

"""p = Player("test")

for i in range(1):
    p.add_exp(20)
    print(p)"""