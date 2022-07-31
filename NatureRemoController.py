import time
import threading
import os
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

        # token指定
        self.api = NatureRemoAPI(myToken)
        # デバイス問い合わせ
        self.devices = self.api.get_devices()
        print(self.devices)
        # 家電問い合わせ
        self.appliances = self.api.get_appliances()
        print(self.appliances)

    def readDevice(self):
        """
        デバイス情報を取得する
        """
        t = threading.Thread(target=self.__readDevice)
        t.start()

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

    def sendSignal(self, nickname, signalName):
        """
        指定した信号名の信号を送信する

        Args:
            nickname (string): 家電名
            signalName (string): 信号名
        """
        t = threading.Thread(target=self.__sendSignal, args=(nickname,signalName))
        t.start()

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

    def sendOnSignal(self, nickname):
        """
        オン信号を送信する

        Args:
            nickname (string): 家電名
        """
        t = threading.Thread(target=self.__sendSignal, args=(nickname,"オン"))
        t.start()

    def sendOnSignals(self, nickname, repetNum=3):
        """
        指定した回数オン信号を送信する

        Args:
            nickname (string): 家電名
        """
        t = threading.Thread(target=self.__sendOnSignals, args=(nickname, repetNum))
        t.start()

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

    def sendOnSignalLight(self, nickname):
        """
        照明をつける

        Args:
            nickname (string): 家電名
        """
        t = threading.Thread(target=self.__sendOnSignalLight, args=(nickname,))
        t.start()

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

    def sendOffSignalLight(self, nickname):
        """
        照明を消す

        Args:
            nickname (string): 家電名
        """
        t = threading.Thread(target=self.__sendOffSignalLight, args=(nickname,))
        t.start()

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


# サンプルコード
if __name__ == "__main__":
    # 環境変数を読み込む
    load_dotenv()
    NATURE_REMO_TOKEN = os.environ.get("NATURE_REMO_TOKEN", "Your Nature Remo Token")
    ROOM_LIGHT_NAME = os.environ.get("ROOM_LIGHT_NAME", "Your Light Name")
    # NatureRemoに接続
    remo = NatureRemoController(NATURE_REMO_TOKEN)
    while 1:
        remo.sendOnSignalLight(ROOM_LIGHT_NAME)
        remo.readDevice()
        time.sleep(15)
        remo.sendOffSignalLight(ROOM_LIGHT_NAME)
        remo.readDevice()
        time.sleep(15)
