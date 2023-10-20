# Battaglia navale
Classico gioco della Battaglia navale per passare il tempo.
### game_settings.json
```
{ 
  "AI_delay_ms": 10, 
  "day_born": 3, 
  "month_born": 9,
  "year_born": 1934,   
  "player_name": "Pippo",  
  "hard_mode" : false,   
  "alternate_turns": false,  
  "side_board" : 14 
}
```
- `AI_delay_ms`: ritardo temporale della mossa del computer
- `day_born, month_born, year_born`: data di nascita per fare gli auguri il giorno del compleanno
- `player_name`: nome del giocatore (se il nome non viene modificato nel gioco allora modificalo nel file data/player.json)
- `hard_mode`: imposta a true per attivarla. In hard mode viene mostrata solo l'ultima posizione dove hai sparato, ottimo per allenare la memoria
- `alternate_turns`: se impostata a true, allora il gioco non dà turni bonus quando colpisci una nave nemica.
- `side_board`: imposta la larghezza della board (solo numeri pari, consiglio minori o uguali a 20 e maggiori o uguali a 12)

