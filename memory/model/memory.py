import random, math

class GameStatus:
    WIN = "Vittoria"
    LOSE = "Sconfitta"
    DRAW = "Pareggio"
    IN_PROGRESS = "Partita in corso"

class Card:
    guessed : bool
    position : tuple
    hashed_id : str

    def __init__(self, position, hashed_id : str):
        self.position = position
        self.hashed_id = hashed_id
        self.guessed = False

    def equals(self, other):
        return self.hashed_id == other.hashed_id
    
    def __str__(self):
        return f"Piece at {self.position} with id {self.hashed_id}"
    def reset(self):
        self.guessed = False

class Move:
    turn : int
    pair : tuple[ Card, Card ]
    message : str
    def __init__( self, turn : int, pair : tuple[ Card, Card ], message : str ):
        self.turn = turn
        self.pair = pair
        self.message = message
    
    def did_guess(self):
        return self.pair[0].equals(self.pair[1])

    def __str__(self):
        return f"Turn {self.turn}, choose pair: {self.pair[0]} - {self.pair[1]}"


class Board:
    guessed : list[Card]
    __score_multiplier = 1
    status : GameStatus = GameStatus.IN_PROGRESS
    height : int = 14
    width : int = 14
    turn_count : int
    moves : list[Move]
    cards : list[Card]
    score : int
    def __init__(self, cards : list[Card] = []):
        self.score = 0
        self.moves = []
        self.guessed = []
        self.turn_count = 0
        self.cards = cards
        self.__updateStatus()

    
    def reset(self):
        positions = []
        for card in self.cards:
            card.reset()
            positions.append(card.position)
        # shuffle cards positions
        random.shuffle(positions)
        for card in self.cards:
            card.position = positions.pop()
        
        self.__init__(self.cards)

    def get_multiplier(self):
        return self.__score_multiplier
    

    def getCardByPosition(self,position) -> Card | None:
        try:
            for card in self.cards:
                if card.position == position:
                    return card
        except KeyError:
            return None
    
    def __updateStatus(self):
        cards_to_guess = 0
        for card in self.cards:
            if not card.guessed:
                cards_to_guess += 1
        if cards_to_guess == 0:
            self.status = GameStatus.WIN
        else:
            self.status = GameStatus.IN_PROGRESS

    def makeMove(self, move : Move):
        self.turn_count += 1
        if move.did_guess():
            move.pair[0].guessed = True
            move.pair[1].guessed = True
            self.guessed.append(move.pair[0])
            self.guessed.append(move.pair[1])
            self.increment_score(move)
        self.moves.append(move)
        self.__updateStatus()

    def increment_score(self,move : Move):
        if move.did_guess():
            self.score += 1 * self.__score_multiplier
            
    def isInsideBounds(self, position):
        return position[0] >= 0 and position[0] < self.width and position[1] >= 0 and position[1] < self.height
