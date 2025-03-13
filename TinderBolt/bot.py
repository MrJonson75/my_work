from multiprocessing.connection import answer_challenge
from xml.sax import parse

from charset_normalizer.cli.normalizer import query_yes_no
from telegram.ext import ApplicationBuilder, MessageHandler, filters, CallbackQueryHandler, CommandHandler

from gpt import *
from util import *


async def start(update, context):
    dialog.mode = 'main'
    text = load_message('main')
    await send_photo(update, context, 'main')
    await send_text(update, context, '*Hello, You gave the command to Start*')
    await send_text(update, context, text)

    await show_main_menu(update, context, {
        'start': 'главное меню бота',
        'profile': 'генерация Tinder-профля',
        'opener': 'сообщение для знакомства',
        'message': 'переписка от вашего имени',
        'date': 'переписка со звездами',
        'gpt': 'задать вопрос чату GPT'
    })


async def gpt(update, context):
    dialog.mode = 'gpt'
    text = load_message('gpt')
    await send_photo(update, context, 'gpt')
    await send_text(update, context, text)


async def gpt_dialog(update, context):
    text = update.message.text
    prompt = load_prompt('gpt')
    # answer = await chatgpt.send_question('Напиши четкий и короткий ответ на следующий вопрос:', text)
    answer = await chatgpt.send_question(prompt, text)
    await send_text(update, context, answer)


async def date(update, context):
    dialog.mode = 'date'
    text = load_message('date')
    await send_photo(update, context, 'date')
    await send_text_buttons(update, context, text, {
        "date_grande": "Ариана Гранде",
        "date_robbie": "Марго Робби",
        "date_zendaya": "Зендея",
        "date_gosling": "Райан Гослинг",
        "date_hardy": "Том Харди"
    })


async def date_dialog(update, context):
    text = update.message.text
    my_message = await send_text(update, context, 'Набирает текст ....')
    answer = await chatgpt.add_message(text)
    await my_message.edit_text(answer)
    # await send_text(update, context, answer)


async def date_button(update, context):
    query = update.callback_query.data
    await update.callback_query.answer()
    await send_photo(update, context, query)    # отправка фото

    await send_text(update, context, 'Отличный выбор! Пригласите деушку (парня) на свидание за 5 сообщений')

    prompt = load_prompt(query)
    chatgpt.set_prompt(prompt)


async def message(update, context):
    dialog.mode = 'message'
    text = load_message('message')
    await send_photo(update, context, 'message')
    await send_text_buttons(update, context, text, {
        'message_next': 'Следующее сообщение',
        'message_date': 'Пригласить на свидание'
    })

    dialog.list.clear()


async def message_button(update, context):
    query = update.callback_query.data
    await update.callback_query.answer()

    prompt = load_prompt(query)
    user_chat_history = '\n\n'.join(dialog.list)
    my_message = await send_text(update, context, 'ChatGPT думает над вариантами ответа ....')
    answer = await chatgpt.send_question(prompt, user_chat_history)
    # await send_text(update, context, answer)
    await my_message.edit_text(answer)


async def message_dialog(update, context):
    text = update.message.text
    dialog.list.append(text)


async def profile(update, context):
    dialog.mode = 'profile'
    text = load_message('profile')
    await send_photo(update, context, 'profile')
    await send_text(update, context, text)

    dialog.user.clear()
    dialog.count = 0
    await send_text(update, context, 'Сколько Вам лет?')


