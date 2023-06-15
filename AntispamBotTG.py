import re
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config_copy import YOUR_GROUP_ID, YOUR_USER_ID, TWO_YOUR_USER_ID, BOT_TOKEN, ADMIN_ID, ID_SPAM_USER

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot) 

@dp.message_handler(content_types=['text'], chat_id=YOUR_GROUP_ID)
async def handle_group_messages(message: types.Message):
    stop_words_file = "stop_words.txt"

    with open(stop_words_file, 'r', encoding='utf-8') as file:
        stop_words = [word.strip() for word in file]

    message_words = re.findall(r'\b\w+\b', message.text.lower())
    spam_users = ID_SPAM_USER

    if message.from_user.id in spam_users:
        user = message.from_user
        user_info = f"Удаление по ID: {user.id}\nСпамер: {user.first_name} {user.last_name}\nUsername: @{user.username}\nОткуда удалено: {message.chat.title}" 

        forwarded_message = await bot.forward_message(chat_id=YOUR_USER_ID, from_chat_id=message.chat.id, message_id=message.message_id)
        await bot.send_message(chat_id=YOUR_USER_ID, text=user_info, reply_to_message_id=forwarded_message.message_id)
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        return

    spam_words = [word for word in message_words if word in stop_words]

    if spam_words:
        user = message.from_user
        user_info = f"Удаление по Стоп слову: {', '.join(spam_words)}\nСпамер: {user.first_name} {user.last_name}\nID: {user.id}, Username: @{user.username}\nОткуда удалено: {message.chat.title}"

        forwarded_message = await bot.forward_message(chat_id=YOUR_USER_ID, from_chat_id=message.chat.id, message_id=message.message_id)
        await bot.send_message(chat_id=YOUR_USER_ID, text=user_info, reply_to_message_id=forwarded_message.message_id)

        forwarded_message_2 = await bot.forward_message(chat_id=TWO_YOUR_USER_ID, from_chat_id=message.chat.id, message_id=message.message_id)
        await bot.send_message(chat_id=TWO_YOUR_USER_ID, text=user_info, reply_to_message_id=forwarded_message_2.message_id)

        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        return

@dp.message_handler(content_types=types.ContentTypes.TEXT, chat_id=ADMIN_ID)
async def handle_private_messages(message: types.Message):
    stop_words_file = "stop_words.txt"
    stop_word = message.text.strip()

    if stop_word.startswith("/"):
        if stop_word == "/start":
            await message.reply("Приветсвую! \nЭто Антиспам Бот\nЧто бы показать список всех стоп слов отправьте команду /show_all_words \n Что бы добавить/удалить стоп слово, просто отправьте мне слово, в одном сообщении 1 слово.")
        elif stop_word == "/show_all_words":
            with open(stop_words_file, 'r', encoding='utf-8') as file:
                stop_words_list = file.read().splitlines()
            response = "Список стоп слов по которым удаляются сообщения:\n" + "\n".join(stop_words_list)
            await message.reply(response)
        else:
            await message.reply("нет такой команды.")
    elif len(stop_word.split()) > 1:
        await message.reply("Я принимаю только одно стоп слово в одном сообщении.")
    else:
        with open(stop_words_file, 'r', encoding='utf-8') as file:
            existing_words = [word.strip() for word in file]

        if stop_word in existing_words:
            keyboard = types.InlineKeyboardMarkup()
            keyboard.row(
                types.InlineKeyboardButton("Да удалить", callback_data=f"delete_word:{stop_word}"),
                types.InlineKeyboardButton("Нет", callback_data="cancel_delete")
            )

            await message.reply("Слово уже находится в списке стоп-слов. Удалить?", reply_markup=keyboard)
        else:
            keyboard = types.InlineKeyboardMarkup()
            keyboard.row(
                types.InlineKeyboardButton("Добавить", callback_data=f"add_word:{stop_word}"),
                types.InlineKeyboardButton("Не добавлять", callback_data="cancel_add")
            )

            await message.reply("Вы хотите добавить это слово в список стоп-слов?", reply_markup=keyboard)

@dp.callback_query_handler(lambda query: query.data.startswith("add_word:"))
async def process_add_word_callback(query: types.CallbackQuery):
    stop_words_file = "stop_words.txt"
    stop_word = query.data.split(":")[1]

    with open(stop_words_file, 'r', encoding='utf-8') as file:
        existing_words = [word.strip() for word in file]

    if stop_word in existing_words:
        await bot.answer_callback_query(query.id, text="Слово уже существует в списке стоп-слов.")
        await bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
    else:
        with open(stop_words_file, 'a', encoding='utf-8') as file:
            file.write('\n' + stop_word)  # Add the new word to the stop_words file

        await bot.edit_message_text(
            chat_id=query.message.chat.id,
            message_id=query.message.message_id,
            text=f"Стоп слово '{stop_word}' успешно добавлено в список стоп-слов."
        )

@dp.callback_query_handler(lambda query: query.data.startswith("delete_word:"))
async def process_delete_word_callback(query: types.CallbackQuery):
    stop_words_file = "stop_words.txt"
    stop_word = query.data.split(":")[1]

    with open(stop_words_file, 'r', encoding='utf-8') as file:
        existing_words = [word.strip() for word in file]

    if stop_word in existing_words:
        existing_words.remove(stop_word)

        with open(stop_words_file, 'w', encoding='utf-8') as file:
            file.write('\n'.join(existing_words))

        await bot.edit_message_text(
            chat_id=query.message.chat.id,
            message_id=query.message.message_id,
            text=f"Стоп слово '{stop_word}' было успешно удалено из списка стоп-слов."
        )
    else:
        await bot.answer_callback_query(query.id, text="Слово отсутствует в списке стоп-слов.")
        await bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)

@dp.callback_query_handler(lambda query: query.data == "cancel_add")
async def process_cancel_add_callback(query: types.CallbackQuery):
    await bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
    await bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.reply_to_message.message_id)

@dp.callback_query_handler(lambda query: query.data == "cancel_delete")
async def process_cancel_delete_callback(query: types.CallbackQuery):
    await bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
    await bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.reply_to_message.message_id)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False)
