from tkinter import filedialog
import pygame,datetime,json,threading,os

from tkinter import *
from tkinter import messagebox
from model.logger import *
from model.memory import *
from model.player import *
from model.my_button import *

# telegram stuff
import telepot
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

USE_WHITELIST = True
TOKEN_TELEGRAM = os.getenv('TOKEN_TELEGRAM') # Your token from Telegram Botfather
WHITELIST = os.getenv('WHITELIST').split(',') # telegram allowed users ['id 1','id 2']


def on_chat_message(msg):
	try:
		content_type, chat_type, chat_id = telepot.glance(msg)
		if USE_WHITELIST and str(chat_id) not in WHITELIST:
			bot.sendMessage(chat_id, f"I can't share my knowledge with you ⛔.\nMaybe if you give this ID {chat_id} to the right person I will...")
			return
		if content_type == 'text':
			if msg["text"] == "/ping": 
				bot.sendMessage(chat_id, 'pong 🏓')
	except Exception as e:
		print("Error while handling chat message",e)

boot_time = datetime.datetime.now()
bot = telepot.Bot(TOKEN_TELEGRAM)
bot.message_loop(on_chat_message)

def broadcast_to_whitelist(msg):
	try:
		for chat_id in WHITELIST:
			bot.sendMessage(chat_id, msg)
	except Exception as e:
		print("Error while broadcasting to whitelist",e)

broadcast_to_whitelist("Nonno Pippo sta giocando a Memory! 🚀")

# end telegram stuff


logger = Logger()

try:
	with open("game_settings.json") as f:
		game_settings = json.load(f)
		AI_delay_ms = game_settings["AI_delay_ms"]
		player_name = game_settings["player_name"]
		day_born = game_settings["day_born"]
		month_born = game_settings["month_born"]
		year_born = game_settings["year_born"]
		hard_mode = game_settings["hard_mode"]
		side_board = game_settings["side_board"]
		sec_show_all_cards = game_settings["seconds_show_all_cards"]
except:
	AI_delay_ms = 500
	player_name = "Pippo"
	day_born = 3
	month_born = 9
	year_born = 1934
	hard_mode = False
	side_board = 14
	sec_show_all_cards = 10


Board.width = Board.height = side_board

pygame.init()

width = pygame.display.Info().current_w
height = pygame.display.Info().current_h - pygame.display.Info().current_h//10
stroke_divider = 5
color_divider = (0,0,0)
cell_width = height/Board.width
start_x_board = 0
start_y_board = 0
text_spacing = cell_width*1.1

bgColor = (255,255,255)
evenCellColor = (99, 6, 6)
oddCellColor = (137, 15, 13)
bgLogColor = (0,0,0)

selectedCard = None
card_show_list = []
colorSelectedPiece = (255,255,0)

showing_cards = False
piecesRadius = cell_width//2 -10
selectedPieceRadius = piecesRadius +2.5
selectedPieceStroke = 8

player_level_previous_game = None

msBlinkSelector = 500
ticksLastBlinkSelector = 0


sec_hide_previous_move = 5

time_elapsed_ms = 0
played_today =0 


def popUp(title,msg):
	Tk().wm_withdraw() #to hide the main window
	messagebox.showinfo(title,msg)

def resetGame():
	global board,time_elapsed_ms,button_reset, showing_cards,time_start_show,last_timer,card_show_list
	card_show_list = []
	board.reset()
	time_elapsed_ms = 0
	button_reset.set_blink(False)
	button_reset.set_original_color()
	pygame.mixer.Sound.play(start_game)

	showing_cards = True
	# timer to hide all cards
	def hide_all_cards():
		global showing_cards, time_start_show
		showing_cards = False
	time_start_show = pygame.time.get_ticks()
	if last_timer and last_timer.is_alive():
		last_timer.cancel()
	last_timer = threading.Timer(sec_show_all_cards, hide_all_cards)
	last_timer.start()

