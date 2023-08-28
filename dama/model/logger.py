import datetime,os,json
class GameLog:
    status : any
    json_hashmaps : list[any]
    timestamp : datetime.datetime 
    duration_ms : int
    black_score : int
    red_score : int
    turns : int
    def create_json_hashmap_list(self, hashmaps : list[any]) -> str:
        for hash in hashmaps:
            json_hash = {}
            for key in hash:
                if hash.get(key) is None:
                    continue
                json_hash[str(key)] = json.dumps(hash[key].__dict__, indent=4)
            self.json_hashmaps.append(json_hash)
            

    def __init__(self, status, timestamp, duration_ms, black_score,red_score,turns,hashmaps):
        self.black_score = black_score
        self.red_score = red_score
        self.turns = turns
        self.json_hashmaps = []
        self.status = status
        self.timestamp = timestamp
        self.duration_ms = duration_ms
        self.create_json_hashmap_list(hashmaps)

class Logger:
    base_path : str = "logs"
    max_logs : int
    delete_old_logs : bool
    def __init__(self, max_logs = 10, delete_old_logs = True):
        self.max_logs = max_logs
        self.delete_old_logs = delete_old_logs
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
                "board_hashmaps" : game_log.json_hashmaps,
            }
            self.__write_json(path, json_log)
            if self.delete_old_logs:
                self.__delete_old_logs()
        except:
            print("Error while logging")

    def __delete_old_logs(self):
        try:
            logs = os.listdir(self.base_path)
            logs.sort()
            if len(logs) > self.max_logs:
                for i in range(len(logs) - self.max_logs):
                    os.remove(f"{self.base_path}/{logs[i]}")
        except Exception as e:
            print("Error while deleting old logs",e)
    
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
                # dump a list of dumped json
                json.dump(to_write, f, indent=4)
        except Exception as e:
            print("Error while writing json",e)
