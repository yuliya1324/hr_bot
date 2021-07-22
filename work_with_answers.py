import re
import nltk
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer

nltk.download('stopwords')
nltk.download('punkt')
stemmer = SnowballStemmer('russian')
stopwords = stopwords.words('russian')


def process_values(text: str) -> bool:
    """
    Функция, которая проверяет кандидата на совпадение ценностей
    :param text: текст сообщения с описанием ценностей и мировоззрения кандидата
    :return: True, если есть зотя бы одно совпадение в ценностях; False иначе
    """
    values_voc = '(уважен|эколог|профессионализм|вовлечен|гибкост|самообразован|образован|профессиона|гибк|эко)'
    # словарь с основами ценностей компании
    message = ' '.join([stemmer.stem(word) for word in word_tokenize(text.lower())
                        if (re.search(r"[^a-zа-я ]", word) is None) and word not in
                        stopwords])  # обрабатываем текст сообщения
    if re.findall(values_voc, message):
        return True
    else:
        return False
