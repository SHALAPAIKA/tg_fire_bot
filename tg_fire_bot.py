import logging
import json
import random
from pathlib import Path
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# 🔑 Твой токен и ID
TOKEN = "8061629633:AAHR_ZJC1LRinp-PUfjFoeJsdgcIHge3F6s"
OWNER_ID = 1431532712  # 👈 замени на свой Telegram ID

# 📂 Файлы для хранения данных
USERS_FILE = Path("users.json")
ADMINS_FILE = Path("admins.json")
EMOJI_FILE = Path("emoji.json")

logging.basicConfig(level=logging.WARNING)

# 🔹 Работа с данными
def load_data(file, default):
    if file.exists():
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    return default

def save_data(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

users = load_data(USERS_FILE, [])
admins = load_data(ADMINS_FILE, [OWNER_ID])
emoji_data = load_data(EMOJI_FILE, {"emoji": "🔥"})

def is_admin(user_id: int) -> bool:
    return user_id in admins

# 🔹 Команды
async def addall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    global users
    users = context.args
    save_data(USERS_FILE, users)
    await update.message.reply_text(f"✅ Добавлено пользователей: {len(users)}")

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    if context.args:
        users.extend(context.args)
        save_data(USERS_FILE, users)
        await update.message.reply_text("✅ Пользователь добавлен")

async def dell(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    if context.args:
        user = context.args[0]
        if user in users:
            users.remove(user)
            save_data(USERS_FILE, users)
            await update.message.reply_text(f"❌ {user} удалён")
        else:
            await update.message.reply_text("⚠️ Пользователь не найден")

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    global users
    users = []
    save_data(USERS_FILE, users)
    await update.message.reply_text("🧹 Список очищен")

async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    if users:
        await update.message.reply_text("\n".join(users))
    else:
        await update.message.reply_text("⚠️ Список пуст")

async def fire(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not users:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="⚠️ Список пуст")
        return
    chosen = random.choice(users)
    # Отправляем эмодзи
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=f"{emoji_data['emoji']}")
    # Отправляем сообщение с выбранным пользователем
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=f"Фортуна выбрала тебя\n{chosen}")


async def addadm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    if context.args:
        try:
            new_admin_id = int(context.args[0])
            if new_admin_id not in admins:
                admins.append(new_admin_id)
                save_data(ADMINS_FILE, admins)
                await update.message.reply_text(f"✅ Новый админ добавлен: {new_admin_id}")
        except ValueError:
            await update.message.reply_text("⚠️ Неверный ID")

async def emo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    if context.args:
        emoji_data["emoji"] = context.args[0]
        save_data(EMOJI_FILE, emoji_data)
        await update.message.reply_text(f"✅ Эмодзи изменено на {emoji_data['emoji']}")

def get_help_text():
    return f"""
📌 Список команд:
/addall user1 user2 ... – добавить список пользователей
/add user – добавить одного пользователя
/dell user – удалить пользователя
/clear – очистить список
/list – показать список пользователей
/fire – выбрать случайного пользователя и отправить в группу
/addadm user_id – добавить администратора (только владелец)
/emo 😀 – сменить эмодзи
/help – показать эту справку

👑 Администраторы: {admins}
👥 Пользователей в списке: {len(users)}
"""

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    await update.message.reply_text(get_help_text())

# 🔹 Основная функция
def main():
    app = Application.builder().token(TOKEN).build()

    # Команды
    app.add_handler(CommandHandler("addall", addall))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("dell", dell))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(CommandHandler("list", list_users))
    app.add_handler(CommandHandler("fire", fire))
    app.add_handler(CommandHandler("addadm", addadm))
    app.add_handler(CommandHandler("emo", emo))
    app.add_handler(CommandHandler("help", help_command))

    print("🚀 Бот запущен!")
    print(get_help_text())

    # запуск бота
    app.run_polling()

if __name__ == "__main__":
    main()
