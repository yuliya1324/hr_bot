import telebot
import flask
import conf
from telebot import types
import re
from work_with_db import add_to_data, collect_vacancies_data, check_experience, \
    get_calendar, add_to_calendar, db
from work_with_answers import process_values
import logging
logging.basicConfig(level=logging.ERROR,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

WEBHOOK_URL_BASE = "https://{}:{}".format(conf.WEBHOOK_HOST, conf.WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/{}/".format(conf.TOKEN)
bot = telebot.TeleBot(conf.TOKEN, threaded=False)
bot.remove_webhook()
bot.set_webhook(url=WEBHOOK_URL_BASE+WEBHOOK_URL_PATH)
app = flask.Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.app = app
db.init_app(app)

applicant_dict = {}  # Словарь с пользователями
vacancies_data = collect_vacancies_data()  # информация о вакансиях из базы данных


# класс пользователя
class Applicant:
    def __init__(self, name):
        self.name = name
        self.city = None
        self.age = None
        self.sex = None
        self.number = None
        self.email = None
        self.social = None
        self.vacancies = []  # сюда будем складывать вакансии, которыми заинтересовался пользователь


@bot.message_handler(commands=['start'])
def send_welcome(message):
    """
    Функция, которой бот приветствует пользователя
    """
    bot.send_message(message.chat.id, 'Привет!\n'
                                      'Меня зовут Бушенка. Я чат-бот компании "Буше". '
                                      'Буду рад рассказать о нашей компании, наших вакансиях, '
                                      'а также помочь тебе попасть именно к нам! '
                                      'У нас обалденные вензели с вишней! :)\n'
                                      'Чтобы узнать, что я умею нажми /help')


@bot.message_handler(commands=['help'])
def help_func(message):
    """
    Функция, которая выводит все полезные кнопки бота
    """
    bot.send_message(message.chat.id, "Я супер-умный и всегда готов тебе помочь. Надеюсь, мы с тобой подружимся)\n"
                                      "У меня ты можешь:\n"
                                      "-узнать все о компании /about\n"
                                      "-найти контакты HR /contacts (Ну вдруг я тебе не понравлюсь:()\n"
                                      "-получить ответ на интересующий вопрос /Q_A\n"
                                      "-посмотреть актуальные вакансии и выбрать то, что тебе подходит /vacancies\n"
                                      "-вспомнить, что я умею /help\n"
                                      "-познакомиться со мной поближе /intro")


@bot.message_handler(commands=['about'])
def about_func(message):
    """
    Функция, которая выводит информацию о компании
    """
    bot.send_message(message.chat.id, "Наш сайт - https://bushe.ru/\n"
                                      "Наши соц. сети:\n"
                                      "Вконтакте - https://vk.com/bushe.bakery\n"
                                      "Инстаграм - https://www.instagram.com/bushe.bakery/\n"
                                      "Одноклассники - https://ok.ru/bushe.bakery\n"
                                      "Facebook - https://www.facebook.com/bushe.bakery/\n"
                                      "YouTube - https://www.youtube.com/c/BusheBakery\n\n"
                                      "Мы - 'Буше'. Меняем вкус повседневной жизни, "
                                      "создавая новые традиции для еды, общения и вдохновения.\n"
                                      "Работать с нами, значит быть живым в любой момент времени!")


@bot.message_handler(commands=['contacts'])
def contacts_func(message):
    """
    Функция, которая выводит контакты HR
    """
    bot.send_message(message.chat.id, "Позвони в HR: +7 (812) 640-01-10\n"
                                      "Напиши: personal@bushe.ru\n"
                                      "Посети наш сайт с вакансиями - https://careers.bushe.ru/\n"
                                      "Или на hh.ru: "
                                      "https://hh.ru/search/"
                                      "vacancy?st=searchVacancy&from=employerPage&employer_id=114223")


@bot.message_handler(commands=['Q_A'])
def qa_func(message):
    """
    Функция для ответов на вопросы пользователя
    """
    msg = bot.send_message(message.chat.id, 'Можешь задать мне любой вопрос!')
    bot.register_next_step_handler(msg, no_answer)


def no_answer(message):
    """
    Функция, которая генерирует ответ на вопрос. Сейчас бот отвечает только на один вопрос :)
    """
    if message.text == 'Какие этапы отбора?':
        bot.send_message(message.chat.id, 'Сначала ты пообщаешься со мной. А дальше если на твою вакансию '
                                          'нужны hard-skills, то мы тебя позовем на прохождение конкурса. '
                                          'И последний этап - это краткое интервью с hr')
    else:
        bot.send_message(message.chat.id, 'Упс! Такое мне не рассказывали. '
                                          'Можешь связаться со знающими людьми /contacts')


@bot.message_handler(commands=['intro'])
def intro_func(message):
    """
    Функция, с которой начинается заполнение информации о пользователе
    """
    if message.chat.id in applicant_dict:  # проверяем, нет ли пользователя уже в БД,
        # если нет, то спрашиваем имя
        bot.send_message(message.chat.id, "Мы с тобой уже знакомы! :)\n"
                                          "Если хочешь посмотреть вакансии, нажми /vacancies")
    else:
        msg = bot.send_message(message.chat.id, 'Как тебя зовут? (Лучше полностью ФИО)')
        bot.register_next_step_handler(msg, process_name_step)  # переходим к следующему вопросу


def process_name_step(message):
    """
    Функция, которая добавляет пользователя в словарь и записывает его имя, затем спрашиваем возраст
    """
    applicant = Applicant(message.text)  # создаем объект класса Applicant и передаем name
    applicant_dict[message.chat.id] = applicant
    msg = bot.send_message(message.chat.id, 'Сколько тебе лет?')
    bot.register_next_step_handler(msg, process_age_step)


def process_age_step(message):
    """
    Функция, которая записывает возраст пользователя. Если возраст указан не цифрой, то просим ответить корректно.
    Потом спрашиваем пол
    """
    age = message.text
    if not age.isdigit():  # проверяем цифрой ли ответил пользователь
        msg = bot.send_message(message.chat.id, 'Пж, укажи возраст одной цифрой')
        bot.register_next_step_handler(msg, process_age_step)
        return
    applicant_dict[message.chat.id].age = int(age)
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('М', 'Ж')
    msg = bot.send_message(message.chat.id, 'Укажи свой пол', reply_markup=markup)
    bot.register_next_step_handler(msg, process_sex_step)


def process_sex_step(message):
    """
    Функция, которая записывает пол пользователя. Затем спрашиваем город
    """
    applicant_dict[message.chat.id].sex = message.text
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('Москва', 'Санкт-Петербург')
    msg = bot.send_message(message.chat.id, 'Из какого ты города?', reply_markup=markup)
    bot.register_next_step_handler(msg, process_city_step)


def process_city_step(message):
    """
    Функция, которая записывает город пользователя. Затем спрашиваем номер телефона
    """
    applicant_dict[message.chat.id].city = message.text
    msg = bot.send_message(message.chat.id, 'Дашь номерочек? Вдруг мне захочется тебе позвонить в 5 утра в вс :)')
    bot.register_next_step_handler(msg, take_number)


def take_number(message):
    """
    Функция, которая записывает номер пользователя. Затем спрашиваем email
    """
    applicant_dict[message.chat.id].number = message.text
    msg = bot.send_message(message.chat.id, 'И email тоже (постараюсь не спамить)')
    bot.register_next_step_handler(msg, take_email)


def take_email(message):
    """
    Функция, которая записывает email пользователя. Затем спрашиваем соц. сети
    """
    applicant_dict[message.chat.id].email = message.text
    msg = bot.send_message(message.chat.id, 'Можешь еще оставить ссылку на какую-нибудь соц. сеть')
    bot.register_next_step_handler(msg, take_social)


def take_social(message):
    """
    Функция, которая записывает соц.сети пользователя, выводит все введенные пользователем данные
    и спрашивает, верны ли они
    """
    applicant_dict[message.chat.id].social = message.text
    bot.send_message(message.chat.id, f'Проверь, все ли я правильно записал:\n'
                                      f'Имя: {applicant_dict[message.chat.id].name}\n'
                                      f'Возраст: {applicant_dict[message.chat.id].age}\n'
                                      f'Пол: {applicant_dict[message.chat.id].sex}\n'
                                      f'Город: {applicant_dict[message.chat.id].city}\n'
                                      f'Телефон: {applicant_dict[message.chat.id].number}\n'
                                      f'Email: {applicant_dict[message.chat.id].email}\n'
                                      f'Соц. сети: {applicant_dict[message.chat.id].social}')
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('Да', 'Нет')
    msg = bot.send_message(message.chat.id, 'Все верно?', reply_markup=markup)
    bot.register_next_step_handler(msg, check_correctness_step)


def check_correctness_step(message):
    """
    Функция, которая записывает все данные в базу данных, если они верны, а если нет, то идем по второму кругу
    """
    if message.text == 'Да':
        user = applicant_dict[message.chat.id]  # получаем информацию о пользователе из словаря
        data_app = [(message.chat.id, user.name, user.city, user.age, user.sex, user.number, user.email, user.social)]
        # подготавливаем данные
        add_to_data(data_app)  # записываем данные в БД
        bot.send_message(message.chat.id, 'Приятно познакомиться! Теперь можешь посмотреть свежие вакансии /vacancies')
    else:
        applicant_dict.pop(message.chat.id, None)
        bot.send_message(message.chat.id, 'Ой-ой, ну ты чего, теперь придется проходить все заново... Нажми /intro')


@bot.message_handler(commands=['vacancies'])
def vacancies_func(message):
    """
    Функция, которая проверяет, есть ли данные о пользователе в БД. Если нет, то спрашиваем,
    если есть, то показываем вакансии
    """
    if message.chat.id not in applicant_dict:  # проверяем, есть ли id пользователя в словаре
        bot.send_message(message.chat.id, "Кажется, мы с тобой еще не знакомы, давай знакомиться!")
        intro_func(message)  # отправляем к функции, которая собирает информацию о пользователе
    else:
        bot.send_message(message.chat.id, "Привет! Сейчас посмотрю, что появилось из новеньких вакансий")
        choose_city(message)


def choose_city(message):
    """
    Функция для выбора города, по которому будут фильтрованы вакансии
    """
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('Москва', 'Санкт-Петербург')
    msg = bot.send_message(message.chat.id, 'В каком городе тебе бы хотелось работать?', reply_markup=markup)
    bot.register_next_step_handler(msg, buttons_vac)


def buttons_vac(message):
    """
    Функция, которая фильтрует вакансии по городу и выводит все актуальные вакансии в виде кнопок с названиями
    """
    city = message.text
    vacancies_city = []
    for vacancy in vacancies_data:
        if vacancy.city == city:
            vacancies_city.append((vacancy.id, vacancy.name))
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*[types.InlineKeyboardButton(text=vac[1], callback_data=f"button_{int(vac[0])}")
                   for vac in vacancies_city])
    bot.send_message(message.chat.id, 'Можешь выбрать из этих вакансий:', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    """
    Функция, которая выводит условия и обязанности по выбранной должности. Дальше спрашиваем про опыт работы
    """
    if call.message:
        _, i = call.data.split('_')  # получаем id вакансии
        vacancy_id = int(i)
        applicant_dict[call.message.chat.id].vacancies.append(vacancy_id)  # добавляем вакансию в список всех вакансий,
        # которыми интересовался пользователь
        for vacancy in vacancies_data:
            if vacancy.id == vacancy_id:
                conditions = vacancy.conditions
                responsibilities = vacancy.responsibilities
        bot.send_message(call.message.chat.id, 'Вот, что мы предлагаем:\n'
                                               f'{conditions}')
        bot.send_message(call.message.chat.id, 'А вот, что тебе предстоит делать:\n '
                                               f'{responsibilities}')
        msg = bot.send_message(call.message.chat.id, 'Если тебя все устраивает, то укажи свой опыт работы на схожей '
                                                     'должности (просто цифрой сколько лет)')
        bot.register_next_step_handler(msg, process_exp_step)


def process_exp_step(message):
    """
    Функция, которая записывает id пользователя, id вакансии и опыт работы в БД
    """
    if re.search('\d+', message.text):  # если в ответе пользователя есть цифра, то записываем ее
        experience = int(re.findall('\d+', message.text)[0])
    else:
        experience = 0  # иначе записываем 0
    vac_id = applicant_dict[message.chat.id].vacancies[-1]  # получаем id вакансии
    if check_experience(vac_id, experience):  # если кандидат подходит по опыту работы, то спрашиваем про ценности
        msg = bot.send_message(message.chat.id, 'Отлично! Теперь мы хотели бы узнать тебя поближе. '
                                                'Пожалуйста, опиши кратко, какой философии по жизни ты придерживаешься,'
                                                'почему хочешь попасть в нашу команду')
        bot.register_next_step_handler(msg, values_step)
    else:
        if applicant_dict[message.chat.id].sex == 'M':  # подберем слово по полу пользователя
            word = 'готов'
        else:
            word = 'готова'
        bot.send_message(message.chat.id, 'Друг, к сожалению, ты не подходишь для данной вакансии из-за нехватки опыта.'
                                          f' Мы с удовольствием примем тебя в нашу команду, когда ты будешь {word}.'
                                          'Или можешь посмотреть другие вакансии /vacancies')


def values_step(message):
    """
    Функция, которая проверяет кандидата на совпадение ценностей.
    Если все ценности совпадают, то выводит требования к кандидату
    """
    answer = message.text
    if process_values(answer):  # проверяем на совпадение ценностей
        vac_id = applicant_dict[message.chat.id].vacancies[-1]
        for vacancy in vacancies_data:
            if vacancy.id == vac_id:
                requirements = vacancy.requirements.split('\n')
        bot.send_message(message.chat.id, 'Теперь тебе надо будет отметить те пункты, по которым ты подходишь')
        ask_requirements(requirements, message)
    else:
        bot.send_message(message.chat.id, 'Прости, друг, но я считаю, что наши мировоззрения не сходятся. '
                                          'Удачи тебе в поисках. Кто ищет, тот найдет!')


def ask_requirements(requirements, message):
    """
    Функция, которая выводит по очереди пункты с требованиями и спрашивает, относятся ли они к кандидату
    Если кандидат подошел по всем требованиям, то предлагает выбрать дату и время для собеседования
    :param requirements: список пунктов с требованиями
    """
    if not requirements:
        dates = get_calendar()  # получаем расписание
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add(*[x.day + ', ' + x.time for x in dates if not x.applicant_id])  # выводим свободные слоты в виде кнопок
        msg = bot.send_message(message.chat.id, 'Мы друг другу подходим! Выбери дату и время, когда ты можешь прийти '
                                                'на собес', reply_markup=markup)
        bot.register_next_step_handler(msg, choose_date)
    else:
        requirement = requirements[0]  # получаем пункт с требованием
        requirements.remove(requirement)  # убираем этот пункт из общего списка требований
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('Да', 'Нет')
        msg = bot.send_message(message.chat.id, f'{requirement}', reply_markup=markup)
        bot.register_next_step_handler(msg, lambda m: check(m, requirements))


def check(message, requirements):
    """
    Функция, которая обрабатывает ответ пользователя по каждому пункту
    Если ответ отрицательный, то кандидат не прошел отбор
    :param requirements: список пунктов с требованиями
    """
    if message.text == 'Да':
        ask_requirements(requirements, message)
    else:
        bot.send_message(message.chat.id, 'Это печально, но по результатам тестового задания мы вынуждены '
                                          'расстаться... Но твои контакты будут добавлены в нашу базу данных, '
                                          'к которым мы обязательно обратимся при необходимости в найме.\n'
                                          'Успехов тебе и побольше вензелей с вишней!')


def choose_date(message):
    """
    Функция, которая записывает пользователя в БД с расписанием
    """
    date = message.text
    day, time = date.split(', ')
    add_to_calendar(day, time, message.chat.id)  # добавляем в БД
    bot.send_message(message.chat.id, f'Супер! Ждем тебя {day} в {time}')


@bot.message_handler(func=lambda m: True)
def send_common_msg(message):
    """
    Функция, которая выводит сообщение, если пользователь ввел что-то не то
    """
    bot.send_message(message.chat.id, 'Дружок, ты что-то потерялся. Нажми на /help, чтобы найти то, что тебе нужно')


@app.route('/', methods=['GET', 'HEAD'])
def index():
    return 'ok'


@app.route(WEBHOOK_URL_PATH, methods=['POST'])
def webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        flask.abort(403)
