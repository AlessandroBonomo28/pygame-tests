from tkinter import filedialog
import pygame,datetime,json

from tkinter import *
from tkinter import messagebox

from model.dama import *
from model.player import *
from model.my_button import *
from model.logger import *

# force single instance
from tendo import singleton
me = singleton.SingleInstance()

pygame.init()

width = pygame.display.Info().current_w
height = pygame.display.Info().current_h - pygame.display.Info().current_h//10

cell_width = height/8
start_x_board = 0
start_y_board = 0
text_spacing = cell_width*0.7

bgColor = (255,255,255)
evenCellColor = (128,128,128)#(205,133,63)
oddCellColor = (255,255,255)
bgLogColor = (0,0,0)
redPiecesColor = (255,0,0)
blackPiecesColor = (0,0,0)
colorSelectedPiece = (0,255,0)
suggestedMoveColor = (255,128,128)

piecesRadius = cell_width//2 -10
selectedPieceRadius = piecesRadius +2.5
selectedPieceStroke = 5

player_level_previous_game = None

msBlinkSelector = 500
ticksLastBlinkSelector = 0

selectedPiece = None
suggestedMoves = None

time_elapsed_ms = 0
eat_streak_happening = False

viewing_replay = False

logger = Logger()

def load_replay(path) -> Replay:
	try:
		json_log = logger.read_json(path)
		status = json_log["status"]
		timestamp = datetime.datetime.strptime(json_log["timestamp"],"%Y-%m-%d %H:%M:%S")
		# json_log["duration"] = "0:00:15.789000"
		duration_ms = int(datetime.timedelta(hours=int(json_log["duration"][0]),minutes=int(json_log["duration"][2:4]),seconds=int(json_log["duration"][5:7]),milliseconds=int(json_log["duration"][8:])).total_seconds()*1000)
		black_score = json_log["black_score"]
		red_score = json_log["red_score"]
		turns = json_log["turns"]
		board_hashmaps = json_log["board_hashmaps"]
		return Replay(board_hashmaps, status, timestamp, duration_ms, black_score,red_score,turns)
	except Exception as e:
		print("Error while loading replay",e)
		return None

def load_last_replay() -> Replay:
	try:
		logs = os.listdir(logger.base_path)
		logs.sort()
		if len(logs) > 0:
			last_log = logs[len(logs)-1]
			path = f"{logger.base_path}/{last_log}"
			return load_replay(path)
	except Exception as e:
		print("Error while loading last replay",e)

def play_replay_step(replay : Replay, step : int):
	global board
	try:
		hash = replay.boards_hash[step]
		board.hashMapPieces = {}
		for key in hash.keys():
			x = int(key[1])
			y = int(key[4])
			json_value = json.loads(hash[key])
			is_dama = bool(json_value["is_dama"])
			position = (json_value["position"][0] , json_value["position"][1])
			color = PieceColor.RED if json_value["color"] == "Rosso" else PieceColor.BLACK
			board.hashMapPieces[(x,y)] = Piece(position,color,is_dama)
		if step > 0:
			pygame.mixer.Sound.play(move_sound)
	except Exception as e:
		print("Error while loading replay",e)

step_replay = 0
current_replay = load_last_replay()

def switchReplayMode():
	global viewing_replay, current_replay, step_replay
	viewing_replay = not viewing_replay
	if viewing_replay:
		# se la cartella non esiste
		if not os.path.exists(logger.base_path):
			popUp("Info","Non ci sono partite salvate")
			viewing_replay = False
			return
		if auto_select_last_replay:
			current_replay = load_last_replay()
			if current_replay:
				step_replay = 0
				play_replay_step(current_replay,0)
				pygame.mixer.Sound.play(draw_sound)
				return
			else:
				popUp("Errore","Errore durante il caricamento dell'ultima partita")
				viewing_replay = False
				return
		# apri file browser con tkinter per scegliere il file
		root = Tk()
		root.withdraw()
		root.filename =  filedialog.askopenfilename(initialdir = logger.base_path,title = "Seleziona il file della partita",filetypes = (("json files","*.json"),("all files","*.*")))
		if root.filename:
			replay_loaded = load_replay(root.filename)
			if replay_loaded:
				current_replay = replay_loaded
				play_replay_step(current_replay,0)
				pygame.mixer.Sound.play(draw_sound)
			else:
				popUp("Errore","Errore durante il caricamento della partita")
				viewing_replay = False
		else:
			popUp("Operazione annullata","Nessuna partita selezionata")
			viewing_replay = False
	else:
		resetGame()
		step_replay	= 0
	


