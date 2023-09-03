from tkinter import filedialog
import pygame,datetime,json

from tkinter import *
from tkinter import messagebox

from model.battleship import *
from model.player import *
from model.my_button import *

pygame.init()

width = pygame.display.Info().current_w
height = pygame.display.Info().current_h - pygame.display.Info().current_h//10
stroke_divider = 5
color_divider = (0,0,0)
cell_width = height/Board.width
start_x_board = 0
start_y_board = 0
text_spacing = cell_width*0.7

bgColor = (255,255,255)
evenCellColor = (0,49,83)
oddCellColor = (0,33,71)
bgLogColor = (0,0,0)
redPiecesColor = (255,0,0)
blackPiecesColor = (200,200,200)
colorSelectedPiece = (0,255,0)
suggestedMoveColor = (255,128,128)

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
		if board.status == GameStatus.BLACK_WINS:
			pygame.mixer.Sound.play(win_sound)
		elif board.status == GameStatus.DRAW:
			pygame.mixer.Sound.play(draw_sound)
		elif board.status == GameStatus.RED_WINS:
			pygame.mixer.Sound.play(lose_sound)
		
		if board.status == GameStatus.BLACK_WINS:
			player.add_win()
		elif board.status == GameStatus.DRAW:
			player.add_draw()
		elif board.status == GameStatus.RED_WINS:
			player.add_loss()
		assign_exp = True
		player_level_previous_game = player.level

def isPlayerTurn():
	return board.whoMoves() == PieceColor.BLACK 


def drawPieces(board : Board):
	# black
	for piece in board.black_pieces:
		# draw line that connects all positions
		prev_position = None
		for position in piece.positions:
			if prev_position:
				pygame.draw.line(canvas,blackPiecesColor,((prev_position[0]+0.5)*cell_width,(prev_position[1]+0.5)*cell_width),((position[0]+0.5)*cell_width,(position[1]+0.5)*cell_width),math.ceil(piecesRadius*2.5))
			
			pygame.draw.circle(canvas,blackPiecesColor,((position[0]+0.5)*cell_width,(position[1]+0.5)*cell_width), piecesRadius)		
			prev_position = position
	#  red
	for piece in board.red_pieces:
		if not piece.is_dead: # disegna solo i pezzi vivi
			continue
		prev_position = None
		for position in piece.positions:
			if prev_position:
				pygame.draw.line(canvas,redPiecesColor,((prev_position[0]+0.5)*cell_width,(prev_position[1]+0.5)*cell_width),((position[0]+0.5)*cell_width,(position[1]+0.5)*cell_width),math.ceil(piecesRadius*2.5))
			
			pygame.draw.circle(canvas,redPiecesColor,((position[0]+0.5)*cell_width,(position[1]+0.5)*cell_width), piecesRadius)		
			prev_position = position

def drawHits(board : Board):
	# cycle over hit hashmap
	hit_enemy_color = (255,255,255)
	hit_player_color = (0,0,0)
	for position in board.hash_hits:
		# draw cross
		x = (position[0]+0.5)*cell_width
		y = (position[1]+0.5)*cell_width
		color = hit_enemy_color if board.getCellColor(position) == PieceColor.RED else hit_player_color
		pygame.draw.line(canvas,color,(x-piecesRadius,y-piecesRadius),(x+piecesRadius,y+piecesRadius),7)
		pygame.draw.line(canvas,color,(x-piecesRadius,y+piecesRadius),(x+piecesRadius,y-piecesRadius),7)

def drawLastAImiss(board : Board):
	#pick last position of AI
	if len(board.moves) == 0:
		return
	
	last_move = None
	# get last red move
	for i in range(len(board.moves)-1,-1,-1):
		if board.moves[i].actor == PieceColor.RED:
			last_move = board.moves[i]
			break

	if last_move == None:
		#print("Red never moved a piece, cannot draw last move")
		return
	
	if last_move.actor == PieceColor.RED:
		# draw cross
		x = (last_move.position_hit[0]+0.5)*cell_width
		y = (last_move.position_hit[1]+0.5)*cell_width
		pygame.draw.line(canvas,(255,0,0),(x-piecesRadius,y-piecesRadius),(x+piecesRadius,y+piecesRadius),7)
		pygame.draw.line(canvas,(255,0,0),(x-piecesRadius,y+piecesRadius),(x+piecesRadius,y-piecesRadius),7)


