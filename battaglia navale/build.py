import os
# runs the following command with os, produces the executable in dist folder

name = "Battaglia navale"

os.system(f"pyinstaller game.py --icon=icon.ico --name={name} -y")

# copy game_settings.json to dist folder
os.system(f"copy game_settings.json dist\{name}")

# copy loop.mp3 to dist folder
os.system(f"copy loop.mp3 dist\{name}")
# copy icon.png to dist folder
os.system(f"copy icon.png dist\{name}")
# copy sound directory with all files to dist folder
os.system(f"xcopy sounds dist\{name}\sounds /E /I /Y")