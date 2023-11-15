
import pygame,datetime,json
import logging, math,random,os
from tkinter import *
from tkinter import messagebox
from classes.logger import Logger
from classes.button import MyButton
from classes.particles import ParticleHandler
from classes.animation import Animation
from classes.plane import Plane
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
shoot_sound = pygame.mixer.Sound("data/sounds/shooting.mp3")
damage1_sound = pygame.mixer.Sound("data/sounds/damage1.mp3")
damage2_sound = pygame.mixer.Sound("data/sounds/damage2.wav")

# trim damage
raw_array = damage2_sound.get_raw()
raw_array = raw_array[12000:30000]
damage2_sound = pygame.mixer.Sound(buffer=raw_array)

# trim shootsound

raw_array = shoot_sound.get_raw()
raw_array = raw_array[0:120000]
shoot_sound = pygame.mixer.Sound(buffer=raw_array)
shoot_sound.set_volume(0.6)
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


def load_tileset(filename, width, height):
	image = pygame.image.load(filename).convert_alpha()
	image_width, image_height = image.get_size()
	tileset = []
	for tile_x in range(0, image_width//width):
		line = []
		tileset.append(line)
		for tile_y in range(0, image_height//height):
			rect = (tile_x*width, tile_y*height, width, height)
			 

			line.append(image.subsurface(rect))
	return tileset

tileset = load_tileset("data/images/bullets/All_Fire_Bullet_Pixel_16x16_00.png", 16, 16)    
bullet = tileset[6][10]


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


explosion_group = pygame.sprite.Group()


scrollers = [0,0,0,0]
min_speed = 5
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
player = None


def load_random_plane(current=None):
	path = "data/images/planes"
	planes = os.listdir(path)
	max_tries = 100
	try_count = 0
	while try_count<max_tries:
		try_count += 1
		choice = random.choice(planes)
		if choice != current:
			break
	plane_name = choice.split(".")[0].replace("_", " ")
	path = f"{path}/{choice}"
	plane = pygame.image.load(path)
	plane = scale_plane(plane)
	return (plane, plane_name)

def set_random_plane():
	global plane_name,player
	player, plane_name = load_random_plane(plane_name)

enemy_plane_sprite, enemy_plane_name = load_random_plane()
enemy_plane_pos = [width - 100  , height//2 ]


Plane.particle_handler = particle_handler
enemy_plane = Plane(enemy_plane_pos,enemy_plane_sprite,enemy_plane_name)

set_random_plane()

px = 0
py = 0
hit_count = 0
distance = 0
shoot = False
bullet_life = 8
bullet_tag =1

enemies = [enemy_plane]

while not exit:	



	clock.tick(FPS)
	
	
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
				enemy_plane.sprite = load_random_plane(enemy_plane_name)[0]
			if event.key == pygame.K_m:
				audio_enabled = not audio_enabled
				if audio_enabled:
					pygame.mixer.music.unpause()
				else:
					pygame.mixer.music.pause()
					#mouse hold down
		if event.type == pygame.MOUSEBUTTONDOWN:
			shoot = True
			# play loop
			shoot_sound.play(-1)

		if event.type == pygame.MOUSEBUTTONUP:
			shoot = False
			shoot_sound.stop()
			#get mouse position
			
	
	draw_bg()
	

	text = default_font.render(f"Travelled: {round(distance,1)} km, Hits: {hit_count}", True, (255,255,255))
	text_rect = text.get_rect(center=(150, 50))
	canvas.blit(text, text_rect)
	if plane_name:
		# write name of plane
		text = default_font.render(f"Plane: {plane_name}", True, (255,255,255))
		text_rect = text.get_rect(center=(width//2, 50))
		canvas.blit(text, text_rect)

	for i in range(len(scrollers)):
		scrollers[i] += (1+ i**1.1)*parallax_speed
		scrollers[i] %= bg_width

	#canvas.fill((0,0,0))
	
	mouse_pos = pygame.mouse.get_pos()
	dy =   mouse_pos[1] - py
	dx =   mouse_pos[0] - px
	
	vertical_speed = 1/65*3
	parallax_speed = min_speed + max( (dx/width)*5 , 0)
	px += dx//65*2  -  ((dx/120) * math.sin(pygame.time.get_ticks()*0.01)) 
	py += dy*vertical_speed  +  ( math.cos(pygame.time.get_ticks()*0.002)) 

	
	h_speed = -2 * parallax_speed
	particle_handler.add_particle( [px, py+ player.get_width()//6], [h_speed, 0], random.randint(4, 8))
	particle_handler.add_particle( [px, py- player.get_width()//6], [h_speed, 0], random.randint(4, 8))
	
	if pygame.time.get_ticks() % 100 < 50 and shoot:
		particle_handler.add_particle( [px, py+ player.get_width()//10], [-h_speed*2, 0], bullet_life,bullet,bullet_tag)
		particle_handler.add_particle( [px, py- player.get_width()//10], [-h_speed*2, 0], bullet_life,bullet,bullet_tag)
	

	
	# draw circle collider
	#pygame.draw.circle(canvas, (255, 255, 255), [int(target[0]), int(target[1])], int(radius_target), 1)

	particle_handler.update()
	particle_handler.draw(canvas)

	# collision check for particles with an image
	for particle in particle_handler.particles:
		if particle[4] == bullet_tag:
			x = particle[0][0] 
			y = particle[0][1] 
			if x > width or x < 0 or y > height or y < 0:
				particle_handler.particles.remove(particle)
				continue
			for enemy in enemies:
				radius_target = enemy.sprite.get_width()//4
				target = enemy.pos
				if ((x-target[0])**2 + (y-target[1])**2 ) < (radius_target + particle[3].get_width())**2:
					particle_handler.particles.remove(particle)
					#logging.debug("hit "+str(hit_count))
					xoff =random.randint(50, 70)
					yoff = random.randint(-20, 20)
					size = random.randint(10, 30)
					explosion = Animation(x+xoff,y+yoff,"data/images/explosion",3,size)
					explosion_group.add(explosion)
					hit_count += 1
					enemy.damage(1)
					damage2_sound.play()

	for enemy in enemies:
		enemy.velocity = [-2*parallax_speed,0]
		enemy.update()
		enemy.draw(canvas)
	
	canvas.blit(player, (px - player.get_width()//2  , py- player.get_width()//2))
	
	explosion_group.draw(canvas)
	explosion_group.update()
	
	pygame.display.update()
	
	#speed 509 km/h
	distance += clock.get_time() * 509 / 1000 / 60 / 60	

