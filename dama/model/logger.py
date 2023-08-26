import datetime,os,json
class GameLog:
    status : any
    json_moves : list[any]
    timestamp : datetime.datetime 
    duration_ms : int
    black_score : int
    red_score : int
    turns : int
    def __moves_to_json(self, moves : list[any]) -> str:
        for move in moves:
            eaten = None if move.piece_to_eat is None else json.dumps(move.piece_to_eat.__dict__)
            json_move = {
                "piece" : json.dumps(move.piece.__dict__),
                "from" : move.position_from,
                "to" : move.position_to,
                "eaten" : eaten,
                "does_eat" : move.does_eat,
            }
            self.json_moves.append(json_move)
            

    def __init__(self, status, timestamp, duration_ms, black_score,red_score,turns,moves):
        self.black_score = black_score
        self.red_score = red_score
        self.turns = turns
        self.json_moves = []
        self.status = status
        self.timestamp = timestamp
        self.duration_ms = duration_ms
        self.__moves_to_json(moves)

class Logger:
    base_path : str = "logs"
    def __init__(self):
        pass
    def log(self, game_log : GameLog):
        try:
            filename = datetime.datetime.now().strftime("%Y-%m-%d %H %M %S")
            path = f"{self.base_path}/{filename}.json"
            formatted_duration = datetime.timedelta(milliseconds=game_log.duration_ms)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            json_log = {
                "status" : game_log.status,
                "timestamp" : game_log.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "duration" : str(formatted_duration),
                "black_score" : game_log.black_score,
                "red_score" : game_log.red_score,
                "turns" : game_log.turns,
                "moves" : game_log.json_moves,
            }
            self.__write_json(path, json_log)
        except:
            print("Error while logging")

    def __read_json(self, path) -> list:
        try:
            with open(path, "r") as f:
                return json.load(f)
        except:
            print("Error while reading json list")
            return []
        
    def __write_json(self, path, to_write : list):
        try:
            with open(path, "w") as f:
                json.dump(to_write, f,indent=4)
        except:
            print("Error while writing json")

    def __append_to_json_list(self, path, item):
        list_to_write = self.__read_json(path)
        list_to_write.append(item)
        self.__write_json(path, list_to_write)


"""logger = Logger()
from model.dama import Move,Piece,PieceColor
piece1 = Piece((0,0),PieceColor.RED,False)
piece2 = Piece((7,7),PieceColor.BLACK,False)
moves = [
    Move(piece1, (0,0), (2,2),"move"),
    Move(piece2, (7,7), (6,6),"move"),
]
logger.log(GameLog("test",datetime.datetime.now(), 1000,moves=moves))"""