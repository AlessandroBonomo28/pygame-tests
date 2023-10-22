# Memory
In this game you have to guess and remember couples of cards with the same number.When the game starts, all the cards are uncovered for 10 seconds,
then you have to uncover and guess them 2 at a time. The game ends when you guessed all the cards.
### game_settings.json
```
{    
   "day_born": 3,   
   "month_born": 9, 
   "year_born": 1934,    
   "player_name": "Pippo", 
   "hard_mode" : false, 
   "side_board" : 14 ,
   "seconds_show_all_cards":10
} 
```
- `day_born, month_born, year_born`: data di nascita per fare gli auguri il giorno del compleanno
- `player_name`: nome del giocatore (se il nome non viene modificato nel gioco allora modificalo nel file data/player.json)
- `hard_mode`: imposta a true per attivarla. In hard mode le carte scoperte vengono coperte dopo pochi secondi
- `side_board`: imposta la larghezza della board e quindi il numero di carte
- `seconds_show_all_cards`: imposta il tempo per ricordare le carte all'inizio della partita
## Telegram updates
The game sends updates to a **Telegram bot**. In order to make it work, you have to create a `.env` file with the following content:
```
TOKEN_TELEGRAM = "xxxxxxx"
WHITELIST_ID_TELEGRAM = "aaaa,bbbb,cccc,ddddd"
```
The `WHITELIST_ID_TELEGRAM` is a string separated by commas. It contains the allowed *telegram IDs* that will receive updates about the game.

![telegram](https://github.com/AlessandroBonomo28/pygame-tests/assets/75626033/8acdf45e-fb48-4b6b-bee7-27e0bc2f12cb)


