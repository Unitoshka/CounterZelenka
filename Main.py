import httpx
import time
import json
import logging
import sys


from enum import Enum
from httpx import Response

#Логирование, зачем вы сюда залезли?
logging.basicConfig(level=logging.INFO, format="%(asctime)s | counter.unitoshka.fun | %(levelname)s | %(message)s")

with open('config.json', 'r', encoding='utf8') as f:
    config = json.load(f)


class CounterType(Enum):
    Sympathies = 'user_like_count'
    User_Messages = 'user_message_count'



class Counter():
    def __init__(self, token: str) -> None:
        self.token = token
        self.headers = {'Authorization': f'Bearer {self.token}',
                                "accept": "application/json"}
        self.baseUrl = "https://api.zelenka.guru"

    def edit_message(self, message_id: int, post_body: str) -> None:
        with httpx.Client(headers=self.headers) as client:
            data = {"post_body": post_body}

            request = client.put(url=f'{self.baseUrl}/profile-posts/{message_id}',
                                 data=data)

    def get_profile(self) -> dict:
        with httpx.Client(headers=self.headers) as client:
            request = client.get(url=f'{self.baseUrl}/users/me')

            if request.json().get('error'):
                logging.critical('Ваш токен невалиден')
                sys.exit()

        return request.json()

    def get_list(self, counter_type: CounterType) -> list[int]:
        profile = self.get_profile()
        value = profile.get('user').get(counter_type.value)
        split = [int(i) for i in str(value)]

        return split

    @staticmethod
    def list_to_counter(split: list[int]) -> list[str]:
        counter_list: list[str] = []

        file_format = 'gif' if 'gif' in config['theme'] else 'png' # Говнокодик)

        for number in split:
            counter_list.append(f'[IMG={config["attributes"]}]https://counter.unitoshka.fun/themes/{config["theme"]}/{number}.{file_format}[/IMG]')

        return counter_list

class Updater():
    @staticmethod
    def get_version() -> int | float | None:
        try:
            with open('version.txt', 'r') as file:
                return float(file.read())
        except IOError:
            return None

    @staticmethod
    def get_update() -> None:
        version = Updater.get_version()

        if isinstance(version, (float, int)):
            actual_version = float(httpx.get(url='https://raw.githubusercontent.com/Unitoshka/CounterZelenka/master/version.txt').text)

            if version < actual_version:
                logging.warning('Обновите свою версию на https://github.com/Unitoshka/CounterZelenka/tree/master')
                return
            logging.info('У вас актуальная версия counter.unitoshka.fun')
            return
        logging.error('У вас отсутствует файл version.txt, создайте его чтобы получать обновления')



if __name__ == '__main__':
    counter = Counter(token=config['token'])

    counter_type = CounterType[config['counter_type']]
    logging.info('Программа запущена')

    Updater.get_update()

    while True:
        list_ = counter.get_list(counter_type=counter_type)
        counter_list = counter.list_to_counter(list_)

        counter_text = ' '.join(counter_list)
        message = str(config["message_text"]).replace("{counter}", counter_text)

        time.sleep(10)

        counter.edit_message(message_id=config['message_id'], post_body=message)
        logging.info('Сообщение было заменено')

        time.sleep(10)