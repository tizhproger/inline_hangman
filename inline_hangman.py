import telebot
import uuid
import re
import sys
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent
API_TOKEN = 'token'
bot = telebot.TeleBot(API_TOKEN)
stages = ['———|\n|\n|\n|\n——',
          '———|\n|        O\n|\n|\n——',
          '———|\n|        O\n|        |  \n|\n——',
          '———|\n|        O\n|      / |  \n|\n——',
          '———|\n|        O\n|      / | \ \n|\n——',
          '———|\n|        O\n|      / | \ \n|       /   \n——',
          '———|\n|        O\n|      / | \ \n|       /  \ \n——']
hangs = {}

"""
TODO: Delete game if joined player is AFK for settled time.
TODO: Game for particular user
"""

def view_buttons(position, id, eng):
    if eng:
        names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U',
                'V', 'W', 'X', 'Y', 'Z']
    else:
        names = ['А', 'Б', 'В', 'Г', 'Д', 'Е', 'Ё', 'Ж', 'З', 'И', 'Й', 'К', 'Л', 'М', 'Н', 'О', 'П', 'Р', 'С', 'Т', 'У',
                'Ф', 'Х', 'Ц', 'Ч', 'Ш', 'Щ', 'Ъ', 'Ы', 'Ь', 'Э', 'Ю', 'Я']
    tst = []
    tst2 = []
    end = 0
    letters_num = 8
    view_keyboard = 0
    start = letters_num * position

    if len(names[start:]) > letters_num:
        end = (start) + letters_num
    else:
        end = start + len(names[start:])
    
    for numb in range(start, end):
        if numb < (start+4):
            tst.append(telebot.types.InlineKeyboardButton(text=names[numb], callback_data='hangman=letter=' + id + '=' + names[numb].lower()))
        else:
            tst2.append(telebot.types.InlineKeyboardButton(text=names[numb], callback_data='hangman=letter=' + id + '=' + names[numb].lower()))
    
    view_keyboard = telebot.types.InlineKeyboardMarkup(keyboard=[tst, tst2], row_width=4)

    view_keyboard.row(telebot.types.InlineKeyboardButton(text='<< Prev', callback_data='hangman=letter_prev=' + id),
                      telebot.types.InlineKeyboardButton(text='Next >>', callback_data='hangman=letter_next=' + id))
    return view_keyboard


def game_info(id, mode, word_mode=False):
    if mode == 'all':
        if word_mode:
            guessed = hangs[id]['guessed']
            return re.sub(f'[^{guessed}]', '*', hangs[id]['word']), hangs[id]['takes'], hangs[id]['keyboard'], guessed, hangs[id]['eng']
        return hangs[id]['word'], hangs[id]['takes'], hangs[id]['keyboard'], hangs[id]['guessed'], hangs[id]['eng']
    return hangs[id][mode]


@bot.inline_handler(lambda query: len(query.query) > 0)
def hangman(inline_query):
    try:
        if len(inline_query.query) > 30:
            long_message = InlineQueryResultArticle('1', 'Слишком многа букав', InputTextMessageContent('Слово слишком длинное, выбери другое!'),
                description='Created by Zeus428',
                thumb_url='https://cdn-icons-png.flaticon.com/512/4522/4522081.png')
            bot.answer_inline_query(inline_query.id, [long_message], is_personal=True, cache_time=10)

        elif '@' not in inline_query.query:
            if re.search('[A-Za-z]', inline_query.query) and re.search('[А-Яа-я]', inline_query.query):
                inproper_letters = InlineQueryResultArticle('1', 'Только один язык', InputTextMessageContent('Не используйте несколько языков в одном слове!'),
                    description='Created by Zeus428',
                    thumb_url='https://cdn-icons-png.flaticon.com/512/484/484582.png')
                bot.answer_inline_query(inline_query.id, [inproper_letters], is_personal=True, cache_time=10)
                return
            
            if re.search('\W+', inline_query.query) or ('_' in inline_query.query) or re.search('[0-9]', inline_query.query):
                wrong_language = InlineQueryResultArticle('1', 'Без спец символов и цифр', InputTextMessageContent('Поддерживается только буквы!'),
                    description='Created by Zeus428',
                    thumb_url='https://i.ibb.co/0fNcL2S/5129504.png')
                bot.answer_inline_query(inline_query.id, [wrong_language], is_personal=True, cache_time=10)
                return

            english = False
            if re.search('[A-Za-z]', inline_query.query):
                english = True

            id = str(uuid.uuid4())
            word = inline_query.query
            hangs[id] = {'player': '', 'word': word.lower(), 'takes': 0, 'keyboard': 0, 'guessed': '`', 'eng': english}
            enter_game = InlineKeyboardMarkup().row(InlineKeyboardButton("Играть", callback_data=f"hangman=join={id}={inline_query.from_user.id}"))
            game_message = InlineQueryResultArticle('1', 'Виселица',
                InputTextMessageContent(stages[0] + '\n📝' + re.sub('\w', '*', word) + '\n🔄0/6'),
                reply_markup=enter_game,
                description='Created by Zeus428',
                thumb_url='https://i.ibb.co/mR9f56Z/3269914.png')
            bot.answer_inline_query(inline_query.id, [game_message], is_personal=True, cache_time=10)
    except:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print('Error type:'  + str(exc_type) + '\nFunction:'  + 'hangman' +  '\| Line:'  + str(exc_tb.tb_lineno) + "\nDetails: " + str(exc_obj))