def mousePositionToCell(position):
	return (position[0]//cell_width, position[1]//cell_width)

def drawSelectedCard():
	global selectedCard
	if selectedCard:
		# draw circle with cross 
		x = (selectedCard.position[0]+0.5)*cell_width
		y = (selectedCard.position[1]+0.5)*cell_width
		pygame.draw.circle(canvas,colorSelectedPiece,(x,y), selectedPieceRadius,selectedPieceStroke)

def games_today():
	# leggi da logs/ e conta i file con data odierna
	try:
		logs = os.listdir("logs")
		logs.sort()
		today = datetime.datetime.now().strftime("%Y-%m-%d")
		count = 0
		for log in logs:
			if log.startswith(today):
				count += 1
		return count
	except:
		return 0
	

def updateGamePostMove():
	global assign_exp, player_level_previous_game,played_today
	
	if board.status != GameStatus.IN_PROGRESS:
		if board.status == GameStatus.WIN:
			pygame.mixer.Sound.play(win_sound)
			player.add_win()
			log = GameLog(board.status,datetime.datetime.now(),time_elapsed_ms,board.score,board.turn_count)
			logger.log(log)
			played_today = games_today()
			msg = f"""
			Nonno Pippo ha vinto una partita a memory! 🎉\n
			- Partite totali: {player.total_games()}
			- Durata partita: {datetime.timedelta(milliseconds=time_elapsed_ms)}
			- Numero di mosse: {board.turn_count}
			- Partite giocate oggi: {played_today}
			"""
			broadcast_to_whitelist(msg)
		elif board.status == GameStatus.DRAW:
			pygame.mixer.Sound.play(draw_sound)
			player.add_draw()
		elif board.status == GameStatus.LOSE:
			pygame.mixer.Sound.play(lose_sound)
			player.add_loss()
		
		played_today = games_today()
		assign_exp = True
		player_level_previous_game = player.level

# loag image pygame
card_back_img = pygame.image.load('card_back.png')
card_front_img = pygame.image.load('card_front.png')
card_front_guessed = pygame.image.load('card_front_guessed.png')
def drawCard(card : Card):
	show_card :bool = card.guessed or card in card_show_list or showing_cards
	if not show_card:
		card_img = card_back_img
	elif card.guessed:
		card_img = card_front_guessed
	else:
		card_img = card_front_img

	offset = 5
	img = pygame.transform.scale(card_img, (int(cell_width)-offset, int(cell_width)-offset))
	canvas.blit(img, (card.position[0]*cell_width,card.position[1]*cell_width))

	if show_card:
			# draw text at center of cell with hash 
			x = (card.position[0]+0.5)*cell_width
			y = (card.position[1]+0.5)*cell_width
			bgColCard = (255,255,255) if not card.guessed else (0,209,0)
			txt = fontTurn.render(str(card.hashed_id), True, (0,0,0), bgColCard)
			txtRect = txt.get_rect()
			txtRect.center = (x, y)
			canvas.blit(txt, txtRect)
			#drawCross(card.position,(255,255,255),(0,0,0))
			card_img = card_front_img
	


def drawPieces(board : Board):
	global card_show_list
	for card in board.cards:
		drawCard(card)
		

def drawCross(position,color_outline,color_cross):
	# draw cross with outline
	x = (position[0]+0.5)*cell_width
	y = (position[1]+0.5)*cell_width
	# outline
	
	pygame.draw.line(canvas,color_outline,(x-piecesRadius,y-piecesRadius - 2),(x+piecesRadius,y+piecesRadius +2),20)
	pygame.draw.line(canvas,color_outline,(x-piecesRadius,y+piecesRadius +2),(x+piecesRadius,y-piecesRadius -2),20)
	
	pygame.draw.line(canvas,color_cross,(x-piecesRadius,y-piecesRadius),(x+piecesRadius,y+piecesRadius),10)
	pygame.draw.line(canvas,color_cross,(x-piecesRadius,y+piecesRadius),(x+piecesRadius,y-piecesRadius),10)
	

def drawAim(board : Board):
	aim_color = (255,255,0)
	if board.status == GameStatus.IN_PROGRESS:
		# draw red circle with cross 
		mouse_pos = pygame.mouse.get_pos()
		cell = mousePositionToCell(mouse_pos)
		if board.isInsideBounds(cell):
			x = (cell[0]+0.5)*cell_width
			y = (cell[1]+0.5)*cell_width
			pygame.draw.circle(canvas,aim_color,(x,y), piecesRadius,3)


def drawBoard(board :Board):
	for i in range(board.width):
		for j in range(board.height):
			if (i+j)%2 == 0:
				x1 = (start_x_board+i)*cell_width
				y1 = j*cell_width
				pygame.draw.rect(canvas,oddCellColor,(x1,y1,cell_width+1,cell_width+1))
			else:
				x1 = (i+start_x_board)*cell_width
				y1 = j*cell_width
				pygame.draw.rect(canvas,evenCellColor,(x1,y1,cell_width+1,cell_width+1))
	
textColor = (255,255,255)
def drawTextGameStatus():
	text_x, text_y = Board.width*cell_width + (width -Board.width*cell_width)//2, 35
	textTurnColor = (0,0,0)
	textTurnBgColor = (255,255,255)

	textTurn = f"Turno {board.turn_count+1}"

	if board.status != GameStatus.IN_PROGRESS: 
		textTurn = "Hai perso!" if board.status == GameStatus.LOSE else "Hai vinto!" if board.status == GameStatus.WIN else "Patta!"
		textTurnColor = (255,255,255)
		textTurnBgColor = (255,0,0)
	text = fontTurn.render(textTurn, True, textTurnColor, textTurnBgColor)
	textRect = text.get_rect()
	textRect.center = (text_x, text_y)
	if board.status != GameStatus.IN_PROGRESS:
		canvas.blit(text, textRect)

	
	time_elapsed_s = (time_elapsed_ms//1000) 
	time_elapsed_m = (time_elapsed_s//60)
	time_elapsed_h = time_elapsed_m//60
	if time_elapsed_h > 0:
		timer_txt = f"Tempo: {time_elapsed_h} ore, {time_elapsed_m%60} min, {time_elapsed_s%60} sec"
	elif time_elapsed_m > 0:
		timer_txt = f"Tempo: {time_elapsed_m%60} min, {time_elapsed_s%60} sec"
	else:
		timer_txt = f"Tempo: {time_elapsed_s%60} sec"

	text = normalText.render(timer_txt, True, textColor, (0,0,0))
	textRect = text.get_rect()
	textRect.center = (text_x, text_y + text_spacing)
	canvas.blit(text, textRect)
	
	status_text_color = (255,255,255) if showing_cards else (0,0,0)
	bg_status_color = (200,0,0) if showing_cards else (200,200,0)
	time_elapsed_hide = pygame.time.get_ticks() - time_start_show
	secs = sec_show_all_cards - (time_elapsed_hide//1000)
	txt_warn = f"ATTENDI {secs} secondi..." if showing_cards else "Seleziona le coppie"
	text = normalText.render(txt_warn, True, status_text_color,bg_status_color)
	textRect = text.get_rect()
	textRect.center = (text_x, text_y + text_spacing*2)
	canvas.blit(text, textRect)
	score_txt_color = (255,255,255)
	score_txt = f"Mancano {Board.height**2 //2- board.score} coppie"
	text = normalText.render(score_txt, True, score_txt_color, (0,0,0))
	textRect = text.get_rect()
	textRect.center = (text_x, text_y + text_spacing*3)
	canvas.blit(text, textRect)

	if board.status != GameStatus.IN_PROGRESS:
		button_reset.set_blink(True)
	
	button_reset.position = (text_x, text_y + text_spacing*4)
	button_reset.draw(canvas)



def drawPlayerStats():
	text_x, text_y = Board.width*cell_width + (width -Board.width*cell_width)//2, 35
	text_y = board.height * cell_width//2
	color = (255,255,255)
	bgColorRect = (0,0,0)
	msg = f"Oggi hai giocato {played_today} partite, bravo Nonno"
	if played_today == 0:
		msg = "Non hai ancora vinto oggi, forza!"
	text = playerText.render(msg, True, color,bgColorRect)
	textRect = text.get_rect()
	textRect.center = (text_x, text_y+ text_spacing*2.5)
	canvas.blit(text, textRect)

def drawPreviousMove():
	previous_move = board.moves[-1] if len(board.moves) > 0 else None
	if previous_move:
		# draw arrow
		pygame.draw.line(canvas,(0,0,255),((previous_move.position_from[0]+0.5)*cell_width,(previous_move.position_from[1]+0.5)*cell_width),((previous_move.position_to[0]+0.5)*cell_width,(previous_move.position_to[1]+0.5)*cell_width),5)


audio_enabled = True
pygame.mixer.init()

move_sound = pygame.mixer.Sound("sounds/move.mp3")
win_sound = pygame.mixer.Sound("sounds/win.mp3")
lose_sound = pygame.mixer.Sound("sounds/lose.mp3")
draw_sound = pygame.mixer.Sound("sounds/draw.mp3")
boom_sound = pygame.mixer.Sound("sounds/boom.mp3")
start_game = draw_sound
wrong_sound = pygame.mixer.Sound("sounds/wrong.mp3")
good_sound = pygame.mixer.Sound("sounds/good.mp3")
big_boom = pygame.mixer.Sound("sounds/big_boom.mp3")

pygame.mixer.music.load('loop.mp3')
pygame.mixer.music.play(-1)

fontTurn,normalText,playerText = None,None,None

def setFont():
	global fontTurn,normalText,playerText
	fontTurn = pygame.font.SysFont('Comic Sans MS', int(cell_width*0.5))
	normalText = pygame.font.SysFont('Comic Sans MS', int(cell_width*0.4))
	playerText = pygame.font.SysFont('Comic Sans MS', int(cell_width*0.25))
setFont()

# CREATING CANVAS
# resizable window

#canvas = pygame.display.set_mode((width,height))
canvas = pygame.display.set_mode((width,height),pygame.RESIZABLE)

icon = pygame.image.load('icon.png')
# make it a square
icon = pygame.transform.scale(icon, (32, 32))
pygame.display.set_icon(icon)

# TITLE OF CANVAS
pygame.display.set_caption("Memory 2023")


exit = False
print("hard mode:",hard_mode)

assign_exp = False
last_timer = None
time_start_show = 0
player = Player(player_name)

button_reset = myButton("Ricomincia partita", (0,0), (0,100,0), (255,255,255), normalText,False,border_color=(255,255,255))

def hash(x):
	return (x % (Board.width**2 // 2)) +1

cards = []
for i in range(Board.width):
	for j in range(Board.height):
		hashed_id = hash(i*Board.width+j)
		pos = (i,j)
		cards.append(Card(pos,hashed_id))
board = Board(cards)
resetGame()


now = datetime.datetime.now()
if now.day == day_born and now.month == month_born:
	pygame.mixer.music.pause()
	pygame.mixer.Sound.play(win_sound)
	str_now = now.strftime("%d/%m/%Y")
	years = now.year - year_born
	popUp("Oggi, "+str_now+" è un giorno speciale!",f"Buon {years}° compleanno {player.name}!")
	pygame.mixer.music.unpause()

while not exit:	
	if board.status == GameStatus.IN_PROGRESS and board.turn_count > 0:
		time_elapsed_ms += pygame.time.Clock().tick(60)
	elif assign_exp:
		assign_exp = False
		player.add_exp(board.score)
	canvas.fill(bgColor)

	
	for event in pygame.event.get():
		# if resized window
		if event.type == pygame.VIDEORESIZE:
			width = event.w
			height = event.h
			cell_width = height/Board.width
			start_x_board = 0
			start_y_board = 0
			text_spacing = cell_width * 1.1
			setFont()
			piecesRadius = cell_width//2 -10
			selectedPieceRadius = piecesRadius +2.5
			canvas = pygame.display.set_mode((width,height),pygame.RESIZABLE)
		
		if event.type == pygame.QUIT:
			#delta con boot time
			delta = datetime.datetime.now() - boot_time
			# format in duration
			delta = datetime.timedelta(seconds=delta.seconds)
			broadcast_to_whitelist(f"Nonno Pippo si è sfasteriato e ha chiuso il gioco dopo {delta} 😢")
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
		if event.type == pygame.MOUSEBUTTONDOWN and button_reset.mouse_over(pygame.mouse.get_pos()):
			resetGame()
			break
		
			
		if (event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEBUTTONUP) :
			pos = pygame.mouse.get_pos()
			

			if board.status != GameStatus.IN_PROGRESS:
				break
			
			cellPosition = mousePositionToCell(pos)
			
			if event.type == pygame.MOUSEBUTTONUP:
				pass
			elif event.type == pygame.MOUSEBUTTONDOWN and board.getCardByPosition:
				ticksLastBlinkSelector = pygame.time.get_ticks()
				if not board.isInsideBounds(cellPosition):
					print("invalid cell to hit")
					selectedCard = None
					break

				if showing_cards:
					pygame.mixer.Sound.play(wrong_sound)
					break

				if board.getCardByPosition(cellPosition).guessed:
					pygame.mixer.Sound.play(wrong_sound)
					selectedCard = None
					break
				if selectedCard == None:
					selectedCard = board.getCardByPosition(cellPosition)
					pygame.mixer.Sound.play(move_sound)
				else:
					pygame.mixer.Sound.play(move_sound)
					# second card selected
					secondCard = board.getCardByPosition(cellPosition)
					if secondCard == selectedCard:
						pygame.mixer.Sound.play(wrong_sound)
						break
					move = Move(board.turn_count,(selectedCard,secondCard),"move")
					board.makeMove(move)
					if move.did_guess():
						pygame.mixer.Sound.play(good_sound)
					else:
						pygame.mixer.Sound.play(wrong_sound)
						if not hard_mode:
							card_show_list = []
						card_show_list.append(selectedCard)
						card_show_list.append(secondCard)
						# deselect after time using threading timer
						def deselect():
							global card_show_list
							# dequeue 2
							try:
								card_show_list.pop(0)
								card_show_list.pop(0)
							except:
								pass
						if hard_mode:
							last_timer = threading.Timer(sec_hide_previous_move, deselect).start()

					selectedCard = None
					updateGamePostMove()
				

	drawBoard(board)
	#drawCellNumbers(board)
	drawPieces(board)
	drawAim(board)
	drawSelectedCard()
	# bg of right part of screen
	pygame.draw.rect(canvas,bgLogColor,(height,0,width-height,height))
	
	drawTextGameStatus()
	drawPlayerStats()
	pygame.display.update()

