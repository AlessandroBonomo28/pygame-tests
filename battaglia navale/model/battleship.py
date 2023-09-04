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
            new_dx = round(dx * math.cos(rad_angle) - dy * math.sin(rad_angle))
            new_dy = round(dx * math.sin(rad_angle) + dy * math.cos(rad_angle))
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
    height : int = 14
    width : int = 14
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
    alternate_turns : bool = False
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
        red_pieces = Fleet.generate(PieceColor.RED)
        black_pieces = Fleet.generate(PieceColor.BLACK)
        self.__init__(red_pieces,black_pieces)

    def get_multiplier(self):
        return self.__score_multiplier
    
    def randomPlace(self,piece)-> bool:
        max_try = 10000
        try_count = 0
        rotations = [0,90,180,270]
        piece.rotate(random.choice(rotations))
        while try_count < max_try:
            add_x = random.randint(-self.width-1,self.width-1)
            add_y = random.randint(-self.height//2,self.height//2)
            valid = True
            for position in piece.positions:
                x = position[0] + add_x
                y = position[1] + add_y

                wrong_side = (y < self.height//2 and piece.color == PieceColor.BLACK) or \
                                (y >= self.height//2 and piece.color == PieceColor.RED)
                piece_at_position = self.getPieceByPosition((x,y))
                free_position = piece_at_position == None or piece_at_position == piece
                if not self.isInsideBounds((x,y)) or wrong_side or not free_position:
                    valid = False
                    break
            if valid:
                for position in piece.positions:
                    p = (position[0] + add_x, position[1] + add_y)
                    piece.positions[piece.positions.index(position)] = p
                return True
            try_count +=1
        return False

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
            if self.alternate_turns:
                self.turn_count += 1
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
    
    def __get_move_that_hits(self,board) -> Move:
        for position in board.black_pieces:
                if not position.is_dead:
                    for coord in position.positions:
                        if coord not in board.hash_hits.keys():
                            move = Move(self.turn_count, PieceColor.RED, coord, position, "random move AI")
                            self.makeMove(move)
                            return move
        return None
    def makeMoveRedAI(self,board):
        luck = min(0.05 + self.turn_count/500, 0.75)
        if self.__event_probability(luck):
            move = self.__get_move_that_hits(board)
            if move != None:
                return move

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
                (never_hit_before and self.__event_probability(probability_trigger) \
                 and near_other_black_boats):
                break
            try_count += 1
        move = Move(self.turn_count, PieceColor.RED, random_position, piece_hit, "random move AI")
        self.makeMove(move)
        print(f"AI move: {move}")
        return move

class Fleet:
    
    @staticmethod
    def get_default_black_fleet() -> list[Piece]:
        color_fleet = PieceColor.BLACK
        gommone_1 = Piece([(0,0 + Board.height//2),(0,1 + Board.height//2)],color_fleet)
        gommone_2 = Piece([(1,0 + Board.height//2),(1,1 + Board.height//2)],color_fleet)

        bombardiere = Piece([(2,0 + Board.height//2),(2,1 + Board.height//2),(2,2 + Board.height//2),(2,3 + Board.height//2)],color_fleet)
        portaerei = Piece([(3,0 + Board.height//2),(3,1 + Board.height//2),(3,2 + Board.height//2),(3,3 + Board.height//2),(3,4 + Board.height//2)],color_fleet)
        nave_assalto_1 = Piece([(4,0 + Board.height//2),(4,1 + Board.height//2),(4,2 + Board.height//2)],color_fleet)
        nave_assalto_2 = Piece([(5,0 + Board.height//2),(5,1 + Board.height//2),(5,2 + Board.height//2)],color_fleet)
        return [gommone_1,gommone_2,bombardiere,portaerei,nave_assalto_1,nave_assalto_2]
    
    @staticmethod
    def get_default_red_fleet() -> list[Piece]:
        color_fleet = PieceColor.RED
        gommone_1 = Piece([(0,0),(0,1)],color_fleet)
        gommone_2 = Piece([(1,0),(1,1)],color_fleet)

        bombardiere = Piece([(2,0),(2,1),(2,2),(2,3)],color_fleet)
        portaerei = Piece([(3,0),(3,1),(3,2),(3,3),(3,4)],color_fleet)
        nave_assalto_1 = Piece([(4,0),(4,1),(4,2)],color_fleet)
        nave_assalto_2 = Piece([(5,0),(5,1),(5,2)],color_fleet)
        return [gommone_1,gommone_2,bombardiere,portaerei,nave_assalto_1,nave_assalto_2]

    @staticmethod
    def generate(color_fleet : PieceColor) -> list[Piece]:
        fleet = Fleet.get_default_black_fleet() if color_fleet == PieceColor.BLACK else Fleet.get_default_red_fleet()
        if color_fleet == PieceColor.BLACK:
            test_board = Board([],fleet)
        else:
            test_board = Board(fleet,[])

        for piece in fleet:
            placed = test_board.randomPlace(piece)
            if not placed:
                print("Could not place piece, loading default fleet")
                return Fleet.get_default_black_fleet() if color_fleet == PieceColor.BLACK else Fleet.get_default_red_fleet()

        return test_board.black_pieces if color_fleet == PieceColor.BLACK else test_board.red_pieces          
        
