import random

class PieceColor:
    RED = "Rosso"
    BLACK = "Nero"

class GameStatus:
    RED_WINS = "Rosso vince"
    BLACK_WINS = "Nero vince"
    DRAW = "Patta"
    IN_PROGRESS = "In corso"

class Piece:
    is_dama : bool
    steps : int
    position : tuple
    color : PieceColor

    def __init__(self, position, color : PieceColor, is_dama : bool = False):
        self.is_dama = is_dama
        self.position = position
        self.color = color
        self.steps = 0

    def move(self, position):
        self.position = position
        self.steps += 1
        if self.color == PieceColor.RED and self.position[1] == 7:
            self.is_dama = True
        elif self.color == PieceColor.BLACK and self.position[1] == 0:
            self.is_dama = True
    
    def printAviableMoves(self, b):
        moves = self.evaluateMovePositions(b)
        for move in moves:
            print(move)

    def evaluateMovePositions(self, b ) -> list[any]:
        moves = []

        top_left = (-1,-1)
        top_right = (+1, -1)
        bottom_left = (-1, +1)
        bottom_right = (+1, +1)
        if self.is_dama:
            positions_to_check = [top_left, top_right, bottom_left, bottom_right]
        else:
            if self.color == PieceColor.BLACK:
                positions_to_check = [top_left, top_right]
            else:  
                positions_to_check = [bottom_left, bottom_right]

        for collision in positions_to_check:
            check_position = (self.position[0] + collision[0], self.position[1] + collision[1])
            hit = b.getPieceByPosition(check_position)
            if b.isInsideBounds(check_position) and hit == None:
                move = Move(self, self.position, check_position, "move")
                moves.append(move) # free position
            elif b.isInsideBounds(check_position) and hit != None:
                if hit.color != self.color and (self.is_dama or not hit.is_dama):
                    # can eat piece
                    check_position = (self.position[0] + collision[0]*2, self.position[1] + collision[1]*2)
                    if b.isInsideBounds(check_position) and b.getPieceByPosition(check_position) == None:
                        move = Move(self, self.position, check_position, "eat", True, hit)
                        moves.append(move)
                    else:
                        continue
                else:
                    continue
            else: # out of bounds
                continue

        return moves
    
    def __str__(self):
        col = "Red" if self.color == PieceColor.RED else "Black"
        return col+" "+str(self.steps) + " " + str(self.position) + " Dama: " + str(self.is_dama)


class Move:
    piece : Piece
    piece_to_eat : Piece
    position_from : tuple
    position_to : tuple
    does_eat : bool
    message : str
    def __init__(self, piece, position_from,position_to, message,does_eat = False, piece_to_eat = None):
        self.piece = piece
        self.piece_to_eat = piece_to_eat
        self.position_from = position_from
        self.position_to = position_to
        self.does_eat = does_eat
        self.message = message
    def __str__(self):
        msg = self.message + " " + str(self.position_from) + " -> " + str(self.position_to)
        if self.does_eat:
            msg += " - move eats "
        return msg
    
    def made_by(self):
        return self.piece.color
    

