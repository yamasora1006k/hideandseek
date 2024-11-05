import asyncio
from bleak import BleakClient, discover
from struct import pack
import firebase_admin
from firebase_admin import credentials, firestore

# サービスアカウントの認証情報ファイルを読み込む
cred = credentials.Certificate('/Users/itougakuto/hideandseek-python/config/hide-data.json')
firebase_admin.initialize_app(cred)

# Firestoreデータベースにアクセス
db = firestore.client()

# UUIDs
CORE_INDICATE_UUID = '72c90005-57a9-4d40-b746-534e22ec9f9e'
CORE_NOTIFY_UUID = '72c90003-57a9-4d40-b746-534e22ec9f9e'
CORE_WRITE_UUID = '72c90004-57a9-4d40-b746-534e22ec9f9e'

# 定数
MESSAGE_TYPE_INDEX = 0
EVENT_TYPE_INDEX = 1
STATE_INDEX = 2
MESSAGE_TYPE_ID = 1
EVENT_TYPE_ID = 0

# コールバック関数
def on_receive(sender, data: bytearray):
    data = bytes(data)
    print(f"[{sender}] 受信データ: {data}")

def on_receive_indicate(sender, data: bytearray):
    data = bytes(data)
    print(f"[{sender}] [indicate] {data}")

async def scan(prefix='MESH-100'):
    """指定されたプレフィックスでデバイスをスキャンし、最初に見つかったデバイスを返す。"""
    while True:
        print('デバイスをスキャン中...')
        devices = await discover()
        matched_devices = [d for d in devices if d.name and d.name.startswith(prefix)]
        if matched_devices:
            return matched_devices[0]
        await asyncio.sleep(2)  # 次のスキャンまで2秒待機

async def handle_button(client, event_queue, num):
    """ボタンデバイスのイベントを処理し、特定のイベントをキューに送信する。"""
    def button_notify(sender, data: bytearray):
        """ボタンの通知を受信した際のコールバック関数。"""
        if len(data) < 3:
            return
        if data[MESSAGE_TYPE_INDEX] != MESSAGE_TYPE_ID or data[EVENT_TYPE_INDEX] != EVENT_TYPE_ID:
            return
        state = data[STATE_INDEX]
        if state == 1:
            print('Single Pressed. ')
            db.collection('orders').document('BUTTON').update({'true': 1})
        elif state == 2:
            print('Long Pressed.')
        elif state == 3:
            print('Double Pressed.')

    # 通知の開始
    await client.start_notify(CORE_NOTIFY_UUID, button_notify)
    await client.start_notify(CORE_INDICATE_UUID, on_receive_indicate)

    # 初期コマンドの送信
    initial_command = pack('<BBBB', 0, 2, 1, 3)
    await client.write_gatt_char(CORE_WRITE_UUID, initial_command, response=True)
    print('ボタンデバイスに接続しました。')

    # ハンドラーを常に動作させるためのループ
    while True:
        await asyncio.sleep(1)

async def handle_led(client, event_queue):
    """LEDデバイスを制御し、キューからのイベントに応じてコマンドを送信する。"""
    # 通知の開始
    await client.start_notify(CORE_NOTIFY_UUID, on_receive)
    await client.start_notify(CORE_INDICATE_UUID, on_receive_indicate)

    # 初期コマンドの送信
    initial_command = pack('<BBBB', 0, 2, 1, 3)
    await client.write_gatt_char(CORE_WRITE_UUID, initial_command, response=True)
    print('LEDデバイスに接続しました。')

    # 白色LED用のコマンドを生成
    def create_white_command():
        messagetype = 1
        red = 255
        green = 255
        blue = 255
        duration = 0  # 0は無限点灯を意味する場合があります
        on = 0
        off = 0
        pattern = 0  # 0: 固定点灯
        command = pack('<BBBBBBBHHHB', messagetype, 0, red, 0, green, 0, blue, duration, on, off, pattern)
        checksum = sum(command) & 0xFF
        command += pack('B', checksum)
        return command

    white_command = create_white_command()

    # イベント処理ループ
    while True:
        event = await event_queue.get()
        if event == 'single_press':
            print('Single Pressイベントを処理します：2秒後にLEDを白色にします。')
            await asyncio.sleep(2)
            try:
                await client.write_gatt_char(CORE_WRITE_UUID, white_command, response=True)
                print('LEDを白色に設定しました。')
            except Exception as e:
                print('LEDの設定中にエラーが発生しました:', e)
        event_queue.task_done()

async def handle_vibration(client):
    """振動デバイスの通知を処理する"""
    def vibration_notify(sender, data: bytearray):
        """振動デバイスの通知を受信した際のコールバック関数。"""
        print('振動イベントが発生しました。')
        db.collection('orders').document('VIBRATION').update({'true': 1})

    # 通知の開始
    await client.start_notify(CORE_NOTIFY_UUID, vibration_notify)
    print('振動デバイスに接続しました。')

    # ハンドラーを常に動作させるためのループ
    while True:
        await asyncio.sleep(1)

async def main():
    # Firebaseの初期化
    db.collection('orders').document('BUTTON').set({'kind': 'button', 'true': 0})
    db.collection('orders').document('VIBRATION').set({'kind': 'vibration', 'true': 0})
    db.collection('orders').document('LED').set({'kind': 'LED', 'true': 0})

    # ボタンデバイスをスキャン
    device_button = await scan('MESH-100BU')
    print('ボタンデバイスを見つけました:', device_button.name, device_button.address)

    # LEDデバイスをスキャン
    device_led = await scan('MESH-100LE')
    print('LEDデバイスを見つけました:', device_led.name, device_led.address)

    # 振動デバイスをスキャン
    device_vibration = await scan('MESH-100VI')
    print('振動デバイスを見つけました:', device_vibration.name, device_vibration.address)

    # 共有キューの作成
    event_queue = asyncio.Queue()

    # ボタンのプッシュ回数を保持
    num = 0

    # 両方のデバイスに接続
    async with BleakClient(device_button, timeout=None) as client_button, \
               BleakClient(device_led, timeout=None) as client_led, \
               BleakClient(device_vibration, timeout=None) as client_vibration:

        # 各デバイスの接続が確立していることを確認
        if not client_button.is_connected:
            await client_button.connect()
        if not client_led.is_connected:
            await client_led.connect()
        if not client_vibration.is_connected:
            await client_vibration.connect()

        print('全てのデバイスに接続しました。')

        # 各デバイスのハンドラーをタスクとして開始
        button_task = asyncio.create_task(handle_button(client_button, event_queue, num))
        led_task = asyncio.create_task(handle_led(client_led, event_queue))
        vibration_task = asyncio.create_task(handle_vibration(client_vibration))

        # 並行して全てのタスクを実行
        await asyncio.gather(button_task, led_task, vibration_task)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('\nプログラムを終了します。')
