
class PieceColor:
    RED = 0
    BLACK = 1


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
                        move = Move(self, self.position, check_position, "eat", True)
                        moves.append(move) # free position
                    else:
                        continue
                else:
                    continue
            else: # out of bounds
                continue

        return moves
    
    def __str__(self):
        col = "Red" if self.color == PieceColor.RED else "Black"
        return col+" "+str(self.steps) + " " + str(self.position)


class Move:
    piece : Piece
    position_from : tuple
    position_to : tuple
    does_eat : bool
    message : str
    def __init__(self, piece, position_from,position_to, message,does_eat = False):
        self.piece = piece
        self.position_from = position_from
        self.position_to = position_to
        self.does_eat = does_eat
        self.message = message

    def __str__(self):
        msg = self.message + " " + str(self.position_from) + " -> " + str(self.position_to)
        if self.does_eat:
            msg += " (can eat)"
        return msg
class Board:
    height : int = 8
    width : int = 8
    turn_count : int = 1
    moves : list[Move] = []
    hashMapPieces : dict[tuple, Piece] = {}
    def __init__(self, pieces_red : list[Piece],pieces_black : list[Piece]):
        for piece in pieces_red:
            self.hashMapPieces[piece.position] = piece
        for piece in pieces_black:
            self.hashMapPieces[piece.position] = piece

    def getPieceByPosition(self,position) -> Piece | None:
        try:
            return self.hashMapPieces[position]
        except KeyError:
            return None
    
    def eatPiece(self, piece, eaten):
        self.hashMapPieces[piece.position] = None
        piece.move(eaten.position)
        self.hashMapPieces[eaten.position] = piece
        self.turn_count += 1

    def movePiece(self, piece, position):
        self.hashMapPieces[piece.position] = None
        piece.move(position)
        self.hashMapPieces[position] = piece
        self.turn_count += 1

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
    
    