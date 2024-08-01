import sys
import requests
from colorama import init, Fore
from fake_useragent import UserAgent
import base64
import time


class PixelTod:
    def __init__(self):
        self.base_headers = {
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Origin': 'https://hamsterkombatgame.io',
            'Referer': 'https://hamsterkombatgame.io/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'Content-Type': 'application/json',
            'User-Agent': self.get_random_user_agent()
        }

    def get_random_user_agent(self):
        ua = UserAgent()
        return ua.random

    def main(self):
        with open("initdata.txt", "r") as file:
            datas = file.read().splitlines()

        print(f'{Fore.LIGHTYELLOW_EX}Обнаружено аккаунтов: {len(datas)}')
        if not datas:
            print(f'{Fore.LIGHTYELLOW_EX}Пожалуйста, введите свои данные в initdata.txt')
            sys.exit()
        print('-' * 50)

        for no, data in enumerate(datas):
            print(f'{Fore.LIGHTYELLOW_EX}Номер аккаунта: {Fore.LIGHTWHITE_EX}{no + 1}')
            self.claim_key(data)
            print('-' * 50)

    def claim_key(self, auth_token):
        headers = self.base_headers.copy()
        headers["Authorization"] = f"{auth_token}"
        sync_response = requests.post("https://api.hamsterkombatgame.io/clicker/sync", headers=headers)
        user_id = str(sync_response.json()["clickerUser"]["id"])
        encoded_cipher = base64.b64encode(f"0300000000|{user_id}".encode()).decode()
        time.sleep(1)
        start_response = requests.post("https://api.hamsterkombatgame.io/clicker/start-keys-minigame", headers=headers)

        if start_response.status_code == 400:
            error_response = start_response.json()
            if error_response.get("error_code") == "KEYS-MINIGAME_WAITING":
                print("Вы уже получили ключи")
                return
            else:
                print(f"Ошибка запуска мини-игры: {start_response.status_code}, {start_response.text}")
                return

        time.sleep(2)

        claim_response = requests.post(
            "https://api.hamsterkombatgame.io/clicker/claim-daily-keys-minigame",
            headers=headers,
            json={"cipher": encoded_cipher}
        )
        if claim_response.status_code == 200:
            response_json = claim_response.json()
            balance_keys = response_json['clickerUser']['balanceKeys']
            bonus_keys = response_json['dailyKeysMiniGame']['bonusKeys']
            print(f"Баланс ключей: {balance_keys}")
            print(f"Ключи за мини-игру: +{bonus_keys}")
            return
        elif claim_response.status_code == 400:
            print("Вы уже получили ключи сегодня")
            return
        else:
            error_message = claim_response.json().get("error_message", "Неизвестная ошибка")
            print(f"Ошибка получения ежедневных ключей: {claim_response.status_code}, {error_message}")
            return

if __name__ == "__main__":
    try:
        app = PixelTod()
        app.main()
    except KeyboardInterrupt:
        sys.exit()
