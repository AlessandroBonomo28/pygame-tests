import os
# runs the following command with os, produces the executable in dist folder
#pyinstaller game.py --add-data "loop.mp3;game_settings.json;."

os.system("pyinstaller game.py --add-data \"loop.mp3;game_settings.json;.\"")