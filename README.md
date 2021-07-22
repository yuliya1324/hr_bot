# Это HR-бот для компании "Буше"

[Ссылка на бота](https://t.me/bushe_hr_bot)

Этот бот может:
* рассказать о компании
* дать контакты HR
* ответить на распространенные вопросы
* показать актуальные вакансии
* взять основную информацию о кандидате
* провести первоначальный отбор на открытую вакансию
* записать на собеседование

## Код

Здесь лежат файлы:
* `database.db` - база данных с вакансиями, кандидатами и календарем
* `main.py` - файл с ботом и фласком
* `work_with_answers.py`, `work_with_db.py` - вспомогательные файлы для бота
* `bd.py`, `vacancy_bd.py` - файлы для создания БД

### Основной код с ботом

`main.py` - главный файл, где прописаны все функции бота и все необходимое для tg API и Flask. Другие файлы не взаимодействуют с tg API.

`work_with_answers.py` - файл, содержащий одну функцию, которая обрабатывает ответ пользователя на вопрос о ценностях. Сначала текст предобрабатывается, остаются только основы слов. Затем проверяется, есть ли хотя бы одно совпадение основ между текстом пользователя и ценностями, которых придерживается компания.

`work_with_db.py` - файл для работы с БД.

#### Алгоритм отбора

1. Сначала бот проверяет есть ли кандидат в БД
2. Если нет, то берет у него основную информацию, а если есть, то переходит к шагу 3
3. Предлагает выбрать город, где пользователь ищет работу
4. Предлагает выбрать интересующую вакансию
5. Выводит условия работы и обязанности, которые необходимо выполнять на данной позиции
6. Спрашивает про опыт работы на схожей позиции и проверяет, имеет ли кандидат минимальный требуемый опыт
7. Если нет, то кандидат не прошел отбор, иначе следующий шаг
8. Просит описать жизненную позицию и ценности кандидата и проверяет на совпадение с позицией и ценностями компании
9. Если ценности не совпали, то кандидат не прошел отбор, иначе следующий шаг
10. Дальше по очереди выводят требования к кандидату, и он должен ответить по каждому пункту, обладает ли он необходимыми компетенциями
11. Если ответ "нет" хотя бы по одному пункту, то то кандидат не прошел отбор, иначе следующий шаг
12. Бот смотрит, какие есть свободные слоты в расписании, и выводит их пользователю для выбора
13. После того, как пользователь выбрал дату и время собеседования, этот слот заполняется в БД id пользователя
14. Бот подтверждает запись на собеседование

### Структура БД

В БД 3 таблицы:
* vacancies
* applicants
* calendar

В таблице vacancies собрана информация о вакансиях: id, название, город, требуемый опыт работы, требования к кандидату, условия работы и обязанности, которые необходимо выполнять на данной позиции. Во время работы бота, эта таблица не меняется.

В таблицу applicants записыаются данные о кандидатах: id, ФИО, город, возраст, пол, номер телефона, email и ссылки на соц.сети. Эта таблица сделана в основном для того, чтобы HR могли к ней обращаться при необходимости.

В таблице calendar хранится расписание: день, время и id кандидата, для записи на собеседование. Во время работы бота информация как берется из этой таблицы, так и вносится в нее.

### Создание БД

**N.B. Лучше не запускать эти файлы, потому что они могут перезаписать БД.**

С помощью файла `bd.py` создаются таблицы в БД, а если запустить `vacancy_bd.py`, то заполнится таблица с вакансиями.

Для заполнения таблицы с вакансиями был распарсен сайт [hh.ru](https://hh.ru/). После чего данные были еще немного поправлены автоматически и вручную (описание очищено тэгов html, добавлены пропущеные значения).