@bot.callback_query_handler(func=lambda call: call.data.startswith("hangman"))
def hangman_buttons(call):
    try:
        data = call.data.split('=')
        game_id = data[2]

        if game_id not in hangs:
            bot.edit_message_text(inline_message_id=call.inline_message_id,
                    text='Игря потеряна, веревки сняты...',
                    reply_markup=None)
            bot.answer_callback_query(call.id)
            return

        if data[1] == 'letter_prev':
            if hangs[game_id]['player'] != str(call.from_user.id):
                bot.answer_callback_query(call.id, "Это не твоя игра, бро!")
                return

            if hangs[game_id]['keyboard'] > 0:
                hangs[game_id]['keyboard'] -= 1
                word, takes, keyboard_pos, guessed, eng = game_info(game_id, 'all', True)
                bot.edit_message_text(inline_message_id=call.inline_message_id,
                                      text=stages[takes] + f'\n📝{word}\n🔄{takes}/6\n<a href="tg://user?id={player}">🙎🏻‍♂️{player_name}</a>',
                                      reply_markup=view_buttons(keyboard_pos, game_id, eng), parse_mode='html')
                bot.answer_callback_query(call.id)
            else:
                bot.answer_callback_query(call.id)
            return

        if data[1] == 'letter_next':
            if hangs[game_id]['player'] != str(call.from_user.id):
                bot.answer_callback_query(call.id, "Это не твоя игра, бро!")
                return

            if (hangs[game_id]['eng'] and hangs[game_id]['keyboard'] < 3) or (not hangs[game_id]['eng'] and hangs[game_id]['keyboard'] < 4):
                hangs[game_id]['keyboard'] += 1
                word, takes, keyboard_pos, guessed, eng = game_info(game_id, 'all', True)
                bot.edit_message_text(inline_message_id=call.inline_message_id,
                                      text=stages[takes] + f'\n📝{word}\n🔄{takes}/6\n<a href="tg://user?id={player}">🙎🏻‍♂️{player_name}</a>',
                                      reply_markup=view_buttons(keyboard_pos, game_id, eng), parse_mode='html')
                bot.answer_callback_query(call.id)
            else:
                bot.answer_callback_query(call.id)
            return
        
        if data[1] == 'join':
            if data[3] == str(call.from_user.id):
                bot.answer_callback_query(call.id, 'Нельзя играть с собой!')
                return

            hangs[game_id]['player'] = str(call.from_user.id)
            english_mode = hangs[game_id]['eng']
            word, takes, keyboard_pos, guessed, eng = game_info(game_id, 'all')
            letter = data[3]
            player = hangs[game_id]['player']
            bot.edit_message_text(inline_message_id=call.inline_message_id,
                                  text=stages[0] + '\n📝' + re.sub('\w', '*', word) + '\n🔄0/6\n<a href="tg://user?id={player}">🙎🏻‍♂️{player_name}</a>',
                                  reply_markup=view_buttons(0, game_id, english_mode), parse_mode='html')
            bot.answer_callback_query(call.id, 'Добро пожаловать в игру!')
            return

        if data[1] == 'letter':
            if hangs[game_id]['player'] != str(call.from_user.id):
                bot.answer_callback_query(call.id, "Это не твоя игра, бро!")
                return
            
            word, takes, keyboard_pos, guessed, eng = game_info(game_id, 'all')
            letter = data[3]

            if re.search(f'[{letter}]', word):
                if letter in hangs[game_id]['guessed']:
                    bot.answer_callback_query(call.id, 'Эту букву уже выбирали!')
                    return
                guessed += letter
                word = re.sub(f'[^{guessed}]', '*', word)
                bot.edit_message_text(inline_message_id=call.inline_message_id,
                                      text=stages[takes] + f'\n📝{word}\n🔄{takes}/6\n<a href="tg://user?id={player}">🙎🏻‍♂️{player_name}</a>',
                                      reply_markup=view_buttons(keyboard_pos, game_id, eng), parse_mode='html')
                hangs[game_id]['guessed'] = guessed
                bot.answer_callback_query(call.id)

            else:
                takes += 1
                word = re.sub(f'[^{guessed}]', '*', word)
                bot.edit_message_text(inline_message_id=call.inline_message_id,
                                      text=stages[takes] + f'\n📝{word}\n🔄{takes}/6\n<a href="tg://user?id={player}">🙎🏻‍♂️{player_name}</a>',
                                      reply_markup=view_buttons(keyboard_pos, game_id, eng), parse_mode='html')
                hangs[game_id]['takes'] = takes
                bot.answer_callback_query(call.id, 'Неа, не то...')
            

            if len(hangs[game_id]['guessed'][1:]) == len(''.join(set(hangs[game_id]['word']))):
                word, takes, keyboard_pos, guessed, eng = game_info(game_id, 'all', True)
                player = hangs[game_id]['player']
                bot.edit_message_text(inline_message_id=call.inline_message_id,
                                      text=stages[takes] + f'\n📝{word}\n🔄{takes}/6\n<a href="tg://user?id={player}">🙎🏻‍♂️{player_name}</a> остался жив, награда: <i>ничего</i>',
                                      reply_markup=None, parse_mode='html')
                bot.answer_callback_query(call.id, 'Ты выиграл!')
                return
            
            if hangs[game_id]['takes'] == 6:
                word, takes, keyboard_pos, guessed, eng = game_info(game_id, 'all')
                player = hangs[game_id]['player']
                bot.edit_message_text(inline_message_id=call.inline_message_id,
                                      text=stages[takes] + f'\n📝{word}\n🔄{takes}/6\n<a href="tg://user?id={player}">{player_name}</a> повесился.',
                                      reply_markup=None, parse_mode='html')
                bot.answer_callback_query(call.id, 'Ты проиграл!')
                return
    except:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print('Error type:'  + str(exc_type) + '\nFunction:'  + 'hangman_buttons' +  '\| Line:'  + str(exc_tb.tb_lineno) + "\nDetails: " + str(exc_obj))


bot.infinity_polling()
