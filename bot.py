import os
import re
import json
import argparse
import asyncio
from dotenv import load_dotenv
from telegram import Update, MessageOriginChannel
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from telethon import TelegramClient

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')

if not (BOT_TOKEN and API_ID and API_HASH):
    raise RuntimeError('BOT_TOKEN, API_ID and API_HASH must be set in the environment')

API_ID = int(API_ID)

# Telethon client for accessing messages
client = TelegramClient('comment_session', API_ID, API_HASH)

POST_URL_RE = re.compile(r'https?://t\.me/(c/)?([^/]+)/(?P<msg>\d+)')


def parse_post_url(url: str):
    """Return chat_id and message_id extracted from a post URL."""
    m = POST_URL_RE.search(url)
    if not m:
        return None
    chat_id = int('-100' + m.group(2)) if m.group(1) else m.group(2)
    msg_id = int(m.group('msg'))
    return chat_id, msg_id

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Send me a forwarded post or a post link and I will return the comments in JSON.')

async def collect_comments(chat_id: int, msg_id: int) -> list[dict]:
    """Collect comments for a given channel message."""
    comments = []
    async with client:
        async for msg in client.iter_messages(chat_id, reply_to=msg_id):
            comments.append({
                'id': msg.id,
                'user_id': msg.sender_id,
                'text': msg.text
            })
    return comments

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message
    chat_id = None
    msg_id = None

    if message.forward_origin:
        origin = message.forward_origin
        if isinstance(origin, MessageOriginChannel):
            chat_id = origin.chat.id
            msg_id = origin.message_id
    elif message.text:
        result = parse_post_url(message.text)
        if result:
            chat_id, msg_id = result

    if chat_id and msg_id:
        comments = await collect_comments(chat_id, msg_id)
        await message.reply_text(
            json.dumps(comments, ensure_ascii=False, indent=2)
        )
    else:
        await message.reply_text('Please forward a channel post or send a post link.')


def main() -> None:
    parser = argparse.ArgumentParser(description='Telegram comment collector bot')
    parser.add_argument('--test', metavar='URL', help='collect comments for the given post and exit')
    args = parser.parse_args()

    if args.test:
        result = parse_post_url(args.test)
        if not result:
            raise SystemExit('Invalid post URL')
        chat_id, msg_id = result
        comments = asyncio.run(collect_comments(chat_id, msg_id))
        print(json.dumps(comments, ensure_ascii=False, indent=2))
        return

    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))
    application.run_polling()

if __name__ == '__main__':
    main()
