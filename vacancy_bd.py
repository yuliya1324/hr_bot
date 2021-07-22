import re
import requests
import json
import sqlite3


def get_vacancies() -> list:
    """
    Функция, которая с помощью API hh ищет вакансии компании "Буше"
    :return: список вакансий
    """
    req_1 = requests.get('https://api.hh.ru/employers/114223')
    data_employer = json.loads(req_1.content.decode())
    req_1.close()
    req_2 = requests.get(data_employer['vacancies_url'], {'per_page': 100})
    data_vacancies = json.loads(req_2.content.decode())
    req_2.close()
    return data_vacancies['items']


def process_description(text: str) -> dict or bool:
    """
    Функция, которая обрабатывает описание вакансии и записывает отдельно обязанности, условия и требования
    :param text: описание вакансии
    :return: словарь с обязанностями, условиями и требованиями по вакансии
    """
    # Словарь со всеми возможными написаниями для "обязанностей", "условий" и "требований"
    dict_of_titles = {'Обязанности': 'Обязанности', 'Условия': 'Условия', 'Требования': 'Требования',
                      'Мы предлагаем': 'Условия', 'Тебе предстоит': 'Обязанности', 'Мы ждем от тебя': 'Требования',
                      'В круг задач будет входить': 'Обязанности', 'Мы ищем профессионала, который': 'Требования',
                      'У нас': 'Условия', 'Вам предстоит': 'Обязанности', 'Мы ждем': 'Требования',
                      'Должностные обязанности': 'Обязанности', 'Что предстоит делать': 'Обязанности',
                      'Что мы ждем': 'Требования', 'От тебя потребуется': 'Требования', 'Наши требования': 'Требования',
                      'Дополнительные условия': 'Условия', 'От Вас': 'Требования', 'Функционал': 'Обязанности',
                      'В твои обязанности будет входить': 'Обязанности', 'От вас потребуется': 'Требования'}
    everything = {'Обязанности': [], 'Условия': [], 'Требования': []}
    titles = re.findall('<strong>([А-Яа-яЁё:, ]+?)</strong>', text)  # находим заголовки в описании
    titles = [title.replace(':', '') for title in titles if title.replace(':', '') in dict_of_titles]  # отбираем только нужные
    for i in range(len(titles)):
        if i != len(titles)-1:
            part = re.findall(f'{titles[i]}(.+){titles[i + 1]}', text)[0]
        else:
            part = re.findall(f'{titles[i]}(.+)', text)[0]
        title = dict_of_titles[titles[i]]
        lists = re.findall('<ul> <li>(.+)</li> </ul>', part)  # находим список с перечислением пунктов
        if not lists:
            return None
        for li in lists:
            everything[title].extend(li.split('</li> <li>'))
    return everything


def get_vacancy(url: str) -> tuple or bool:
    """
    Функция, которая собирает информацию о вакансии и обрабатывает ее
    :param url: ссылка на вакансию
    :return: вся информация о вакансии
    """
    req = requests.get(url)
    vacancy_data = json.loads(req.content.decode())
    req.close()
    experience = vacancy_data['experience']['name']  # получаем требуемый опыт работы
    if experience == 'Нет опыта':
        experience = 0  # если он не требуется, то записываем 0
    else:
        experience = int(re.findall('От (\d+)', experience)[0])  # берем только нижнюю планку
    processed_descr = process_description(vacancy_data['description'])  # обрабатываем описание вакансии
    if not processed_descr:  # если из описания не получилось достать то, что нам нужно, то пропускаем эту вакансию
        return None
    return int(vacancy_data['id']), vacancy_data['name'], vacancy_data['area']['name'], \
           experience, '\n'.join(processed_descr['Требования']), '\n'.join(processed_descr['Условия']), \
           '\n'.join(processed_descr['Обязанности'])


def write_to_bd(data: list):
    """
    Функция, которая записывает информацию о вакансиях в БД
    :param data: список кортежей со всеми вакансиями
    """
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.executemany("INSERT INTO vacancies VALUES (?, ?, ?, ?, ?, ?, ?)", data)
    con.commit()


def main():
    data_vac = []
    data = get_vacancies()  # получаем список вакансий
    for v in data:
        vacancy = get_vacancy(v['url'])  # получаем информацию о вакансии
        if vacancy:
            data_vac.append(vacancy)  # если вакансия обработалась, то добавляем ее в список всех вакансий
    write_to_bd(data_vac)  # записываем вакансии в БД


if __name__ == '__main__':
    main()
