# Telegram Comment Collector Bot

This repository provides a simple Telegram bot that collects comments for a given channel post. The bot works when you forward a post from a channel or send a link to a post. It replies with the comments in JSON format.

## Setup

1. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
2. Create a `.env` file with the following variables:
   ```
   BOT_TOKEN=your_bot_token
   API_ID=your_api_id
   API_HASH=your_api_hash
   ```
   `BOT_TOKEN` is obtained from [BotFather](https://t.me/BotFather). `API_ID` and `API_HASH` are obtained from [my.telegram.org](https://my.telegram.org).

3. Run the bot:
   ```bash
   python bot.py
   ```

## Usage

Send the bot a forwarded post or a link to the post. The bot will respond with collected comments in a structured JSON format.
