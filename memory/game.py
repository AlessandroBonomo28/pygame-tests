from tkinter import filedialog
import pygame,datetime,json

from tkinter import *
from tkinter import messagebox

from model.memory import *
from model.player import *
from model.my_button import *


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
except:
	AI_delay_ms = 500
	player_name = "Pippo"
	day_born = 3
	month_born = 9
	year_born = 1934
	hard_mode = False
	side_board = 14


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
evenCellColor = (0,49,83)
oddCellColor = (0,33,71)
bgLogColor = (0,0,0)

colorSelectedPiece = (0,255,0)


piecesRadius = cell_width//2 -10
selectedPieceRadius = piecesRadius +2.5
selectedPieceStroke = 5

player_level_previous_game = None

msBlinkSelector = 500
ticksLastBlinkSelector = 0



time_elapsed_ms = 0
kill_streak_happening = False



def popUp(title,msg):
	Tk().wm_withdraw() #to hide the main window
	messagebox.showinfo(title,msg)

def resetGame():
	global board,   time_elapsed_ms,button_reset
	board.reset()
	time_elapsed_ms = 0
	button_reset.set_blink(False)
	button_reset.set_original_color()
	pygame.mixer.Sound.play(start_game)

def mousePositionToCell(position):
	return (position[0]//cell_width, position[1]//cell_width)


def updateGamePostMove():
	global assign_exp, player_level_previous_game
	if board.status != GameStatus.IN_PROGRESS:
		if board.status == GameStatus.WIN:
			pygame.mixer.Sound.play(win_sound)
			player.add_win()
		elif board.status == GameStatus.DRAW:
			pygame.mixer.Sound.play(draw_sound)
			player.add_draw()
		elif board.status == GameStatus.LOSE:
			pygame.mixer.Sound.play(lose_sound)
			player.add_loss()
		
			
		assign_exp = True
		player_level_previous_game = player.level


def drawPieces(board : Board):
	for card in board.cards:
		# draw text at center of cell with hash 
		x = (card.position[0]+0.5)*cell_width
		y = (card.position[1]+0.5)*cell_width
		txt = fontTurn.render(str(card.hashed_id), True, (0,0,0), (255,255,255))
		txtRect = txt.get_rect()
		txtRect.center = (x, y)
		canvas.blit(txt, txtRect)
		#drawCross(card.position,(255,255,255),(0,0,0))

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
	aim_color = (0,200,0)
	if board.status == GameStatus.IN_PROGRESS:
		# draw red circle with cross 
		mouse_pos = pygame.mouse.get_pos()
		cell = mousePositionToCell(mouse_pos)
		if board.isInsideBounds(cell):
			x = (cell[0]+0.5)*cell_width
			y = (cell[1]+0.5)*cell_width
			pygame.draw.circle(canvas,aim_color,(x,y), piecesRadius,3)
			# draw single cross vertical horizontal
			pygame.draw.line(canvas,aim_color,(x-piecesRadius,y),(x+piecesRadius,y),3)
			pygame.draw.line(canvas,aim_color,(x,y-piecesRadius),(x,y+piecesRadius),3)


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
		textTurn = "Hai perso!" if board.status == GameStatus.WIN else "Hai vinto!" if board.status == GameStatus.LOSE else "Patta!"
		textTurnColor = (255,255,255)
		textTurnBgColor = (255,0,0)
	text = fontTurn.render(textTurn, True, textTurnColor, textTurnBgColor)
	textRect = text.get_rect()
	textRect.center = (text_x, text_y)
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
	
	status_text_color = (0,0,0)
	bg_status_color = (200,200,0)
	enemy_boats_txt = "Indovina le coppie di carte"
	text = normalText.render(enemy_boats_txt, True, status_text_color,bg_status_color)
	textRect = text.get_rect()
	textRect.center = (text_x, text_y + text_spacing*2)
	canvas.blit(text, textRect)
	score_txt_color = (255,255,255)
	score_txt = f"Mancano {board.score} coppie"
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
	text_y += text_spacing*4
	color = (255,255,255)
	bgColorRect = (0,0,0)
	text = playerText.render(f"Giocate {player.total_games()} partite in totale", True, color,bgColorRect)
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
	normalText = pygame.font.SysFont('Comic Sans MS', int(cell_width*0.5))
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

player = Player(player_name)

button_reset = myButton("Ricomincia partita", (0,0), (0,100,0), (255,255,255), normalText,False,border_color=(255,255,255))

def hash(x):
	return x% Board.width

cards = []
for i in range(Board.width):
	for j in range(Board.height):
		cards.append(Card((i,j),hash(i+j)))
board = Board(cards)



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
		player.add_exp(board.black_score)
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
					break
				
				
				"""if board.getCellColor(cellPosition) == PieceColor.RED:
					piece_to_hit = board.getCardByPosition(cellPosition)
					if piece_to_hit != None and piece_to_hit.color != board.whoMoves():
						print("piece to hit:",piece_to_hit)
						move = Move(board.turn_count,PieceColor.BLACK,cellPosition,piece_to_hit,"hitted")
					else:
						move = Move(board.turn_count,PieceColor.BLACK,cellPosition,None,"missed")
					board.makeMove(move)
					if move.did_hit() and piece_to_hit.is_dead:
						pygame.mixer.Sound.play(big_boom)
					elif move.did_hit():
						pygame.mixer.Sound.play(boom_sound)
					else:
						pygame.mixer.Sound.play(wrong_sound)
					updateGamePostMove()
				else:
					pygame.mixer.Sound.play(wrong_sound)"""

	drawBoard(board)
	#drawCellNumbers(board)
	drawPieces(board)
	
	# bg of right part of screen
	pygame.draw.rect(canvas,bgLogColor,(height,0,width-height,height))
	
	drawTextGameStatus()
	drawPlayerStats()
	drawAim(board)
	pygame.display.update()

