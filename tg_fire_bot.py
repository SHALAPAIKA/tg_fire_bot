import os
import random
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# 🔑 Берём настройки из Environment Variables на Render
TOKEN = os.getenv("TOKEN")   # твой токен
CHAT_ID = int(os.getenv("CHAT_ID"))  # id группы, куда бот пишет
OWNER_ID = int(os.getenv("OWNER_ID"))  # твой личный id

# 📂 файлы для админов и юзеров
USERS_FILE = "users.txt"
ADMINS_FILE = "admins.txt"
EMOJI_FILE = "emoji.txt"


# ======================
# 🔧 Работа с файлами
# ======================
def load_list(filename):
    if not os.path.exists(filename):
        return []
    with open(filename, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def save_list(filename, items):
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(items))


# ======================
# 🛠 Команды
# ======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """При старте бот пишет список команд и админов"""
    admins = load_list(ADMINS_FILE)
    users = load_list(USERS_FILE)
    emoji = load_list(EMOJI_FILE)
    emoji = emoji[0] if emoji else "🔥"

    commands = (
        "📜 Доступные команды:\n"
        "/addadm <id> – добавить администратора\n"
        "/adduser <@username> – добавить пользователя\n"
        "/list – показать список пользователей\n"
        "/emo <emoji> – сменить эмодзи для сообщений\n"
        "/admins – показать список админов\n"
    )

    text = (
        f"🚀 Бот запущен!\n\n"
        f"{commands}\n"
        f"👑 Администраторы: {', '.join(admins) if admins else 'пока нет'}\n"
        f"👥 Пользователи: {', '.join(users) if users else 'пока нет'}\n"
        f"Эмодзи по умолчанию: {emoji}"
    )

    # отправляем в личку
    if update.message.chat.type == "private":
        await update.message.reply_text(text)
    else:
        await context.bot.send_message(chat_id=CHAT_ID, text=text)


async def add_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Добавление администратора"""
    if str(update.effective_user.id) != str(OWNER_ID):
        return await update.message.reply_text("⛔ Только владелец может добавлять админов.")

    if not context.args:
        return await update.message.reply_text("Укажи ID пользователя: /addadm 123456789")

    new_admin = context.args[0]
    admins = load_list(ADMINS_FILE)
    if new_admin not in admins:
        admins.append(new_admin)
        save_list(ADMINS_FILE, admins)
        await update.message.reply_text(f"✅ Админ {new_admin} добавлен!")
    else:
        await update.message.reply_text("⚠️ Этот админ уже есть.")


async def add_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Добавление пользователя"""
    user_id = str(update.effective_user.id)
    admins = load_list(ADMINS_FILE)
    if user_id not in admins and user_id != str(OWNER_ID):
        return await update.message.reply_text("⛔ Нет прав.")

    if not context.args:
        return await update.message.reply_text("Укажи username: /adduser @example")

    new_user = context.args[0]
    users = load_list(USERS_FILE)
    if new_user not in users:
        users.append(new_user)
        save_list(USERS_FILE, users)
        await update.message.reply_text(f"✅ Пользователь {new_user} добавлен!")
    else:
        await update.message.reply_text("⚠️ Этот пользователь уже есть.")


async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать всех пользователей"""
    users = load_list(USERS_FILE)
    if users:
        await update.message.reply_text("👥 Список пользователей:\n" + "\n".join(users))
    else:
        await update.message.reply_text("⚠️ Список пользователей пуст.")


async def list_admins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать всех админов"""
    admins = load_list(ADMINS_FILE)
    if admins:
        await update.message.reply_text("👑 Администраторы:\n" + "\n".join(admins))
    else:
        await update.message.reply_text("⚠️ Список админов пуст.")


async def change_emoji(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Смена эмодзи"""
    user_id = str(update.effective_user.id)
    admins = load_list(ADMINS_FILE)
    if user_id not in admins and user_id != str(OWNER_ID):
        return await update.message.reply_text("⛔ Нет прав.")

    if not context.args:
        return await update.message.reply_text("Укажи эмодзи: /emo 🔥")

    emoji = context.args[0]
    save_list(EMOJI_FILE, [emoji])
    await update.message.reply_text(f"✅ Эмодзи изменено на {emoji}")


async def fortune_message(app: Application):
    """Фортуна выбирает случайного пользователя"""
    users = load_list(USERS_FILE)
    emoji = load_list(EMOJI_FILE)
    emoji = emoji[0] if emoji else "🔥"

    if users:
        chosen = random.choice(users)
        text = f"Фортуна выбрала тебя {emoji}\n{chosen}"
        await app.bot.send_message(chat_id=CHAT_ID, text=text)


# ======================
# 🚀 MAIN
# ======================
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("addadm", add_admin))
    app.add_handler(CommandHandler("adduser", add_user))
    app.add_handler(CommandHandler("list", list_users))
    app.add_handler(CommandHandler("admins", list_admins))
    app.add_handler(CommandHandler("emo", change_emoji))

    print("🚀 Бот запущен...")
    app.run_polling()


if __name__ == "__main__":
    main()
