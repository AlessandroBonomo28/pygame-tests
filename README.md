# Game prototyping using pygame library
In this repo there are some games I developed to keep my grandpa entertained during the day and some more experiments. You can download the executables on my itch.io page: https://alex-8bit.itch.io/
## Instructions to run/build
Python 3 is required. 
- Go inside a game folder
- Create a virtual environment with `python -v venv env`
- Check if the project requires a `.env` file, if so configure it following the README instructions
- run the environment

```
If you are using windows Windows

> ./env/Scripts/activate

If you are using Linux

> source env/bin/activate
```
- install dependencies with `pip install -r requirements.txt`

*Now you can run any python file in the folder*

- run `game.py` (dev mode).
- run `build.py` to build an exe into dist/ folder.
- edit `game_settings.json`
- edit `data/player.json`
