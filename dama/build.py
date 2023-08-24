import os
# runs the following command with os, produces the executable in dist folder


os.system("pyinstaller game.py")

# copy game_settings.json to dist folder
os.system("copy game_settings.json dist\game")

# copy loop.mp3 to dist folder
os.system("copy loop.mp3 dist\game")

# copy sound directory with all files to dist folder
os.system("xcopy sounds dist\game\sounds /E /I /Y")