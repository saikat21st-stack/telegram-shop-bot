import logging
import random
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = os.environ.get("TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))

logging.basicConfig(level=logging.INFO)

stock = {"binance": [], "coinbase": []}
photo_stock = {"binance": [], "coinbase": []}

def menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛒 Buy", callback_data="buy")],
        [InlineKeyboardButton("📦 Stock", callback_data="stock")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 AUTO SHOP BOT 🔥", reply_markup=menu())

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if q.data == "buy":
        kb = [
            [InlineKeyboardButton("Binance", callback_data="buy_binance")],
            [InlineKeyboardButton("Coinbase", callback_data="buy_coinbase")]
        ]
        await q.edit_message_text("Select product:", reply_markup=InlineKeyboardMarkup(kb))

    elif q.data.startswith("buy_"):
        product = q.data.split("_")[1]

        if len(photo_stock.get(product, [])) > 0:
            photo = photo_stock[product].pop(0)
            await q.message.reply_photo(photo=photo, caption="✅ Delivered instantly")

        elif len(stock.get(product, [])) > 0:
            acc = stock[product].pop(0)
            await q.message.reply_text(f"✅ Delivered:\n{acc}")

        else:
            await q.edit_message_text("❌ Out of stock")

    elif q.data == "stock":
        text = "📦 Stock:\n\n"
        for p in stock:
            text += f"{p} → {len(stock[p]) + len(photo_stock[p])}\n"
        await q.edit_message_text(text)

async def addstock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    product = context.args[0]
    acc = " ".join(context.args[1:])
    stock.setdefault(product, []).append(acc)
    await update.message.reply_text("✅ Added")

async def addphoto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    product = context.args[0]
    context.user_data["photo_product"] = product
    await update.message.reply_text("📸 Send photo")

async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid == ADMIN_ID and "photo_product" in context.user_data:
        product = context.user_data["photo_product"]
        photo_id = update.message.photo[-1].file_id
        photo_stock.setdefault(product, []).append(photo_id)
        context.user_data.pop("photo_product")
        await update.message.reply_text("✅ Photo stock added")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("addstock", addstock))
app.add_handler(CommandHandler("addphoto", addphoto))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.PHOTO, photo))

app.run_polling()
