import sqlite3

con = sqlite3.connect('database.db')
cur = con.cursor()

# Создаем таблицу с вакансиями, гду мы будем хранить id, название, город, требуемый опыт работы,
# требования к кандидату, условия работы и обязаности на предлагаемой должности
cur.execute("""
CREATE TABLE vacancies (
    id INT,
    name TEXT,
    city TEXT,
    experience INT,
    requirements TEXT,
    conditions TEXT,
    responsibilities TEXT,
    PRIMARY KEY (id)
)
""")


# Другая таблица будет хранить данные о кандидатах на вакансии. Здесь будут храниться id кандидата,
# его имя, город, возраст, пол, номер телефона, email и ссылки на соц. сети. Информация о пользователе
# заполняется ожин раз, потом ее переписать нельзя, так как id - это уникальный ключ, который берется из
# id ползователя тг
cur.execute("""
CREATE TABLE applicants (
    id INT,
    name TEXT,
    city TEXT,
    age INT,
    gender TEXT,
    number TEXT,
    email TEXT,
    social TEXT,
    PRIMARY KEY (id)
)
""")


# В этой таблице будет храниться информация о том, какой кандидат на какую вакансию откликнулся и его опыт работы
# на схожей должности
cur.execute("""
CREATE TABLE app_vac (
    applicant_id INT,
    vacancy_id INT,
    experience INT
)
""")


# В этой таблице будет храниться расписание собеседований
cur.execute("""
CREATE TABLE calendar (
    day TEXT,
    time TEXT,
    applicant_id INT
)
""")


# Заполняем расписание, пока с пустыми id кандидатов
calendar = {'25.06': {'10:00': None, '11:00': None, '15:00': None, '18:00': None},
            '26.06': {'9:00': None, '17:00': None, '18:00': None, '19:00': None},
            '27.06': {'11:00': None, '12:00': None, '16:00': None, '18:00': None},
            '28.06': {'10:00': None, '11:00': None, '12:00': None, '13:00': None},
            '29.06': {'10:00': None, '11:00': None, '12:00': None, '13:00': None}}
slots = []
for day in calendar:
    for time in calendar[day]:
        slots.append((day, time, None))
cur.executemany("INSERT INTO calendar VALUES (?, ?, ?)", slots)
con.commit()