async def profile_dialog(update, context):
    text = update.message.text
    dialog.count += 1

    if dialog.count == 1:
        dialog.user['age'] = text
        await send_text(update, context, 'Кем Вы работаете?')
    elif dialog.count == 2:
        dialog.user['occupation'] = text
        await send_text(update, context, 'У Вас есть хобби?')
    elif dialog.count == 3:
        dialog.user['hobby'] = text
        await send_text(update, context, 'что Вам ненравится в людях')
    elif dialog.count == 4:
        dialog.user['annoys'] = text
        await send_text(update, context, 'Цели знакомства')
    elif dialog.count == 5:
        dialog.user['goals'] = text
        prompt = load_prompt('profile')
        user_info = dialog_user_info_to_str(dialog.user)

        my_message = await send_text(update, context, 'ChatGPT 🧠 занимается генерацией Вашего профиля. Подождите ...')
        answer = await chatgpt.send_question(prompt, user_info)

        await my_message.edit_text(answer)


async def opener(update, context):
    dialog.mode = 'opener'
    text = load_message('opener')
    await send_photo(update, context, 'opener')
    await send_text(update, context, text)

    dialog.user.clear()
    dialog.count = 0
    await send_text(update, context, 'Имя деушки?')


async def opener_dialog(update, context):
    text = update.message.text
    dialog.count += 1

    if dialog.count == 1:
        dialog.user['name'] = text
        await send_text(update, context, 'Сколько ей лет?')
    elif dialog.count == 2:
        dialog.user['age'] = text
        await send_text(update, context, 'Оцените ее внешность: 1-10 баллов?')
    elif dialog.count == 3:
        dialog.user['handsome'] = text
        await send_text(update, context, 'Кем она работает?')
    elif dialog.count == 4:
        dialog.user['occupation'] = text
        await send_text(update, context, 'Цель знакомства?')
    elif dialog.count == 5:
        dialog.user['goals'] = text
        prompt = load_prompt('opener')
        user_info = dialog_user_info_to_str(dialog.user)

        my_message = await send_text(update, context, 'ChatGPT 🧠 занимается. Подождите ...')

        answer = await chatgpt.send_question(prompt, user_info)
        await my_message.edit_text(answer)




async def hello(update, context):
    if dialog.mode == 'gpt':
        await gpt_dialog(update, context)
    elif dialog.mode == 'date':
        await date_dialog(update, context)
    elif dialog.mode == 'message':
        await message_dialog(update, context)
    elif dialog.mode == 'profile':
        await profile_dialog(update, context)
    elif dialog.mode == 'opener':
        await opener_dialog(update, context)
    else:
        await send_text(update, context, '*Здравствуй, как дела?*')  # *__* Сделать жирным
        await send_text(update, context, '_Получил_ ' + update.message.text)   # _   _ Сделать курсив

        await send_photo(update, context, 'avatar_main')
        await send_text_buttons(update, context, 'Запустить',
                                {
                                    'start': 'Запустить',
                                    'stop': 'Остановить'
                                })


async def hello_button(update, context):
    query = update.callback_query.data
    if query == 'start':
        await send_text(update, context, '*Запускаю процесс*')
    elif query == 'stop':
        await send_text(update, context, '*Стоп машина*')


dialog = Dialog()
dialog.mode = None
dialog.list = []    # сюда сбрасываем все сообщения которые человек пишет
dialog.count = 0    # счетчик количества вопросов
dialog.user = {}    # словарь для хранения ответов пользователя


#   Токен ChatGPT
chatgpt = ChatGptService(token='gpt:')

#   Токен Телеграмм
app = ApplicationBuilder().token(":").build()

# подключение хендлеров
app.add_handler(CommandHandler('start', start))
app.add_handler(CommandHandler('gpt', gpt))
app.add_handler(CommandHandler('date', date))
app.add_handler(CommandHandler('message', message))
app.add_handler(CommandHandler('profile', profile))
app.add_handler(CommandHandler('opener', opener))

# подключение основного хендлера с фильтром на комманды
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, hello))

# подключение кнопок
app.add_handler(CallbackQueryHandler(date_button, pattern='^date_.*'))
app.add_handler(CallbackQueryHandler(message_button, pattern='^message_.*'))
app.add_handler(CallbackQueryHandler(hello_button))
app.run_polling()