def stepForwardReplay():
	global step_replay
	step_replay+=1
	if step_replay >= len(current_replay.boards_hash):
		pygame.mixer.Sound.play(wrong_sound)
		step_replay = len(current_replay.boards_hash)-1
	else:
		play_replay_step(current_replay,step_replay)

def stepBackwardReplay():
	global step_replay
	step_replay-=1
	if step_replay < 0:
		pygame.mixer.Sound.play(wrong_sound)
		step_replay = 0
	else:
		play_replay_step(current_replay,step_replay)

def popUp(title,msg):
	Tk().wm_withdraw() #to hide the main window
	messagebox.showinfo(title,msg)

def resetGame():
	global board, selectedPiece, suggestedMoves, time_elapsed_ms,button_reset
	board.reset()
	time_elapsed_ms = 0
	selectedPiece = None
	suggestedMoves = None
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
		
		if not BLACK_AI_enabled:
			if board.status == GameStatus.BLACK_WINS:
				player.add_win()
			elif board.status == GameStatus.DRAW:
				player.add_draw()
			elif board.status == GameStatus.RED_WINS:
				player.add_loss()
			assign_exp = True
			player_level_previous_game = player.level
			log = GameLog(board.status, datetime.datetime.now(), time_elapsed_ms,
					board.black_score, board.red_score, board.turn_count, board.hashMapList)
			logger.log(log)

def isPlayerTurn():
	return board.whoMoves() == PieceColor.RED and not RED_AI_enabled or \
		board.whoMoves() == PieceColor.BLACK and not BLACK_AI_enabled

def isPlayerVsPlayer():
	return not RED_AI_enabled and not BLACK_AI_enabled

def isPlayerVsAI():
	return (RED_AI_enabled and not BLACK_AI_enabled) or (not RED_AI_enabled and BLACK_AI_enabled)

def isAIvsAI():
	return RED_AI_enabled and BLACK_AI_enabled

