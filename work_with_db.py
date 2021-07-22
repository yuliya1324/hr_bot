from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Vacancies(db.Model):
    __tablename__ = "vacancies"

    id = db.Column('id', db.Integer, primary_key=True)
    name = db.Column('name', db.Text)
    city = db.Column('city', db.Text)
    experience = db.Column('experience', db.Integer)
    requirements = db.Column('requirements', db.Text)
    conditions = db.Column('conditions', db.Text)
    responsibilities = db.Column('responsibilities', db.Text)


class Applicants(db.Model):
    __tablename__ = "applicants"

    id = db.Column('id', db.Integer, primary_key=True)
    name = db.Column('name', db.Text)
    city = db.Column('city', db.Text)
    age = db.Column('age', db.Integer)
    gender = db.Column('gender', db.Text)
    number = db.Column('number', db.Text)
    email = db.Column('email', db.Text)
    social = db.Column('social', db.Text)


class Calendar(db.Model):
    __tablename__ = "calendar"

    day = db.Column('day', db.Text, primary_key=True)
    time = db.Column('time', db.Text, primary_key=True)
    applicant_id = db.Column('applicant_id', db.Integer)


def collect_vacancies_data():
    """
    Функция, которая берет информацию о вакансиях из БД
    :return: Информация о вакансиях
    """
    return Vacancies.query.all()


def collect_applicants_data():
    """
    Функция, которая берет информацию о кандидатах из БД
    :return: информация о кандидатах
    """
    return Applicants.query.all()


def add_to_data(data_app: list):
    """
    Функция, которая добавляет информацию о кандидатах в БД
    :param data_app: список кортежей с информацией о кандидатах
    """
    app = Applicants()
    app.id = data_app[0][0]
    app.name = data_app[0][1]
    app.city = data_app[0][2]
    app.age = data_app[0][3]
    app.gender = data_app[0][4]
    app.number = data_app[0][5]
    app.email = data_app[0][6]
    app.social = data_app[0][7]
    db.session.add(app)
    db.session.commit()


def check_experience(vac_id: int, experience: int) -> bool:
    """
    Функция, которая проверяет, подходит ли кандидат по опыту работы
    :param vac_id: id вакансии
    :param experience: опыт работы в количестве лет
    :return: True, если кандидат подходит по опыту работы на данную должность; False иначе
    """
    vacancies = Vacancies.query.all()
    for vacancy in vacancies:
        if vacancy.id == vac_id:
            required_experience = vacancy.experience
    if experience >= required_experience:
        return True
    else:
        return False


def get_calendar():
    """
    Функция, которая берет расписание собеседований из БД
    :return: записи с пустыми слотами для записи на собеседование
    """
    return Calendar.query.filter_by().all()


def add_to_calendar(day: str, time: str, idx: int) -> None:
    """
    Функция, которая добавляет дату, время и пользователя для собеседования в БД
    :param day: день собеседования
    :param time: время собеседования
    :param idx: id пользователя
    """
    slot = Calendar.query.filter_by(day=day, time=time).first()
    slot.applicant_id = idx
    db.session.commit()
