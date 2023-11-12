
import pygame,datetime,json
import logging, math,random
from tkinter import *
from tkinter import messagebox
from classes.logger import Logger
from classes.button import MyButton
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
FPS = 60
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

default_font_size = 20
font_size_btn = 40
default_font = pygame.font.SysFont('Comic Sans MS', default_font_size)
btn_font = pygame.font.SysFont('Comic Sans MS', font_size_btn)




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


btn_start = MyButton("START", position_center=(width // 2, height // 2), 
					 bg_color=(0,0,0), text_color=(255,255,255), font=btn_font,border_stroke=2,
					 border_color=(255,255,255))

scroll = 0


bg_images = []
for i in range(1, 5):
	bg_image = pygame.image.load(f"data/images/parallax/{i}.png").convert_alpha()
	bg_images.append(bg_image)
bg_images = [pygame.transform.scale(i, (width, height)) for i in bg_images]
bg_width = bg_images[0].get_width()
# scale image to fit screen


def draw_bg():
	global scroll
	
	x = 0
	speed = 1
	for i in bg_images:
		xdraw = (x * bg_width) - scroll * speed
		canvas.blit(i, (xdraw, 0))
		speed += 0

		canvas.blit(i, (bg_width+ xdraw, 0))

	

		
plane_img = pygame.image.load("data/images/planes/GER_bf109.png")		
px = 0
py = 0
scale = width // 6
plane_img = pygame.transform.scale(plane_img, (scale,scale))
# rotate 90

plane_img = pygame.transform.rotate(plane_img, -90)
while not exit:	

	clock.tick(FPS)

	#draw world
	draw_bg()

	scroll += 2
	scroll %= bg_width
	

	#canvas.fill((0,0,0))
	btn_start.draw(canvas)
	mouse_pos = pygame.mouse.get_pos()
	sign = -1 if pygame.time.get_ticks() % 5000 < 2000 else 1
	dy =   mouse_pos[1] - py
	dx =   mouse_pos[0] - px
	px += dx//65  -  ((dx/120) * math.sin(pygame.time.get_ticks()*0.003)) 
	py += dy/65  +  ((dy/40) * math.cos(pygame.time.get_ticks()*0.006)) - sign*math.cos(pygame.time.get_ticks()*0.013)

	canvas.blit(plane_img, (px, py))
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
			if event.key == pygame.K_m:
				audio_enabled = not audio_enabled
				if audio_enabled:
					pygame.mixer.music.unpause()
				else:
					pygame.mixer.music.pause()
		if event.type == pygame.MOUSEBUTTONDOWN:
			#get mouse position
			pos = pygame.mouse.get_pos()
			if btn_start.mouse_over(pos):
				logging.debug("start")
			break
		
			
				

	pygame.display.update()

