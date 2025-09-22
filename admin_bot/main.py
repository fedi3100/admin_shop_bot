import logging
import os
import sys
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("ADMIN_BOT_TOKEN", "YOUR_ADMIN_BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 6146268714))

orders = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return await update.message.reply_text("Unauthorized.")
    await update.message.reply_text("👑 Admin bot ready!\nUse /send [details] [user_id] or /orders")


async def handle_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    order_id = f"order_{int(datetime.now().timestamp())}"
    orders[order_id] = {
        "user_id": user.id,
        "username": user.username,
        "full_name": user.full_name,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "pending",
    }
    await context.bot.send_message(
        ADMIN_ID,
        f"📦 New order!\nID: {order_id}\nUser: {user.full_name} (@{user.username})\nUser ID: {user.id}",
    )
    await update.message.reply_text("✅ Screenshot forwarded to admin.")


async def send_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return await update.message.reply_text("❌ Unauthorized")
    if not context.args or len(context.args) < 2:
        return await update.message.reply_text("Usage: /send [details] [user_id]")

    user_id = context.args[-1]
    product = " ".join(context.args[:-1])
    try:
        await context.bot.send_message(chat_id=int(user_id), text=f"🎉 Your SMTP:\n{product}")
        await update.message.reply_text("✅ Sent successfully.")
    except Exception as e:
        await update.message.reply_text(f"❌ Failed: {e}")


async def show_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return await update.message.reply_text("❌ Unauthorized")

    pending = {k: v for k, v in orders.items() if v["status"] == "pending"}
    if not pending:
        return await update.message.reply_text("📋 No pending orders.")

    msg = "📋 Pending Orders:\n\n" + "\n".join(
        [f"{oid}: {o['full_name']} ({o['status']})" for oid, o in pending.items()]
    )
    await update.message.reply_text(msg)


def main():
    logger.info(f"Starting admin_bot with Python {sys.version}")
    if sys.version_info >= (3, 12):
        logger.error("python-telegram-bot v20.x is not compatible with Python 3.12+. Use Python 3.11.9.")
        raise SystemExit(1)

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("send", send_product))
    app.add_handler(CommandHandler("orders", show_orders))
    app.add_h_
