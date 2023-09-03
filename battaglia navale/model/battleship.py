import random, math

class PieceColor:
    RED = "Rosso"
    BLACK = "Nero"

class GameStatus:
    RED_WINS = "il Rosso vince"
    BLACK_WINS = "il Nero vince"
    DRAW = "Patta"
    IN_PROGRESS = "Partita in corso"

class Piece:
    is_dead : bool
    positions : list[tuple]
    hits : list[tuple]
    color : PieceColor

    def __init__(self, positions, color : PieceColor):
        self.positions = positions
        self.color = color
        self.is_dead = False
        self.hits = []

    def hit(self, position):
        self.hits.append(position)
        if len(self.hits) == len(self.positions):
            self.is_dead = True

    def __deg2rad(self,degrees):
        return degrees * math.pi / 180
    
    def rotate(self,degrees):
        x = self.positions[0][0]
        y = self.positions[0][1]
        rad_angle = self.__deg2rad(degrees)
        new_positions = []
        for position in self.positions:
            dx = position[0] - x
            dy = position[1] - y
            new_dx = dx * math.cos(rad_angle) - dy * math.sin(rad_angle)
            new_dy = dx * math.sin(rad_angle) + dy * math.cos(rad_angle)
            new_positions.append((x+new_dx,y+new_dy))
        self.positions = new_positions

    def isAlreadyHit(self, position):
        return position in self.hits

    def __str__(self):
        col = "Red ship" if self.color == PieceColor.RED else "Black ship"
        return col+  str(self.positions) + " Is dead: " + str(self.is_dead)

    def reset(self):
        self.is_dead = False
        self.hits = []

class Move:
    turn : int
    actor : PieceColor
    position_hit : tuple
    piece_hit : Piece
    message : str
    def __init__(self, turn, actor, position_hit, piece_hit, message):
        self.turn = turn
        self.actor = actor
        self.position_hit = position_hit
        self.piece_hit = piece_hit
        self.message = message
    
    def did_hit(self):
        return self.piece_hit != None

    def __str__(self):
        if self.did_hit():
            return f"[Turn {self.turn}]: {self.actor} hits {self.piece_hit.color} ship at {self.position_hit}"
        else:
            return f"[Turn {self.turn}]: {self.actor} misses at {self.position_hit}"
    
    def made_by(self):
        return self.actor


