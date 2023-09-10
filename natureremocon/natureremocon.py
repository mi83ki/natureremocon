"""natureremocon.py

スマートリモコンNatureRemoをコントローラーするクラス

"""

import os
import threading
import time
from datetime import datetime, timedelta

from dotenv import load_dotenv

# APIモジュールのインポート
from remo import Appliance, Device, NatureRemoAPI, User


class NatureRemoController:
    """NatureRemoコントローラ"""

    def __init__(self, my_token: str) -> None:
        """コンストラクタ

        Args:
            my_token (str): NatureRemoトークン
        """
        # 温度
        self._temperature = 0
        # 湿度
        self._humidity = 0
        # 照度
        self._illumination = 0
        # 人感センサ
        self._movement = 0
        # 送信回数
        self._send_cnt = 0
        # 送受信情報
        self._request_name: str = ""

        # token指定
        self.api = NatureRemoAPI(my_token)
        # デバイス問い合わせ
        self.devices: list[Device] = self.get_devices()
        print(self.devices)
        # 家電問い合わせ
        while not self.can_request():
            time.sleep(1)
        self.appliances: list[Appliance] = self.get_appliances()
        print(self.appliances)

    @property
    def request_name(self) -> str:
        """送受信情報を取得する

        Returns:
            str: _description_
        """
        return self._request_name

    def get_user(self) -> User:
        """ユーザー情報を取得する

        Returns:
            User: _description_
        """
        self._send_cnt = 0
        return self.api.get_user()

    def get_devices(self) -> list[Device]:
        """デバイス情報を取得する

        Returns:
            list[Device]: _description_
        """
        self._send_cnt = 0
        return self.api.get_devices()

    def get_appliances(self) -> list[Appliance]:
        """家電情報を取得する

        Returns:
            list[Appliance]: _description_
        """
        self._send_cnt = 0
        return self.api.get_appliances()

    def read_devices(self, callback=None) -> bool:
        """デバイス情報を取得する

        Args:
            callback (_type_, optional): _description_. Defaults to None.

        Returns:
            bool: _description_
        """
        if self.can_request():
            self._send_cnt += 1
            thread = threading.Thread(target=self.__read_device, args=(callback,))
            thread.start()
            return True
        else:
            return False

    def __read_device(self, callback=None):
        """デバイス情報を取得する"""
        self._request_name = "get_devices"
        self.devices = self.get_devices()
        for device in self.devices:
            self._temperature = device.newest_events["te"].val
            self._humidity = device.newest_events["hu"].val
            self._illumination = device.newest_events["il"].val
            self._movement = device.newest_events["mo"].val
            print(
                str(device.name)
                + ": "
                + str(self._temperature)
                + ", "
                + str(self._humidity)
                + ", "
                + str(self._illumination)
                + ", "
                + str(self._movement)
            )
        if callback is not None:
            callback()
        if self._request_name == "get_devices":
            self._request_name = ""

    def send_signal(self, nickname, signal_name, callback=None) -> bool:
        """指定した信号名の信号を送信する

        Args:
            nickname (string): 家電名
            signal_name (string): 信号名
        """
        if self.can_request():
            self._send_cnt += 1
            thread = threading.Thread(
                target=self.__send_signal, args=(nickname, signal_name, callback)
            )
            thread.start()
            return True
        else:
            return False

    def __send_signal(self, nickname, signal_name, callback=None):
        """指定した信号名の信号を送信する

        Args:
            nickname (string): 家電名
            signal_name (string): 信号名
        """
        self._request_name = nickname + ":" + signal_name
        for appliance in self.appliances:
            if appliance.nickname == nickname:
                for signal in appliance.signals:
                    if signal.name == signal_name:
                        self.api.send_signal(signal.id)
                        print(
                            "### send "
                            + signal_name
                            + " signal to "
                            + appliance.nickname
                            + " ###"
                        )
        if callback is not None:
            callback()
        if self._request_name == nickname + ":" + signal_name:
            self._request_name = ""

    def send_on_signal(self, nickname, callback=None) -> bool:
        """オン信号を送信する

        Args:
            nickname (string): 家電名
        """
        return self.send_signal(nickname, "オン", callback)

    def send_on_signals(self, nickname, repeat_num=3, callback=None) -> bool:
        """指定した回数オン信号を送信する

        Args:
            nickname (string): 家電名
        """
        if self.can_request(repeat_num):
            self._send_cnt += repeat_num
            thread = threading.Thread(
                target=self.__send_on_signals, args=(nickname, repetNum, callback)
            )
            thread.start()
            return True
        else:
            return False

    def __send_on_signals(self, nickname, repeat_num=1, callback=None) -> None:
        """指定した回数オン信号を送信する

        Args:
            nickname (string): 家電名
        """
        self.__send_signal(nickname, "オン")
        repeat_num -= 1
        if repeat_num > 0:
            for _ in range(repeat_num):
                time.sleep(1)
                self.__send_signal(nickname, "オン")
        if callback is not None:
            callback()

    def send_on_signal_light(self, nickname, callback=None) -> bool:
        """照明をつける

        Args:
            nickname (string): 家電名
        """
        return self.send_signal_light(nickname, "on", callback)

    def send_off_signal_light(self, nickname, callback=None) -> bool:
        """照明を消す

        Args:
            nickname (string): 家電名
        """
        return self.send_signal_light(nickname, "off", callback)

    def send_signal_light(self, nickname, signal_name, callback=None) -> bool:
        """照明をつける

        Args:
            nickname (string): 家電名
        """
        if self.can_request():
            self._send_cnt += 1
            thread = threading.Thread(
                target=self.__send_signal_light, args=(nickname, signal_name, callback)
            )
            thread.start()
            return True
        else:
            return False

    def __send_signal_light(self, nickname, signal_name, callback=None):
        """照明をつける

        Args:
            nickname (string): 家電名
            signal_name (string): 信号名
        """
        self._request_name = nickname + ":" + signal_name
        for appliance in self.appliances:
            if appliance.nickname == nickname:
                self.api.send_light_infrared_signal(appliance.id, signal_name)
                print(
                    "### send "
                    + signal_name
                    + " signal to "
                    + appliance.nickname
                    + " ###"
                )
        if callback is not None:
            callback()
        if self._request_name == nickname + ":" + signal_name:
            self._request_name = ""

    def get_remain_cnt(self) -> int | None:
        """残り送信可能な回数を取得する

        Returns:
            int | None: 残り送信可能な回数
        """
        remaining = self.api.rate_limit.remaining
        if remaining is not None:
            return remaining - self._send_cnt
        return None

    def get_reset_time(self) -> int | None:
        """制限が解除されるまでの時間

        Returns:
            int | None: 制限が解除されるまでの時間[s]
        """
        reset: datetime | None = self.api.rate_limit.reset
        if reset is not None:
            delta: timedelta = reset - (datetime.now() - timedelta(hours=9))
            return int(delta.total_seconds())
        return None

    def can_request(self, num=1) -> bool:
        """NatureRemoにリクエストできるかどうか

        Args:
            num (int, optional): リクエストするコマンドの数. Defaults to 1.
        Returns:
            bool: True:リクエスト可能
        """
        reset_time: int | None = self.get_reset_time()
        remain_cnt: int | None = self.get_remain_cnt()
        if reset_time is not None and reset_time < 0:
            print(self.get_user())
        if remain_cnt is not None and remain_cnt > num:
            print(
                "can_request(): OK. remain cnt = "
                + str(remain_cnt)
                + ", resetTime = "
                + str(reset_time)
                + ", rate_limit = "
                + str(self.api.rate_limit)
            )
            return True
        else:
            print(
                "can_request(): Too Many Requests. remain cnt = "
                + str(remain_cnt)
                + ", resetTime = "
                + str(reset_time)
                + ", rate_limit = "
                + str(self.api.rate_limit)
            )
            return False


# サンプルコード
def send_callback() -> None:
    """送信コールバック"""
    print("send finished! " + str(datetime.now()))


if __name__ == "__main__":
    # 環境変数を読み込む
    load_dotenv()
    NATURE_REMO_TOKEN = os.environ.get("NATURE_REMO_TOKEN", "Your Nature Remo Token")
    DEVICE_NAME = os.environ.get("DEVICE_NAME", "Your Nature Remo Token")
    # NatureRemoに接続
    remo = NatureRemoController(NATURE_REMO_TOKEN)
    while 1:
        print(remo.request_name)
        print("send start! " + str(datetime.now()))
        print(remo.send_signal(DEVICE_NAME, "ch_up", send_callback))
        print(remo.send_on_signal_light("書斎", send_callback))
        print(remo.request_name)
        time.sleep(3)
        print(remo.request_name)
        print("send start! " + str(datetime.now()))
        print(remo.send_signal(DEVICE_NAME, "ch_down", send_callback))
        print(remo.send_off_signal_light("書斎", send_callback))
        print(remo.request_name)
        time.sleep(3)
