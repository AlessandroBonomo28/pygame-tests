import random, datetime

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

    

    def __str__(self):
        col = "Red ship" if self.color == PieceColor.RED else "Black ship"
        return col+  str(self.positions) + " Is dead: " + str(self.is_dead)

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
        return self.piece_hit is not None

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
    def __init__(self, pieces_red : list[Piece] = [],pieces_black : list[Piece] = []):
        self.black_score = 0
        self.red_score = 0
        self.red_pieces = pieces_red
        self.black_pieces = pieces_black
        self.hash_hits = {}
        self.hash_miss = {}
        self.moves = []
        self.turn_count = 0
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
            for piece in self.red_pieces.extend(self.black_pieces):
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

    def makeMove(self, move : Move, append_hashmap : bool = True):
        who_moves = "Red" if self.whoMoves() == PieceColor.RED else "Black"
        print(f"{who_moves} moves {move}")
        if move.did_hit:
            self.__mark_hit(move)
        else:
            self.__mark_miss(move)
        
        self.moves.append(move)
        if append_hashmap:
            self.append_hashmap_copy(self.hashMapPieces)
        
        possible_moves = move.piece.evaluateMovePositions(self)
        # filter only eat moves
        possible_eat_moves = list(filter(lambda m: m.does_eat, possible_moves)) 
        
        if move.does_eat and len(possible_eat_moves) > 0:
            self.turn_count += 0
            # auto eat
            #if len(possible_eat_moves) == 1:
            #    self.makeMove(possible_eat_moves[0])
        else:
            self.turn_count += 1
        self.__updateStatus()

    def increment_score(self,move : Move):
        if move.actor == PieceColor.RED:
            self.red_score += 1 * self.__score_multiplier
        else:
            self.black_score += 1 * self.__score_multiplier

    def __mark_hit(self, move : Move):
        self.hash_hits[move.position_hit] = move.piece_hit
        self.increment_score(move)
            

    def __mark_miss(self, move : Move):
        self.hash_miss[move.position_hit] = True

    
        
    def isInsideBounds(self, position):
        return position[0] >= 0 and position[0] < self.width and position[1] >= 0 and position[1] < self.height
    
    def makeMoveRedAI(self):
        return self.__makeMoveAI()
    
    def __makeMoveAI(self):
        # pick random position inside board
        random_position = (random.randint(0,self.width-1),random.randint(0,self.height-1))
        move = Move(self.turn_count, PieceColor.RED, random_position, False, "random move AI")
        self.makeMove(move)
        return move
