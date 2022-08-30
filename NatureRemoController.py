import datetime
import os
import threading
import time

from dotenv import load_dotenv
# APIモジュールのインポート
from remo import NatureRemoAPI


class NatureRemoController:
    """
    NatureRemoコントローラ
    """

    def __init__(self, myToken):
        """
        コンストラクタ
        """
        # 温度
        self.temperature = 0
        # 湿度
        self.humidity = 0
        # 照度
        self.illumination = 0
        # 人感センサ
        self.movement = 0
        # 送信回数
        self.sendCnt = 0

        # token指定
        self.api = NatureRemoAPI(myToken)
        # デバイス問い合わせ
        self.devices = self.getDevices()
        print(self.devices)
        # 家電問い合わせ
        while not self.canRequest():
            time.sleep(1)
        self.appliances = self.getAppliances()
        print(self.appliances)

    def getUser(self):
        self.sendCnt = 0
        return self.api.get_user()

    def getDevices(self):
        self.sendCnt = 0
        return self.api.get_devices()

    def getAppliances(self):
        self.sendCnt = 0
        return self.api.get_appliances()

    def readDevice(self) -> bool:
        """
        デバイス情報を取得する
        """
        if self.canRequest():
            self.sendCnt += 1
            t = threading.Thread(target=self.__readDevice)
            t.start()
            return True
        else:
            return False

    def __readDevice(self):
        """
        デバイス情報を取得する
        """
        self.devices = self.api.get_devices()
        for device in self.devices:
            self.temperature = device.newest_events["te"].val
            self.humidity = device.newest_events["hu"].val
            self.illumination = device.newest_events["il"].val
            self.movement = device.newest_events["mo"].val
            print(
                str(device.name)
                + ": "
                + str(self.temperature)
                + ", "
                + str(self.humidity)
                + ", "
                + str(self.illumination)
                + ", "
                + str(self.movement)
            )

    def sendSignal(self, nickname, signalName) -> bool:
        """
        指定した信号名の信号を送信する

        Args:
            nickname (string): 家電名
            signalName (string): 信号名
        """
        if self.canRequest():
            self.sendCnt += 1
            t = threading.Thread(target=self.__sendSignal, args=(nickname, signalName))
            t.start()
            return True
        else:
            return False

    def __sendSignal(self, nickname, signalName):
        """
        指定した信号名の信号を送信する

        Args:
            nickname (string): 家電名
            signalName (string): 信号名
        """
        for appliance in self.appliances:
            if appliance.nickname == nickname:
                for signal in appliance.signals:
                    if signal.name == signalName:
                        self.api.send_signal(signal.id)
                        print("### send " + signalName + " signal to " + appliance.nickname + " ###")

    def sendOnSignal(self, nickname) -> bool:
        """
        オン信号を送信する

        Args:
            nickname (string): 家電名
        """
        return self.sendSignal(nickname, "オン")

    def sendOnSignals(self, nickname, repetNum=3):
        """
        指定した回数オン信号を送信する

        Args:
            nickname (string): 家電名
        """
        if self.canRequest(repetNum):
            self.sendCnt += repetNum
            t = threading.Thread(target=self.__sendOnSignals, args=(nickname, repetNum))
            t.start()
            return True
        else:
            return False

    def __sendOnSignals(self, nickname, repetNum=1):
        """
        指定した回数オン信号を送信する

        Args:
            nickname (string): 家電名
        """
        self.__sendSignal(nickname, "オン")
        repetNum -= 1
        if repetNum > 0:
            for num in range(repetNum):
                time.sleep(1)
                self.__sendSignal(nickname, "オン")

    def sendOnSignalLight(self, nickname) -> bool:
        """
        照明をつける

        Args:
            nickname (string): 家電名
        """
        if self.canRequest():
            self.sendCnt += 1
            t = threading.Thread(target=self.__sendOnSignalLight, args=(nickname,))
            t.start()
            return True
        else:
            return False

    def __sendOnSignalLight(self, nickname):
        """
        照明をつける

        Args:
            nickname (string): 家電名
        """
        for appliance in self.appliances:
            if appliance.nickname == nickname:
                self.api.send_light_infrared_signal(appliance.id, "on")
                print("### send on signal to " + appliance.nickname + " ###")

    def sendOffSignalLight(self, nickname) -> bool:
        """
        照明を消す

        Args:
            nickname (string): 家電名
        """
        if self.canRequest():
            self.sendCnt += 1
            t = threading.Thread(target=self.__sendOffSignalLight, args=(nickname,))
            t.start()
            return True
        else:
            return False

    def __sendOffSignalLight(self, nickname):
        """
        照明を消す

        Args:
            nickname (string): 家電名
        """
        for appliance in self.appliances:
            if appliance.nickname == nickname:
                self.api.send_light_infrared_signal(appliance.id, "off")
                print("### send off signal to " + appliance.nickname + " ###")

    def getRemainCnt(self) -> int:
        """
        残り送信可能な回数を取得する
        Returns:
            int: 残り送信可能な回数
        """
        return self.api.rate_limit.remaining - self.sendCnt

    def getResetTime(self) -> int:
        """
        制限が解除されるまでの時間
        Returns:
            int: 制限が解除されるまでの時間[s]
        """
        delta = self.api.rate_limit.reset - (datetime.datetime.now() - datetime.timedelta(hours=9))
        return int(delta.total_seconds())

    def canRequest(self, num=1) -> bool:
        """
        NatureRemoにリクエストできるかどうか
        Args:
            num (int, optional): リクエストするコマンドの数. Defaults to 1.
        Returns:
            bool: True:リクエスト可能
        """
        if self.getResetTime() < 0:
            print(self.getUser())
        if self.getRemainCnt() > num:
            print(
                "canRequest(): OK. remain cnt = "
                + str(self.getRemainCnt())
                + ", resetTime = "
                + str(self.getResetTime())
                + ", rate_limit = "
                + str(self.api.rate_limit)
            )
            return True
        else:
            print(
                "canRequest(): Too Many Requests. remain cnt = "
                + str(self.getRemainCnt())
                + ", resetTime = "
                + str(self.getResetTime())
                + ", rate_limit = "
                + str(self.api.rate_limit)
            )
            return False


# サンプルコード
if __name__ == "__main__":
    # 環境変数を読み込む
    load_dotenv()
    NATURE_REMO_TOKEN = os.environ.get("NATURE_REMO_TOKEN", "Your Nature Remo Token")
    DEVICE_NAME = os.environ.get("DEVICE_NAME", "Your Nature Remo Token")
    # NatureRemoに接続
    remo = NatureRemoController(NATURE_REMO_TOKEN)
    while 1:
        print(remo.sendSignal(DEVICE_NAME, "ch_up"))
        time.sleep(3)
        print(remo.sendSignal(DEVICE_NAME, "ch_down"))
        time.sleep(3)
