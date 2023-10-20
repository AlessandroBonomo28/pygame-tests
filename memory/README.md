# Memory
In this game you have to guess and remember couples of cards with the same number.When the game starts, all the cards are uncovered for 10 seconds,
then you have to uncover and guess them 2 at a time. The game ends when you guessed all the cards.

## Telegram updates
The game sends updates to a **Telegram bot**. In order to make it work, you have to create a `.env` file with the following content:
```
TOKEN_TELEGRAM = "xxxxxxx"
WHITELIST_ID_TELEGRAM = "aaaa,bbbb,cccc,ddddd"
```
The `WHITELIST_ID_TELEGRAM` is a string separated by commas. It contains the allowed *telegram IDs* that will receive updates about the game.
