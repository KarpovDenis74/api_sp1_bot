import os
import requests
import telegram
import time
from dotenv import load_dotenv
import logging

load_dotenv()
PRACTICUM_TOKEN = os.getenv("PRACTICUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
TIME_OUT = int(os.getenv('TIME_OUT'))
PRACTICUM_SERVER = os.getenv('PRACTICUM_SERVER')
logger = logging.getLogger("Log1")
logger.setLevel(logging.INFO)
fh = logging.FileHandler(filename="log.log", mode="w")
formatter = logging.Formatter('%(asctime)s - %(name)s'
    ' - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)
log_get_homework_statuses = logging.getLogger("Log1.get_homework_statuses")
log_send_message = logging.getLogger("Log1.send_message")


def parse_homework_status(homework):
    if homework.get('homework_name') is None or homework.get('status') is None:
        return 'Неверный ответ сервера.'
    homework_name = homework.get('homework_name')
    if homework.get('status') == 'rejected':
        verdict = 'К сожалению в работе нашлись ошибки.'
    else:
        verdict = ('Ревьюеру всё понравилось, '
            'можно приступать к следующему уроку.')
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    if current_timestamp is None:
        return None
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    params = {
        'from_date': current_timestamp,
    }
    try:
        homework_statuses = requests.get(PRACTICUM_SERVER,
                            headers=headers,
                            params=params)
        log_get_homework_statuses.info('Запрос статуса домашки. Ответ '
            f'{PRACTICUM_SERVER} - {homework_statuses.status_code}')
        homework_status = homework_statuses.json()
    except Exception as e:
        log_get_homework_statuses.error('Запрос статуса домашки. Ошибка:'
            f'{PRACTICUM_SERVER} - {e}')
        homework_status = None
    return homework_status


def send_message(message):
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    log_send_message.info("Отослано сообщение об изменении статуса домашки")
    return bot.send_message(chat_id=CHAT_ID, text=message)


def main():
    logger.info("Программа запущена")
    current_timestamp = int(time.time())
    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework is not None:
                if new_homework.get('homeworks'):
                    logger.info('Статус домашки изменился')
                    send_message(parse_homework_status(
                        new_homework.get(
                            'homeworks')[0]))
                current_timestamp = new_homework.get('current_date')
            else:
                logger.error(f'Запрос от сервера - {new_homework}')
            time.sleep(TIME_OUT)
            logger.info("Очередной запрос по циклу while статуса домашки")
        except Exception as e:
            logger.error(f'Бот упал с ошибкой: {e}')
            print(f'Бот упал с ошибкой: {e}')
            time.sleep(5)
            continue


if __name__ == '__main__':
    main()
