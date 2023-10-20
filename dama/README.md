# Dama
Classico gioco della dama per passare il tempo.
### game_settings.json
```
{ 
  "AI_delay_ms": 750,
  "day_born": 3, 
  "month_born": 9, 
  "year_born": 1934, 
  "player_name": "Pippo", 
  "hide_button_enable_black_AI": true,
  "auto_select_last_replay": true, 
  "max_logs": 10 
}
```
- `AI_delay_ms`: ritardo temporale della mossa del computer
- `day_born, month_born, year_born`: data di nascita per fare gli auguri il giorno del compleanno
- `player_name`: nome del giocatore (se il nome non viene modificato nel gioco allora modificalo nel file data/player.json)
- `hide_button_enable_black_AI`: imposta a false per mostrare il pulsante che abilita la modalità spettatore
- `auto_select_last_replay`: imposta a false per disattivare l'auto select dell'ultimo replay, in questo modo il gioco ti chiederà di scegliere il file del replay che vuoi riprodurre dalla cartella logs/
- `max_logs`: numero massimo di replay da conservare nella cartella **logs/**

