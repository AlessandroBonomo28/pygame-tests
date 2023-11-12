
import pygame,datetime,json
import logging
from tkinter import *
from tkinter import messagebox
from classes.logger import Logger
logging.basicConfig(level = logging.DEBUG)

# force single instance
from tendo import singleton
me = singleton.SingleInstance()

try:
	with open("data/settings.json") as f:
		game_settings = json.load(f)
		player_name = game_settings["player_name"]
		day_born = game_settings["day_born"]
		month_born = game_settings["month_born"]
		year_born = game_settings["year_born"]
except:
	player_name = "Pippo"
	day_born = 3
	month_born = 9
	year_born = 1934

clock = pygame.time.Clock()
boot_time = datetime.datetime.now()

logger = Logger()



pygame.init()

width = pygame.display.Info().current_w
height = pygame.display.Info().current_h 

def popUp(title,msg):
	Tk().wm_withdraw() #to hide the main window
	messagebox.showinfo(title,msg)


audio_enabled = True
pygame.mixer.init()


win_sound = pygame.mixer.Sound("data/sounds/win.mp3")
lose_sound = pygame.mixer.Sound("data/sounds/lose.mp3")
boom_sound = pygame.mixer.Sound("data/sounds/boom.mp3")
start_game = pygame.mixer.Sound("data/sounds/start.mp3")
wrong_sound = pygame.mixer.Sound("data/sounds/wrong.mp3")
good_sound = pygame.mixer.Sound("data/sounds/good.mp3")
boom_sound = pygame.mixer.Sound("data/sounds/boom.mp3")

pygame.mixer.music.load('data/music/loop.mp3')
pygame.mixer.music.play(-1)

font_size = 20
game_font = pygame.font.SysFont('Comic Sans MS', font_size)





# CREATING CANVAS
# resizable window

canvas = pygame.display.set_mode((width,height-50), pygame.RESIZABLE)


icon = pygame.image.load('icon.png')
# make it a square
icon = pygame.transform.scale(icon, (32, 32))
pygame.display.set_icon(icon)

# TITLE OF CANVAS
pygame.display.set_caption("Planes 2023")
logging.debug(f"{player_name} ha aperto il gioco")

exit = False


now = datetime.datetime.now()
if now.day == day_born and now.month == month_born:
	pygame.mixer.music.pause()
	pygame.mixer.Sound.play(win_sound)
	str_now = now.strftime("%d/%m/%Y")
	years = now.year - year_born
	popUp("Oggi, "+str_now+" è un giorno speciale!",f"Buon {years}° compleanno {player_name}!")
	pygame.mixer.music.unpause()

while not exit:	
	
	canvas.fill((0,0,0))

	
	for event in pygame.event.get():
		# if resized window
		if event.type == pygame.VIDEORESIZE:
			width = event.w
			height = event.h
			canvas = pygame.display.set_mode((width,height),pygame.RESIZABLE)
		
		if event.type == pygame.QUIT:
			#delta con boot time
			delta = datetime.datetime.now() - boot_time
			# format in duration
			delta = datetime.timedelta(seconds=delta.seconds)
			logging.debug(f"{player_name} ha chiuso il gioco dopo {delta} 😢")
			exit = True
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:
				exit = True
			if event.key == pygame.K_s:
				showing_cards = not showing_cards
			if event.key == pygame.K_m:
				audio_enabled = not audio_enabled
				if audio_enabled:
					pygame.mixer.music.unpause()
				else:
					pygame.mixer.music.pause()
		if event.type == pygame.MOUSEBUTTONDOWN:
			logging.debug("resetting game")
			break
		
			
				

	pygame.display.update()