def drawYourLastMiss(board : Board):
	global ticksLastBlinkSelector
	if len(board.moves) == 0:
		return
	
	last_move = None
	# get last red move
	for i in range(len(board.moves)-1,-1,-1):
		if board.moves[i].actor == PieceColor.BLACK and board.moves[i].did_hit():
			break
		elif board.moves[i].actor == PieceColor.BLACK and not board.moves[i].did_hit():
			last_move = board.moves[i]
			break

	if last_move == None:
		return
	

	# blink condition (blink distrae e quindi commento)
	#blink_condition = (pygame.time.get_ticks() - ticksLastBlinkSelector) % (msBlinkSelector*2) < msBlinkSelector
	if last_move.actor == PieceColor.BLACK: # and blink_condition:
		# draw circle with inside empty
		x = (last_move.position_hit[0]+0.5)*cell_width
		y = (last_move.position_hit[1]+0.5)*cell_width
		pygame.draw.circle(canvas,(255,255,255),(x,y), piecesRadius,5)
		# draw single cross
		pygame.draw.line(canvas,(255,255,255),(x-piecesRadius,y-piecesRadius),(x+piecesRadius,y+piecesRadius),5)

def drawAim(board : Board):
	aim_color = (0,200,0)
	if board.whoMoves() == PieceColor.BLACK and board.status == GameStatus.IN_PROGRESS:
		# draw red circle with cross 
		mouse_pos = pygame.mouse.get_pos()
		cell = mousePositionToCell(mouse_pos)
		if board.isInsideBounds(cell) and board.getCellColor(cell) == PieceColor.RED:
			x = (cell[0]+0.5)*cell_width
			y = (cell[1]+0.5)*cell_width
			pygame.draw.circle(canvas,aim_color,(x,y), piecesRadius,3)
			# draw single cross vertical horizontal
			pygame.draw.line(canvas,aim_color,(x-piecesRadius,y),(x+piecesRadius,y),3)
			pygame.draw.line(canvas,aim_color,(x,y-piecesRadius),(x,y+piecesRadius),3)

			# draw cell number
			txt_cell = "Casella "
			txt_cell += chr(ord('A')+round(cell[1]))+str(round(cell[0]+1))
			text = normalText.render(txt_cell, True, (255,255,255), (0,0,0))
			textRect = text.get_rect()
			if mouse_pos[1] < cell_width:
				textRect.center = (mouse_pos[0], mouse_pos[1] + 40)
			else:
				textRect.center = (mouse_pos[0], mouse_pos[1] - 40)
			canvas.blit(text, textRect)
		elif board.isInsideBounds(cell) and board.getCellColor(cell) == PieceColor.BLACK:
			# draw text Questa è la tua flotta
			text = normalText.render("Questa è la tua flotta!", True, (255,255,255), (0,0,0))
			textRect = text.get_rect()
			textRect.center = (mouse_pos[0], mouse_pos[1] - 30)
			canvas.blit(text, textRect)