class Board:
    __score_multiplier = 1
    status : GameStatus = GameStatus.IN_PROGRESS
    height : int = 8
    width : int = 8
    turn_count : int
    moves : list[Move]
    hashMapPieces : dict[tuple, Piece]
    red_score : int 
    black_score : int
    red_pieces_start : list[Piece]
    black_pieces_start : list[Piece]
    def __init__(self, pieces_red : list[Piece],pieces_black : list[Piece]):
        self.black_score = 0
        self.red_score = 0
        self.hashMapPieces = {}
        self.moves = []
        self.turn_count = 0
        for piece in pieces_red:
            self.hashMapPieces[piece.position] = piece
        for piece in pieces_black:
            self.hashMapPieces[piece.position] = piece
        self.__updateStatus()
        self.red_pieces_start = pieces_red.copy()
        self.black_pieces_start = pieces_black.copy()

    def reset(self):
        black_pieces = []
        red_pieces = []
        for i in range(3):
            for j in range(8):
                if (i+j)%2 == 0:
                    red_pieces.append(Piece((j,i),PieceColor.RED,False))
                    black_pieces.append(Piece((7-j,7-i),PieceColor.BLACK,False))
        self.__init__(red_pieces,black_pieces)

    def get_multiplier(self):
        return self.__score_multiplier
    
    def getPieceByPosition(self,position) -> Piece | None:
        try:
            return self.hashMapPieces[position]
        except KeyError:
            return None
    
    def whoMoves(self) -> PieceColor:
        return PieceColor.BLACK if self.turn_count % 2 == 0 else PieceColor.RED

    def __updateStatus(self):
        count_available_moves = 0
        # count red and black pieces
        red_pieces = 0
        black_pieces = 0
        for piece in self.hashMapPieces.values():
            if piece is None:
                continue
            if piece.color == self.whoMoves():
                count_available_moves += len(piece.evaluateMovePositions(self))
            if piece.color == PieceColor.RED:
                red_pieces += 1
            else:
                black_pieces += 1
        if red_pieces == 0:
            self.status = GameStatus.BLACK_WINS
        elif black_pieces == 0:
            self.status = GameStatus.RED_WINS
        elif count_available_moves == 0:
            self.status = GameStatus.DRAW
        else:
            self.status = GameStatus.IN_PROGRESS

    def makeMove(self, move : Move):
        was_dama = move.piece.is_dama
        who_moves = "Red" if self.whoMoves() == PieceColor.RED else "Black"
        print(f"{who_moves} moves {move}")
        if move.does_eat:
            self.__eatPiece(move.piece, move.piece_to_eat,move.position_to)
        else:
            self.__movePiece(move.piece, move.position_to)
        self.moves.append(move)

        if not was_dama and move.piece.is_dama and move.piece.color == PieceColor.RED:
            self.red_score += 1 * self.__score_multiplier
        elif not was_dama and move.piece.is_dama and move.piece.color == PieceColor.BLACK:
            self.black_score += 1 * self.__score_multiplier

        possible_moves = move.piece.evaluateMovePositions(self)
        # filter only eat moves
        possible_eat_moves = list(filter(lambda m: m.does_eat, possible_moves)) 
        
        if move.does_eat and len(possible_eat_moves) > 0:
            self.turn_count += 0
            #if len(possible_eat_moves) == 1:
            #    self.makeMove(possible_eat_moves[0])
        else:
            self.turn_count += 1
        self.__updateStatus()

    def __eatPiece(self, piece, eaten, final_position):
        self.hashMapPieces[piece.position] = None
        piece.move(final_position)
        self.hashMapPieces[eaten.position] = None
        self.hashMapPieces[final_position] = piece
        score = 2 if eaten.is_dama else 1
        if piece.color == PieceColor.RED:
            self.red_score += score * self.__score_multiplier
        else:
            self.black_score += score * self.__score_multiplier
            

    def __movePiece(self, piece, position):
        self.hashMapPieces[piece.position] = None
        piece.move(position)
        self.hashMapPieces[position] = piece

    def printHashmap(self):
        # stampa in forma di matrice
        for i in range(self.height):
            for j in range(self.width):
                try:
                    piece = self.hashMapPieces[(i,j)]
                except KeyError:
                    piece = None
                if piece == None:
                    print("0", end=" ")
                else:
                    letter = "r" if piece.color == PieceColor.RED else "b"
                    if piece.is_dama:
                        letter = letter.upper()
                    print(letter, end=" ")
            print()
        
    def isInsideBounds(self, position):
        return position[0] >= 0 and position[0] < self.width and position[1] >= 0 and position[1] < self.height
    
    def makeMoveRedAI(self):
        return self.__makeMoveAI(PieceColor.RED)
    def makeMoveBlackAI(self):
        return self.__makeMoveAI(PieceColor.BLACK)
    
    def __makeMoveAI(self, AI_color : PieceColor):
        moves = []
        for piece in self.hashMapPieces.values():
            if piece is None:
                continue
            if piece.color == AI_color:
                piece_moves = piece.evaluateMovePositions(self)
                moves.extend(piece_moves)
        if len(moves) == 0:
            return None, None
        # filter eat moves
        eat_moves = list(filter(lambda m: m.does_eat, moves))
        if len(eat_moves) > 0:
            move = random.choice(eat_moves)
        else:
            move = random.choice(moves)
        was_dama = move.piece.is_dama
        self.makeMove(move)
        return move, was_dama

        