class Board:
    __score_multiplier = 1
    status : GameStatus = GameStatus.IN_PROGRESS
    height : int = 12
    width : int = 12
    turn_count : int
    moves : list[Move]
    red_pieces : list[Piece]
    black_pieces : list[Piece]
    hash_hits : dict[tuple, Piece]
    hash_miss : dict[tuple, bool]
    red_score : int 
    black_score : int
    red_pieces_alive : int
    black_pieces_alive : int
    def __init__(self, pieces_red : list[Piece] = [],pieces_black : list[Piece] = []):
        self.black_score = 0
        self.red_score = 0
        self.red_pieces = pieces_red
        self.black_pieces = pieces_black
        self.hash_hits = {}
        self.hash_miss = {}
        self.moves = []
        self.turn_count = 0
        self.red_pieces_alive = len(self.red_pieces)
        self.black_pieces_alive = len(self.black_pieces)
        self.__updateStatus()

    
    def reset(self):
        black_pieces = []
        red_pieces = []
        for i in range(2):
            for j in range(Board.width):
                if (i+j)%2 == 0:
                    red_pieces.append(Piece([(j,i)],PieceColor.RED))
                    black_pieces.append(Piece([(Board.height-1-j,Board.height-1-i)],PieceColor.BLACK))
        self.__init__(red_pieces,black_pieces)

    def get_multiplier(self):
        return self.__score_multiplier
    
    def getPieceByPosition(self,position) -> Piece | None:
        try:
            for piece in self.red_pieces:
                if position in piece.positions:
                    return piece
            for piece in self.black_pieces:
                if position in piece.positions:
                    return piece
        except KeyError:
            return None

    def whoMoves(self) -> PieceColor:
        return PieceColor.BLACK if self.turn_count % 2 == 0 else PieceColor.RED

    def __updateStatus(self):
        # count red and black pieces
        red_pieces_alive = 0
        black_pieces_alive = 0
        for piece in self.red_pieces:
            if not piece.is_dead:
                red_pieces_alive += 1
        for piece in self.black_pieces:
            if not piece.is_dead:
                black_pieces_alive += 1
        if red_pieces_alive == 0:
            self.status = GameStatus.BLACK_WINS
        elif black_pieces_alive == 0:
            self.status = GameStatus.RED_WINS
        else:
            self.status = GameStatus.IN_PROGRESS
        self.red_pieces_alive = red_pieces_alive
        self.black_pieces_alive = black_pieces_alive

    def makeMove(self, move : Move):
        who_moves = "Red" if self.whoMoves() == PieceColor.RED else "Black"
        print(f"{who_moves} moves {move}")
        if move.piece_hit and move.piece_hit.isAlreadyHit(move.position_hit):
            print("Already hit")
            self.turn_count += 1
        elif move.did_hit():
            self.__mark_hit(move)
        else:
            self.__mark_miss(move)
            self.turn_count += 1
        
        self.moves.append(move)
        self.__updateStatus()

    def increment_score(self,move : Move):
        if move.actor == PieceColor.RED:
            self.red_score += 1 * self.__score_multiplier
        else:
            self.black_score += 1 * self.__score_multiplier

    def __mark_hit(self, move : Move):
        self.hash_hits[move.position_hit] = move.piece_hit
        move.piece_hit.hit(move.position_hit)
        self.increment_score(move)
            

    def __mark_miss(self, move : Move):
        print(f"Missed at {move.position_hit}")
        self.hash_miss[move.position_hit] = True

    def getCellColor(self, position) -> PieceColor | None:
        if not self.isInsideBounds(position):
            return None
        if position[1] >= self.height//2:
            return PieceColor.BLACK
        else:
            return PieceColor.RED
        
    def isInsideBounds(self, position):
        return position[0] >= 0 and position[0] < self.width and position[1] >= 0 and position[1] < self.height
    
    def __get_black_hits_centroid(self):
        x = 0
        y = 0
        count = 0
        for position in self.hash_hits.keys():
            if self.hash_hits[position].color == PieceColor.BLACK:
                x += position[0]
                y += position[1]
                count += 1
        if count == 0:
            return (self.width//2,self.height//2)
        return (x/count,y/count)
    
    def __squared_distance(self, position1, position2):
        return (position1[0]-position2[0])**2 + (position1[1]-position2[1])**2
    
   
    def __event_probability(self, percentage : float) -> bool:
        """
        Event probability is a function that returns true or false based on a percentage parameter between 0 and 1
        """
        return random.random() < percentage

    def makeMoveRedAI(self,board):
        max_try = 100
        try_count = 0
        # pick random position inside board
        while try_count < max_try:
            random_position = (random.randint(0,self.width-1),random.randint(self.height//2,self.height-1))
            piece_hit = board.getPieceByPosition(random_position)
            
            never_hit_before : bool = random_position not in board.hash_miss.keys() and \
                                      random_position not in board.hash_hits.keys()
            
            distance_trigger = 6
            probability_trigger = 0.75
            centroid_black = self.__get_black_hits_centroid()
            near_other_black_boats : bool = self.__squared_distance(random_position,centroid_black) < distance_trigger**2
            
            if never_hit_before or \
                (never_hit_before and self.__event_probability(probability_trigger) and near_other_black_boats):
                break
            try_count += 1
        move = Move(self.turn_count, PieceColor.RED, random_position, piece_hit, "random move AI")
        self.makeMove(move)
        print(f"AI move: {move}")
        return move

class Fleet:
    pieces : list[Piece]
    def __init__(self, pieces : list[Piece] = []):
        self.pieces = pieces
    
    def generate():
        pass
