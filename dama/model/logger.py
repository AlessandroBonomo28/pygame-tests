import datetime,os
class GameLog:
    status : any
    timestamp : datetime.datetime 
    duration_ms : int
    def __init__(self, status, timestamp, duration_ms):
        self.status = status
        self.timestamp = timestamp
        self.duration_ms = duration_ms

class Logger:
    base_path : str = "logs"
    def __init__(self):
        pass
    def log(self, game_log : GameLog):
        try:
            filename = datetime.datetime.now().strftime("%Y-%m-%d")
            path = f"{self.base_path}/{filename}.txt"
            formatted_duration = datetime.timedelta(milliseconds=game_log.duration_ms)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "a") as f:
                f.write(f"{game_log.status} - timestamp: {game_log.timestamp} - duration: {formatted_duration}\n")
        except:
            print("Error while logging")