def drawSelectedPieceOverMouse():
	global selectedPiece
	if selectedPiece != None:
		if selectedPiece.color == PieceColor.RED:
			pygame.draw.circle(canvas,redPiecesColor,pygame.mouse.get_pos(), piecesRadius)
		else:
			pygame.draw.circle(canvas,blackPiecesColor,pygame.mouse.get_pos(), piecesRadius)
		if selectedPiece.is_dama:
			pygame.draw.circle(canvas,(255,255,0),pygame.mouse.get_pos(), piecesRadius//2)
def drawPieces(board : Board): # draw red circle or black circle
	for piece in board.hashMapPieces.values():
		if piece is None or (piece == selectedPiece and isPlayerTurn()):
			continue
		if piece.color == PieceColor.RED:
			pygame.draw.circle(canvas,redPiecesColor,((piece.position[0]+0.5)*cell_width,(piece.position[1]+0.5)*cell_width), piecesRadius)
		else:
			pygame.draw.circle(canvas,blackPiecesColor,((piece.position[0]+0.5)*cell_width,(piece.position[1]+0.5)*cell_width), piecesRadius)		
		if piece.is_dama:
			pygame.draw.circle(canvas,(255,255,0),((piece.position[0]+0.5)*cell_width,(piece.position[1]+0.5)*cell_width), piecesRadius//2)

def drawCircleAroundSelectedPiece():
	global selectedPiece, ticksLastBlinkSelector
	if selectedPiece != None and (pygame.time.get_ticks() - ticksLastBlinkSelector) > msBlinkSelector:
		pygame.draw.circle(canvas,colorSelectedPiece,((selectedPiece.position[0]+0.5)*cell_width,(selectedPiece.position[1]+0.5)*cell_width), selectedPieceRadius,selectedPieceStroke)
		if (pygame.time.get_ticks() - ticksLastBlinkSelector) > 2*msBlinkSelector:
			ticksLastBlinkSelector = pygame.time.get_ticks()

def drawMovesForSelectedPiece():
	if selectedPiece and suggestedMoves:
		for move in suggestedMoves:
			pygame.draw.circle(canvas,suggestedMoveColor,((move.position_to[0]+0.5)*cell_width,(move.position_to[1]+0.5)*cell_width), selectedPieceRadius,selectedPieceStroke)

textColor = (255,255,255)
def drawTextGameStatus():
	text_x, text_y = 8*cell_width + (width -8*cell_width)//2, 35
	textTurnColor = (0,0,0) if board.whoMoves() == PieceColor.RED else (255,255,255)
	textTurnBgColor = (255,255,255) if board.whoMoves() == PieceColor.RED else (255,0,0)
	if board.whoMoves() == PieceColor.BLACK and not BLACK_AI_enabled:
		textTurn = f"Turno {board.turn_count+1}: Muovi il Nero"
	else: 
		textTurn = f"Turno {board.turn_count+1}: il {board.whoMoves()} muove"

	if board.status != GameStatus.IN_PROGRESS:
		if BLACK_AI_enabled:
			textTurn = f"{board.status}"
		else: 
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

	status_text_color = (255,255,255)
	bg_status_color = (0,0,0)
	msg_replay = "Premi R per rivedere una partita" if not auto_select_last_replay else "Premi R per rivedere la partita"
	text = normalText.render(msg_replay, True, status_text_color,bg_status_color)
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
		score_txt += " per il Nero"
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
	
	if not hide_button_enable_black_AI:
		btn_AI_txt_height = button_enable_black_AI.font.get_height()
		button_enable_black_AI.position = (width-btn_AI_txt_height*1.5,btn_AI_txt_height)
		button_enable_black_AI.draw(canvas)

	text = normalText.render(f"Premi M per mutare la musica", True, textColor, (0,0,0))
	textRect = text.get_rect()
	textRect.center = (text_x, text_y + text_spacing*5)
	canvas.blit(text, textRect)

def drawReplayUI():
	text_x, text_y = 8*cell_width + (width -8*cell_width)//2, 35
	
	if step_replay == len(current_replay.boards_hash)-1:
		textTurn = current_replay.status
		textTurnBgColor = (200,0,0)
		textTurnColor = (255,255,255) 
	elif step_replay == 0:
		textTurnBgColor = (255,255,255) 
		textTurnColor = (0,0,0) 
		textTurn = "Inizio partita"
	else:
		textTurnBgColor = (255,255,255) 
		textTurnColor = (0,0,0) 
		textTurn = f"Mossa N° {step_replay}"

	
	text = fontTurn.render(textTurn, True, textTurnColor, textTurnBgColor)
	textRect = text.get_rect()
	textRect.center = (text_x, text_y)
	canvas.blit(text, textRect)

	
	timer_txt = f"Partita giocata il {current_replay.timestamp}"

	text = normalText.render(timer_txt, True, textColor, (0,0,0))
	textRect = text.get_rect()
	textRect.center = (text_x, text_y + text_spacing)
	canvas.blit(text, textRect)

	status_text_color = (255,255,255)
	bg_status_color = (0,0,0)
	text = normalText.render(f"Durata: {datetime.timedelta(milliseconds=current_replay.duration_ms)}", True, status_text_color,bg_status_color)
	textRect = text.get_rect()
	textRect.center = (text_x, text_y + text_spacing*2)
	canvas.blit(text, textRect)


	if step_replay == len(current_replay.boards_hash)-1:
		min_score = min(current_replay.red_score, current_replay.black_score)
		max_score = max(current_replay.red_score, current_replay.black_score)
		
		score_txt_color = (220,220,0)
		score_txt = f"{max_score} - {min_score}"
		if current_replay.red_score > current_replay.black_score:
			score_txt += " per il Rosso"
		elif current_replay.red_score < current_replay.black_score:
			score_txt += " per il Nero"
		else:
			score_txt += " Pari"	
		text = normalText.render(score_txt, True, score_txt_color, (0,0,0))
		textRect = text.get_rect()
		textRect.center = (text_x, text_y + text_spacing*3)
		canvas.blit(text, textRect)

	
	button_exit_replay.position = (text_x, text_y + text_spacing*4)
	button_exit_replay.draw(canvas)

	text = normalText.render(f"Premi M per mutare la musica", True, textColor, (0,0,0))
	textRect = text.get_rect()
	textRect.center = (text_x, text_y + text_spacing*5)
	canvas.blit(text, textRect)

	text_x = 8*cell_width + (width -8*cell_width)//2
	text_y = height//2 + cell_width//2 +10
	bg = (64,64,0)
	pygame.draw.rect(canvas,bg,(8*cell_width +10, text_y - 30, width-(8*cell_width+20), height-text_y))
	

	
	str_txt = "Clicca le frecce per andare avanti/indietro"
	text = normalText.render(str_txt, True,(255,255,255) ,bg)
	textRect = text.get_rect()
	textRect.center = (text_x, text_y )
	canvas.blit(text, textRect)

	text_y+= text_spacing*2

	arrow_h = 20 *8
	arrow_w = 10 * 8
	# draw left arrow
	pygame.draw.polygon(canvas,(255,255,255),[(text_x-arrow_h,text_y),(text_x-arrow_w,text_y-arrow_w),(text_x-arrow_w,text_y+arrow_w)])
	# draw right arrow
	pygame.draw.polygon(canvas,(255,255,255),[(text_x+arrow_h,text_y),(text_x+arrow_w,text_y-arrow_w),(text_x+arrow_w,text_y+arrow_w)])

	# check click on arrows
	if pygame.mouse.get_pressed()[0]:
		mouse_pos = pygame.mouse.get_pos()
		if mouse_pos[0] > text_x-arrow_h and mouse_pos[0] < text_x-arrow_w and mouse_pos[1] > text_y-arrow_w and mouse_pos[1] < text_y+arrow_w:
			stepBackwardReplay()
			pygame.time.delay(delay_move_replay)
		elif mouse_pos[0] > text_x+arrow_w and mouse_pos[0] < text_x+arrow_h and mouse_pos[1] > text_y-arrow_w and mouse_pos[1] < text_y+arrow_w:
			stepForwardReplay()
			pygame.time.delay(delay_move_replay)

def drawExpBar(x,y):
	w = (width - cell_width*8) - 40
	pygame.draw.rect(canvas,(0,0,0),(x,y,w,cell_width//3))
	pygame.draw.rect(canvas,(0,0,220),(x+cell_width//24,y+cell_width//24,(w-cell_width//24)*(player.experience/player.exp_limit_current_level()),cell_width//4))

def drawTextAutoplay():
	text_x = 8*cell_width + (width -8*cell_width)//2
	text_y = height//2 + cell_width//2 +10
	# draw background rect
	bg = (64,64,0)
	pygame.draw.rect(canvas,bg,(8*cell_width +10, text_y - 30, width-(8*cell_width+20), height-text_y))
	
	str_txt = "Autopilota attivo"
	text = normalText.render(str_txt, True,(255,255,255) ,bg)
	textRect = text.get_rect()
	textRect.center = (text_x, text_y)
	canvas.blit(text, textRect)

	# scrivi un altro testo sotto
	str_txt = "Premi su 'Auto' per disattivarlo"
	text = normalText.render(str_txt, True,(255,255,255) ,bg)
	textRect = text.get_rect()
	textRect.center = (text_x, text_y+text_spacing*1.5)
	canvas.blit(text, textRect)

def drawPlayerStats():
	text_x = 8*cell_width + (width -8*cell_width)//2
	text_y = height//2 + cell_width//2 +10
	bgColorRect = (64,64,64)
	# draw background rect
	pygame.draw.rect(canvas,bgColorRect,(8*cell_width +10, text_y - 30, width-(8*cell_width+20), height-text_y))
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
	
	drawExpBar(8*cell_width + 20, text_y + text_spacing)
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

	text = playerText.render(f"{player.wins} Vinte, {player.losses} Perse, {player.draws} Patte", True, colorPlayerTxt,bgColorRect)
	textRect = text.get_rect()
	textRect.center = (text_x, text_y+ text_spacing*3.5)
	canvas.blit(text, textRect)

def drawPreviousMove():
	previous_move = board.moves[-1] if len(board.moves) > 0 else None
	if previous_move:
		# draw arrow
		pygame.draw.line(canvas,(0,0,255),((previous_move.position_from[0]+0.5)*cell_width,(previous_move.position_from[1]+0.5)*cell_width),((previous_move.position_to[0]+0.5)*cell_width,(previous_move.position_to[1]+0.5)*cell_width),5)
	
def clickedAnyAviableMove(position):
	global suggestedMoves
	if suggestedMoves:
		for move in suggestedMoves:
			if move.position_to == position:
				return move
	return None



audio_enabled = True
pygame.mixer.init()

move_sound = pygame.mixer.Sound("sounds/move.mp3")
win_sound = pygame.mixer.Sound("sounds/win.mp3")
lose_sound = pygame.mixer.Sound("sounds/lose.mp3")
draw_sound = pygame.mixer.Sound("sounds/draw.mp3")
dama_sound = pygame.mixer.Sound("sounds/dama.mp3")
start_game = draw_sound
wrong_sound = pygame.mixer.Sound("sounds/wrong.mp3")
enemy_dama_sound = wrong_sound


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
pygame.display.set_caption("Dama 2023")

try:
	with open("game_settings.json") as f:
		game_settings = json.load(f)
		AI_delay_ms = game_settings["AI_delay_ms"]
		player_name = game_settings["player_name"]
		day_born = game_settings["day_born"]
		month_born = game_settings["month_born"]
		year_born = game_settings["year_born"]
		hide_button_enable_black_AI = game_settings["hide_button_enable_black_AI"]
		auto_select_last_replay = game_settings["auto_select_last_replay"]
		logger.max_logs = game_settings["max_logs"]
		delay_move_replay = game_settings["delay_move_replay"]
except:
	delay_move_replay = 500
	AI_delay_ms = 500
	player_name = "Pippo"
	day_born = 3
	month_born = 9
	year_born = 1934
	hide_button_enable_black_AI = True
	auto_select_last_replay = True
	logger.max_logs = 10

exit = False
RED_AI_enabled = True
BLACK_AI_enabled = False
auto_reset = False
assign_exp = False

player = Player(player_name)

button_exit_replay = myButton("Esci dal replay", (0,0), (0,100,0), (255,255,255), normalText,False,border_color=(255,255,255))
button_reset = myButton("Ricomincia partita", (0,0), (0,100,0), (255,255,255), normalText,False,border_color=(255,255,255))
button_enable_black_AI = myButton("Auto",(0,0), (100,100,0), (255,255,255), playerText,False,border_color=(255,255,255))

# init board
black_pieces = []
red_pieces = []
for i in range(2):
	for j in range(8):
		if (i+j)%2 == 0:
			red_pieces.append(Piece((j,i),PieceColor.RED,False))
			black_pieces.append(Piece((7-j,7-i),PieceColor.BLACK,False))

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

	if board.status == GameStatus.IN_PROGRESS and not viewing_replay:
		if board.whoMoves() == PieceColor.RED and RED_AI_enabled:
			# AI RED
			move, was_dama = board.makeMoveRedAI()
			selectedPiece = None
			suggestedMoves = None
			pygame.time.delay(AI_delay_ms)
			updateGamePostMove()
			if move:
				if not was_dama and move.piece.is_dama:
					pygame.mixer.Sound.play(enemy_dama_sound)
			pygame.mixer.Sound.play(move_sound)
			time_elapsed_ms += AI_delay_ms
			
		elif board.whoMoves() == PieceColor.BLACK and BLACK_AI_enabled:
			# AI BLACK
			move, was_dama = board.makeMoveBlackAI()
			selectedPiece = None
			suggestedMoves = None
			pygame.time.delay(AI_delay_ms)
			updateGamePostMove()
			if move:
				if not was_dama and move.piece.is_dama:
					pygame.mixer.Sound.play(dama_sound)
			pygame.mixer.Sound.play(move_sound)
			time_elapsed_ms += AI_delay_ms
	elif auto_reset and not viewing_replay:
		pygame.time.delay(5000)
		board.reset()
		time_elapsed_ms = 0
		selectedPiece = None
		suggestedMoves = None
	
	for event in pygame.event.get():
		# if resized window
		if event.type == pygame.VIDEORESIZE:
			width = event.w
			height = event.h
			cell_width = height/8
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
			if event.key == pygame.K_r:
				switchReplayMode()
			if event.key == pygame.K_RIGHT and viewing_replay: 
				stepForwardReplay()
			if event.key == pygame.K_LEFT and viewing_replay:
				stepBackwardReplay()
			if event.key == pygame.K_m:
				audio_enabled = not audio_enabled
				if audio_enabled:
					pygame.mixer.music.unpause()
				else:
					pygame.mixer.music.pause()
		if event.type == pygame.MOUSEBUTTONDOWN and button_reset.mouse_over(pygame.mouse.get_pos()) and not viewing_replay:
			resetGame()
			break
		
		if event.type == pygame.MOUSEBUTTONDOWN and button_exit_replay.mouse_over(pygame.mouse.get_pos()) and viewing_replay:
			switchReplayMode()
			break

		# clicked on button enable black AI
		if not hide_button_enable_black_AI and event.type == pygame.MOUSEBUTTONUP and button_enable_black_AI.mouse_over(pygame.mouse.get_pos()) and not viewing_replay:
			BLACK_AI_enabled = not BLACK_AI_enabled
			auto_reset = True if BLACK_AI_enabled else False
			new_color = (0,200,0) if BLACK_AI_enabled else (100,100,0)
			button_enable_black_AI.set_new_color(new_color)
			
		if (event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEBUTTONUP) and isPlayerTurn() and not viewing_replay:
			pos = pygame.mouse.get_pos()

			if board.status != GameStatus.IN_PROGRESS:
				break
			
			ticksLastBlinkSelector = pygame.time.get_ticks() - msBlinkSelector
			cellPosition = mousePositionToCell(pos)
			move = clickedAnyAviableMove(cellPosition)
			
			if event.type == pygame.MOUSEBUTTONUP and suggestedMoves:
				selected_valid_position = False
				for m in suggestedMoves:
					if cellPosition == m.position_to:
						selected_valid_position = True
						break
				if not selected_valid_position:
					selectedPiece = None
					suggestedMoves = None

			if selectedPiece and move != None:
				was_dama = move.piece.is_dama
				board.makeMove(move)
				pygame.mixer.Sound.play(move_sound)
				if not was_dama and move.piece.is_dama: # play sound when becomes dama
					pygame.mixer.Sound.play(dama_sound)	
				updateGamePostMove()
				selectedPiece = None
				suggestedMoves = None
			elif event.type == pygame.MOUSEBUTTONDOWN:
				selectedPiece = board.getPieceByPosition(cellPosition)

				if selectedPiece:
					print(f"Piece can be eaten : {selectedPiece.canBeEaten(board)}")
				
				if selectedPiece and selectedPiece.color == board.whoMoves():
					suggestedMoves = selectedPiece.evaluateMovePositions(board)
					if len(suggestedMoves) == 0:
						selectedPiece = None
						suggestedMoves = None
						print("No moves available for this piece")
						pygame.mixer.Sound.play(wrong_sound)
				elif selectedPiece and selectedPiece.color != board.whoMoves():
					pygame.mixer.Sound.play(wrong_sound)
					selectedPiece = None
					suggestedMoves = None
				else:
					selectedPiece = None
					suggestedMoves = None
			
			if board.whoMoves() == PieceColor.RED and RED_AI_enabled:
				selectedPiece = None
				suggestedMoves = None
	
	try: # eat streak
		last_move = board.moves[len(board.moves)-1]
		if last_move.does_eat and last_move.piece.color == board.whoMoves():
			selectedPiece = last_move.piece
			suggestedMoves = selectedPiece.evaluateMovePositions(board)
			# filtra mosse che mangiano
			suggestedMoves = list(filter(lambda move: move.does_eat, suggestedMoves))
			eat_streak_happening = True
		else:
			eat_streak_happening = False
	except:
		pass
			
	for i in range(board.width):
		for j in range(board.height):
			if (i+j)%2 == 0:
				pygame.draw.rect(canvas,oddCellColor,((start_x_board+i)*cell_width,j*cell_width,cell_width,cell_width))
			else:
				pygame.draw.rect(canvas,evenCellColor,((i+start_x_board)*cell_width,j*cell_width,cell_width,cell_width))
	drawPieces(board)
	pygame.draw.rect(canvas,bgLogColor,(height,0,width-height,height))
	
	if not viewing_replay:
		drawPreviousMove()
		if selectedPiece and isPlayerTurn():
			drawSelectedPieceOverMouse()
			drawCircleAroundSelectedPiece()
			drawMovesForSelectedPiece()
		drawTextGameStatus()

		if isAIvsAI():
			drawTextAutoplay()
			
		else:
			drawPlayerStats()
	else:
		drawReplayUI()
	pygame.display.update()