def drawCellNumbers(board : Board):
	for j in range(board.height//2):
		for i in range(board.width):
			# txt cell es A1,B1
			txt_cell = chr(ord('A')+j)+str(i+1)
			color = oddCellColor if (i+j)%2 == 0 else evenCellColor
			text = normalText.render(txt_cell, True, (255,255,255,128), color)
			textRect = text.get_rect()
			textRect.center = ((i+0.5)*cell_width, (j+0.5)*cell_width)
			canvas.blit(text, textRect)

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
	# draw line that divides half board up and down
	half_h = Board.height*cell_width // 2
	pygame.draw.line(canvas,color_divider,(0,half_h),(Board.width*cell_width,half_h),stroke_divider)
textColor = (255,255,255)
def drawTextGameStatus():
	text_x, text_y = Board.height*cell_width + (width -Board.height*cell_width)//2, 35
	textTurnColor = (0,0,0) if board.whoMoves() == PieceColor.RED else (255,255,255)
	textTurnBgColor = (255,255,255) if board.whoMoves() == PieceColor.RED else (255,0,0)
	if board.whoMoves() == PieceColor.BLACK:
		textTurn = f"Turno {board.turn_count+1}: Scegli dove colpire ! "
	else: 
		textTurn = f"Turno {board.turn_count+1}: il {board.whoMoves()} colpisce! "

	if board.status != GameStatus.IN_PROGRESS: 
		textTurn = "Hai perso!" if board.status == GameStatus.RED_WINS else "Hai vinto!" if board.status == GameStatus.BLACK_WINS else "Patta!"
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
	if board.red_pieces_alive == 0:
		status_text_color = (0,0,0)
		bg_status_color = (0,255,0)
		enemy_boats_txt = "Hai distrutto tutte le barche nemiche!"
	elif board.black_pieces_alive == 0:
		enemy_boats_txt = "Tutte le tue barche sono state distrutte!"
		status_text_color = (255,255,255)
		bg_status_color = (255,0,0)
	else:
		
		if board.red_pieces_alive == 1:
			enemy_boats_txt = "Il nemico ha una sola barca ! "
		else:
			enemy_boats_txt = f"Il nemico ha ancora {board.red_pieces_alive} barche"
	
	text = normalText.render(enemy_boats_txt, True, status_text_color,bg_status_color)
	textRect = text.get_rect()
	textRect.center = (text_x, text_y + text_spacing*2)
	canvas.blit(text, textRect)

	min_score = min(board.red_score, board.black_score)
	max_score = max(board.red_score, board.black_score)
	
	score_txt_color = (220,220,0)
	score_txt = f"{max_score} - {min_score}"
	if board.red_score > board.black_score:
		score_txt += " per il Rosso"
	elif board.red_score < board.black_score:
		score_txt += " per te"
	else:
		score_txt += " Pari"	
	text = normalText.render(score_txt, True, score_txt_color, (0,0,0))
	textRect = text.get_rect()
	textRect.center = (text_x, text_y + text_spacing*3)
	canvas.blit(text, textRect)

	if board.status != GameStatus.IN_PROGRESS:
		button_reset.set_blink(True)
	
	button_reset.position = (text_x, text_y + text_spacing*4)
	button_reset.draw(canvas)

	text = normalText.render(f"Premi M per mutare la musica", True, textColor, (0,0,0))
	textRect = text.get_rect()
	textRect.center = (text_x, text_y + text_spacing*5)
	canvas.blit(text, textRect)

def drawExpBar(x,y):
	w = (width - cell_width*Board.height) - 40
	pygame.draw.rect(canvas,(0,0,0),(x,y,w,cell_width//3))
	pygame.draw.rect(canvas,(0,0,220),(x+cell_width//24,y+cell_width//24,(w-cell_width//24)*(player.experience/player.exp_limit_current_level()),cell_width//4))

def drawPlayerStats():
	text_x = Board.height*cell_width + (width -Board.height*cell_width)//2
	text_y = height//2 + cell_width//2 +10
	bgColorRect = (64,64,64)
	# draw background rect
	pygame.draw.rect(canvas,bgColorRect,(Board.height*cell_width +10, text_y - 30, width-(Board.height*cell_width+20), height-text_y))
	colorPlayerTxt = (255,255,255)
	str_txt = f"{player.name} - Livello {player.level}"
	if board.status != GameStatus.IN_PROGRESS and player_level_previous_game != player.level:
		str_txt += f" (+{player.level -player_level_previous_game})"
		colorPlayerTxt = (0,255,0)
	text = normalText.render(str_txt, True,colorPlayerTxt ,bgColorRect)
	colorPlayerTxt = (255,255,255)
	textRect = text.get_rect()
	textRect.center = (text_x, text_y)
	canvas.blit(text, textRect)
	
	drawExpBar(Board.height*cell_width + 20, text_y + text_spacing)
	txt_exp = f"Esperienza: {int(player.experience)}/{int(player.exp_limit_current_level())}"
	txt_exp_color = (255,255,255)
	score_exp = board.black_score*board.get_multiplier()
	if board.status != GameStatus.IN_PROGRESS and score_exp>0:
		txt_exp += f"  +{score_exp} guadagnati!"
		txt_exp_color = (0,255,0)
	text = playerText.render(txt_exp, True, txt_exp_color,bgColorRect)
	textRect = text.get_rect()
	textRect.center = (text_x, text_y+ text_spacing*2)
	canvas.blit(text, textRect)

	text = playerText.render(f"Percentuale vittorie: {int(player.win_percent())}%", True, colorPlayerTxt,bgColorRect)
	textRect = text.get_rect()
	textRect.center = (text_x, text_y+ text_spacing*2.8)
	canvas.blit(text, textRect)

	text = playerText.render(f"{player.wins} Vinte, {player.losses} Perse", True, colorPlayerTxt,bgColorRect)
	textRect = text.get_rect()
	textRect.center = (text_x, text_y+ text_spacing*3.5)
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


pygame.mixer.music.load('loop.mp3')
pygame.mixer.music.play(-1)

fontTurn = pygame.font.SysFont('Comic Sans MS', int(cell_width*0.5))
normalText = pygame.font.SysFont('Comic Sans MS', int(cell_width*0.35))
playerText = pygame.font.SysFont('Comic Sans MS', int(cell_width*0.25))
# CREATING CANVAS
# resizable window

#canvas = pygame.display.set_mode((width,height))
canvas = pygame.display.set_mode((width,height),pygame.RESIZABLE)

icon = pygame.image.load('icon.png')
# make it a square
icon = pygame.transform.scale(icon, (32, 32))
pygame.display.set_icon(icon)

# TITLE OF CANVAS
pygame.display.set_caption("Battaglia navale 2023")

try:
	with open("game_settings.json") as f:
		game_settings = json.load(f)
		AI_delay_ms = game_settings["AI_delay_ms"]
		player_name = game_settings["player_name"]
		day_born = game_settings["day_born"]
		month_born = game_settings["month_born"]
		year_born = game_settings["year_born"]
except:
	AI_delay_ms = 500
	player_name = "Pippo"
	day_born = 3
	month_born = 9
	year_born = 1934

exit = False


assign_exp = False

player = Player(player_name)

button_reset = myButton("Ricomincia partita", (0,0), (0,100,0), (255,255,255), normalText,False,border_color=(255,255,255))


red_pieces = Fleet.generate(PieceColor.RED)
black_pieces = Fleet.generate(PieceColor.BLACK)
board = Board(red_pieces,black_pieces)

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

	if board.status == GameStatus.IN_PROGRESS:
		if board.whoMoves() == PieceColor.RED:
			# AI RED
			print("AI RED moves")
			pygame.time.delay(AI_delay_ms//2)
			move = board.makeMoveRedAI(board)
			pygame.time.delay(AI_delay_ms//2)
			updateGamePostMove()
			if move.did_hit():
				pygame.mixer.Sound.play(boom_sound)
			else:
				pygame.mixer.Sound.play(move_sound)
			time_elapsed_ms += AI_delay_ms
	
	
	for event in pygame.event.get():
		# if resized window
		if event.type == pygame.VIDEORESIZE:
			width = event.w
			height = event.h
			cell_width = height/Board.height
			start_x_board = 0
			start_y_board = 0
			text_spacing = cell_width*0.7
			fontTurn = pygame.font.SysFont('Comic Sans MS', int(cell_width*0.5))
			normalText = pygame.font.SysFont('Comic Sans MS', int(cell_width*0.35))
			playerText = pygame.font.SysFont('Comic Sans MS', int(cell_width*0.25))
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
		
			
		if (event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEBUTTONUP) and isPlayerTurn():
			pos = pygame.mouse.get_pos()

			if board.status != GameStatus.IN_PROGRESS:
				break
			
			cellPosition = mousePositionToCell(pos)
			
			if event.type == pygame.MOUSEBUTTONUP:
				pass
			elif event.type == pygame.MOUSEBUTTONDOWN and board.getPieceByPosition:
				ticksLastBlinkSelector = pygame.time.get_ticks()
				if not board.isInsideBounds(cellPosition):
					print("invalid cell to hit")
					break
				
				if board.getCellColor(cellPosition) == PieceColor.RED:
					piece_to_hit = board.getPieceByPosition(cellPosition)
					if piece_to_hit != None and piece_to_hit.color != board.whoMoves():
						print("piece to hit:",piece_to_hit)
						move = Move(board.turn_count,PieceColor.BLACK,cellPosition,piece_to_hit,"hitted")
					else:
						move = Move(board.turn_count,PieceColor.BLACK,cellPosition,None,"missed")
					board.makeMove(move)
					if move.did_hit():
						pygame.mixer.Sound.play(boom_sound)
					else:
						pygame.mixer.Sound.play(wrong_sound)
					updateGamePostMove()
				else:
					pygame.mixer.Sound.play(wrong_sound)

	drawBoard(board)
	#drawCellNumbers(board)
	drawPieces(board)
	drawHits(board)
	drawLastAImiss(board)
	drawYourLastMiss(board)
	
	# bg of right part of screen
	pygame.draw.rect(canvas,bgLogColor,(height,0,width-height,height))
	
	drawTextGameStatus()
	drawPlayerStats()
	drawAim(board)
	pygame.display.update()

