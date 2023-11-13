
import pygame,datetime,json
import logging, math,random,os
from tkinter import *
from tkinter import messagebox
from classes.logger import Logger
from classes.button import MyButton
from classes.particles import ParticleHandler
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
particle_handler = ParticleHandler()


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


scrollers = [0,0,0,0]
min_speed = 2
parallax_speed = min_speed

def pick_random_parallax_folder():
	path = "data/images/parallax"
	parallaxes = os.listdir(path)
	return random.choice(parallaxes)

bg_images = []
bg_width = 0
current_parallax_name = None
def set_random_parallax():
	global bg_images, bg_width, current_parallax_name
	max_tries = 100
	try_count = 0
	while try_count<max_tries:
		try_count += 1
		parallax_choice = pick_random_parallax_folder()
		if parallax_choice != current_parallax_name:
			break
	current_parallax_name = parallax_choice
	bg_images = []
	for i in range(1, 5):
		bg_image = pygame.image.load(f"data/images/parallax/{parallax_choice}/{i}.png").convert_alpha()
		bg_images.append(bg_image)
	bg_images = [pygame.transform.scale(i, (width, height)) for i in bg_images]
	bg_width = bg_images[0].get_width()

set_random_parallax()

def draw_bg():
	global scrollers
	for i in range(len(scrollers)):
		x = - scrollers[i] 
		canvas.blit(bg_images[i], (x, 0))
		canvas.blit(bg_images[i], (bg_width+ x, 0))



	
def scale_plane(plane):
	scale = width // 6
	plane = pygame.transform.scale(plane, (scale,scale))
	plane = pygame.transform.rotate(plane, -90)
	return plane

plane_name = None
menu_plane = None
def set_random_plane():
	global plane_name,menu_plane
	path = "data/images/planes"
	planes = os.listdir(path)
	max_tries = 100
	try_count = 0
	while try_count<max_tries:
		try_count += 1
		choice = random.choice(planes)
		if choice != plane_name:
			break
	plane_name = choice.split(".")[0].replace("_", " ")
	path = f"{path}/{choice}"
	menu_plane = pygame.image.load(path)
	menu_plane = scale_plane(menu_plane)


set_random_plane()

px = 0
py = 0

while not exit:	

	clock.tick(FPS)
	draw_bg()
	
	if plane_name:
		# write name of plane
		text = default_font.render("Plane: "+ plane_name, True, (255,255,255))
		#left corner top
		text_rect = text.get_rect(center=(width//2, 50))
		canvas.blit(text, text_rect)

	for i in range(len(scrollers)):
		scrollers[i] += (1+ i)*parallax_speed
		scrollers[i] %= bg_width

	#canvas.fill((0,0,0))
	
	mouse_pos = pygame.mouse.get_pos()
	dy =   mouse_pos[1] - py
	dx =   mouse_pos[0] - px
	parallax_speed = min_speed + max( (dx/width)*5 , 0)
	px += dx//65*2  -  ((dx/120) * math.sin(pygame.time.get_ticks()*0.01)) 
	py += dy/65  +  ( math.cos(pygame.time.get_ticks()*0.002)) 

	
	h_speed = -2 * parallax_speed
	particle_handler.add_particle( [px, py+ menu_plane.get_width()//6], [h_speed, 0], random.randint(4, 8))
	particle_handler.add_particle( [px, py- menu_plane.get_width()//6], [h_speed, 0], random.randint(4, 8))
	particle_handler.update()
	particle_handler.draw(canvas)

	canvas.blit(menu_plane, (px - menu_plane.get_width()//2  , py- menu_plane.get_width()//2))


	

	
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
			if event.key == pygame.K_r:
				set_random_plane()
				set_random_parallax()
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

