import os
import random
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# 🔑 Настройки
TOKEN = "8061629633:AAHR_ZJC1LRinp-PUfjFoeJsdgcIHge3F6s"
CHAT_ID = -1002286664635  # ID группы
OWNER_ID = 1431532712      # твой Telegram ID

# 📂 файлы для хранения
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
def help_cmd(update: Update, context: CallbackContext):
    text = (
        "📜 Доступные команды:\n"
        "/addall user1 user2 ... – добавить список пользователей\n"
        "/add user – добавить одного пользователя\n"
        "/dell user – удалить пользователя\n"
        "/clear – очистить список\n"
        "/list – показать список пользователей\n"
        "/fire – выбрать случайного пользователя и отправить в группу\n"
        "/addadm user_id – добавить администратора (только владелец)\n"
        "/emo 😀 – сменить эмодзи\n"
        "/help – показать эту справку"
    )
    update.message.reply_text(text)

def start(update: Update, context: CallbackContext):
    help_cmd(update, context)
    admins = load_list(ADMINS_FILE)
    update.message.reply_text(f"👑 Администраторы: {', '.join(admins) if admins else 'пока нет'}")

def addadm(update: Update, context: CallbackContext):
    if update.effective_user.id != OWNER_ID:
        update.message.reply_text("⛔ Только владелец может добавлять админов")
        return
    if not context.args:
        update.message.reply_text("Используй: /addadm user_id")
        return
    new_admin = context.args[0]
    admins = load_list(ADMINS_FILE)
    if new_admin not in admins:
        admins.append(new_admin)
        save_list(ADMINS_FILE, admins)
        update.message.reply_text(f"✅ Админ {new_admin} добавлен")
    else:
        update.message.reply_text("⚠️ Этот админ уже есть")

def addall(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    admins = load_list(ADMINS_FILE)
    if user_id not in admins and user_id != str(OWNER_ID):
        update.message.reply_text("⛔ Нет прав")
        return
    if not context.args:
        update.message.reply_text("Используй: /addall user1 user2 ...")
        return
    users = load_list(USERS_FILE)
    for user in context.args:
        if user not in users:
            users.append(user)
    save_list(USERS_FILE, users)
    update.message.reply_text(f"✅ Добавлены пользователи: {' '.join(context.args)}")

def add(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    admins = load_list(ADMINS_FILE)
    if user_id not in admins and user_id != str(OWNER_ID):
        update.message.reply_text("⛔ Нет прав")
        return
    if not context.args:
        update.message.reply_text("Используй: /add user")
        return
    user = context.args[0]
    users = load_list(USERS_FILE)
    if user not in users:
        users.append(user)
        save_list(USERS_FILE, users)
        update.message.reply_text(f"✅ Пользователь {user} добавлен")
    else:
        update.message.reply_text("⚠️ Этот пользователь уже есть")

def dell(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    admins = load_list(ADMINS_FILE)
    if user_id not in admins and user_id != str(OWNER_ID):
        update.message.reply_text("⛔ Нет прав")
        return
    if not context.args:
        update.message.reply_text("Используй: /dell user")
        return
    user = context.args[0]
    users = load_list(USERS_FILE)
    if user in users:
        users.remove(user)
        save_list(USERS_FILE, users)
        update.message.reply_text(f"✅ Пользователь {user} удалён")
    else:
        update.message.reply_text("⚠️ Пользователя нет в списке")

def clear(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    admins = load_list(ADMINS_FILE)
    if user_id not in admins and user_id != str(OWNER_ID):
        update.message.reply_text("⛔ Нет прав")
        return
    save_list(USERS_FILE, [])
    update.message.reply_text("✅ Список очищен")

def list_users(update: Update, context: CallbackContext):
    users = load_list(USERS_FILE)
    if users:
        update.message.reply_text("👥 Список пользователей:\n" + "\n".join(users))
    else:
        update.message.reply_text("⚠️ Список пользователей пуст")

def emo(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    admins = load_list(ADMINS_FILE)
    if user_id not in admins and user_id != str(OWNER_ID):
        update.message.reply_text("⛔ Нет прав")
        return
    if not context.args:
        update.message.reply_text("Используй: /emo 😀")
        return
    emoji = context.args[0]
    save_list(EMOJI_FILE, [emoji])
    update.message.reply_text(f"✅ Эмодзи изменено на {emoji}")

def fire(update: Update, context: CallbackContext):
    users = load_list(USERS_FILE)
    emoji = load_list(EMOJI_FILE)
    emoji = emoji[0] if emoji else "🔥"
    if users:
        chosen = random.choice(users)
        text = f"Фортуна выбрала тебя {emoji}\n{chosen}"
        context.bot.send_message(chat_id=CHAT_ID, text=text)
    else:
        update.message.reply_text("⚠️ Список пользователей пуст")

# ======================
# 🚀 MAIN
# ======================
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_cmd))
    dp.add_handler(CommandHandler("addadm", addadm))
    dp.add_handler(CommandHandler("addall", addall))
    dp.add_handler(CommandHandler("add", add))
    dp.add_handler(CommandHandler("dell", dell))
    dp.add_handler(CommandHandler("clear", clear))
    dp.add_handler(CommandHandler("list", list_users))
    dp.add_handler(CommandHandler("emo", emo))
    dp.add_handler(CommandHandler("fire", fire))

    print("🚀 Бот запущен...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
