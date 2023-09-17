import datetime,os,json
class GameLog:
    status : any
    timestamp : datetime.datetime 
    duration_ms : int
    score : int
    turns : int
    
            

    def __init__(self, status, timestamp, duration_ms, score, turns):
        self.status = status
        self.timestamp = timestamp
        self.duration_ms = duration_ms
        self.score = score
        self.turns = turns


class Logger:
    base_path : str = "logs"
    max_logs : int
    delete_old_logs : bool
    def __init__(self, max_logs = 1000, delete_old_logs = True):
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
                "score" : game_log.score,
                "turns" : game_log.turns
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
    
    def read_json(self, path) -> list:
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