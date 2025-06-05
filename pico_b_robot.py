# pico_b_robot.py (aka main.py)


import aioble
import bluetooth
import asyncio
import struct
from sys import exit
from pico_car import Motor

# Define UUIDs for the service and characteristic
_SERVICE_UUID = bluetooth.UUID(0x1848)
_CHARACTERISTIC_UUID = bluetooth.UUID(0x2A6E)

# IAM = "Central" # Change to 'Peripheral' or 'Central'
IAM = "Central"

if IAM not in ['Peripheral','Central']:
    print("IAM must be either Peripheral or Central")
    exit()

if IAM == "Central":
    IAM_SENDING_TO = "Peripheral"
else:
    IAM_SENDING_TO = "Central"

MESSAGE = f"Hello from {IAM}!"

# Bluetooth parameters
BLE_NAME = f"{IAM}"  # You can dynamically change this if you want unique names
BLE_SVC_UUID = bluetooth.UUID(0x181A)
BLE_CHARACTERISTIC_UUID = bluetooth.UUID(0x2A6E)
BLE_APPEARANCE = 0x0300
BLE_ADVERTISING_INTERVAL = 2000
BLE_SCAN_LENGTH = 5000
BLE_INTERVAL = 30000
BLE_WINDOW = 30000

# state variables
joyvals = (0, 0, 0)

##### Motor control code #####

# Use the Motor class provided by Adeept
motor = Motor()

# individual motors
m1 = motor.motor_left_front
m2 = motor.motor_right_front
m3 = motor.motor_right_back
m4 = motor.motor_left_back

def mtr1(spd):
    """Run motor1 at spd (int) from -100 to 100"""
    if spd < 0:  # backward
        direction = -1
    else:  # forward
        direction = 1
    m1(1, direction, abs(spd))

def mtr2(spd):
    """Run motor2 at spd (int) from -100 to 100"""
    if spd < 0:  # backward
        direction = -1
    else:  # forward
        direction = 1
    m2(1, direction, abs(spd))

def mtr3(spd):
    """Run motor3 at spd (int) from -100 to 100"""
    if spd < 0:  # backward
        direction = -1
    else:  # forward
        direction = 1
    m3(1, direction, abs(spd))

def mtr4(spd):
    """Run motor4 at spd (int) from -100 to 100"""
    if spd < 0:  # backward
        direction = -1
    else:  # forward
        direction = 1
    m4(1, direction, abs(spd))

def drive_motors(joyvals):
    jsx, jsy, jsz = joyvals
    x = jsx * 10
    y = jsy * 10
    z = jsz * 5

    m1_spd = x-z
    m2_spd = y+z
    m3_spd = x+z
    m4_spd = y-z

    mtr1(m1_spd)
    mtr2(m2_spd)
    mtr3(m3_spd)
    mtr4(m4_spd)
    
    print(m1_spd, m2_spd, m3_spd, m4_spd)

##### End of motor code #####

def encode_message(message):
    """ Encode a message to bytes """
    return message.encode('utf-8')

def decode_message(message):
    """ Decode a message from bytes """
    return message.decode('utf-8')

async def send_data_task(connection, characteristic):
    """ Send data to the connected device """
    global joyvals
    while True:
        if not connection:
            print("error - no connection in send data")
            continue

        if not characteristic:
            print("error no characteristic provided in send data")
            continue

        message = f"{MESSAGE} Got joyvals = {joyvals}"
        print(f"sending {message}")

        try:
            msg = encode_message(message)
            characteristic.write(msg)

            await asyncio.sleep(0.1)
            response = decode_message(characteristic.read())

            print(f"{IAM} sent: {message}, response {response}")
        except Exception as e:
            print(f"writing error {e}")
            continue

        await asyncio.sleep(0.1)

async def receive_data_task(characteristic):
    """ Receive data from the connected device """
    global joyvals
    while True:
        try:
            data = await characteristic.read()

            if data:
                joyvals_string = decode_message(data)
                joy_string_list = joyvals_string.split(',')
                joyvals = [int(str_val) for str_val in joy_string_list]
                print(joyvals)
                drive_motors(joyvals)
                print(f"{IAM} received: {decode_message(data)}")
                #await characteristic.write(encode_message(f"Got {joyvals}"))
                await asyncio.sleep(0.1)

        except asyncio.TimeoutError:
            print("Timeout waiting for data in {ble_name}.")
            break
        except Exception as e:
            print(f"Error receiving data: {e}")
            continue

async def run_peripheral_mode():
    """ Run the peripheral mode """

    # Set up the Bluetooth service and characteristic
    ble_service = aioble.Service(BLE_SVC_UUID)
    characteristic = aioble.Characteristic(
        ble_service,
        BLE_CHARACTERISTIC_UUID,
        read=True,
        notify=True,
        write=True,
        capture=True,
    )
    aioble.register_services(ble_service)

    print(f"{BLE_NAME} starting to advertise")

    while True:
        async with await aioble.advertise(
            BLE_ADVERTISING_INTERVAL,
            name=BLE_NAME,
            services=[BLE_SVC_UUID],
            appearance=BLE_APPEARANCE) as connection:
            print(f"{BLE_NAME} connected to another device: {connection.device}")

            tasks = [
                asyncio.create_task(send_data_task(connection, characteristic)),
            ]
            await asyncio.gather(*tasks)
            print(f"{IAM} disconnected")
            break

async def ble_scan():
    """ Scan for a BLE device with the matching service UUID """

    print(f"Scanning for BLE Beacon named {BLE_NAME}...")

    async with aioble.scan(5000, interval_us=30000, window_us=30000, active=True) as scanner:
        async for result in scanner:
            if result.name() == IAM_SENDING_TO and BLE_SVC_UUID in result.services():
                print(f"found {result.name()} with service uuid {BLE_SVC_UUID}")
                return result
    return None

async def run_central_mode():
    """ Run the central mode """

    # Start scanning for a device with the matching service UUID
    while True:
        device = await ble_scan()

        if device is None:
            continue
        print(f"device is: {device}, name is {device.name()}")

        try:
            print(f"Connecting to {device.name()}")
            connection = await device.device.connect()

        except asyncio.TimeoutError:
            print("Timeout during connection")
            continue

        print(f"{IAM} connected to {connection}")

        # Discover services
        async with connection:
            try:
                service = await connection.service(BLE_SVC_UUID)
                characteristic = await service.characteristic(BLE_CHARACTERISTIC_UUID)
            except (asyncio.TimeoutError, AttributeError):
                print("Timed out discovering services/characteristics")
                continue
            except Exception as e:
                print(f"Error discovering services {e}")
                await connection.disconnect()
                continue

            tasks = [
                asyncio.create_task(receive_data_task(characteristic)),
            ]
            await asyncio.gather(*tasks)

            await connection.disconnected()
            print(f"{BLE_NAME} disconnected from {device.name()}")
            break

async def main():
    """ Main function """
    motor.motor_stop()
    while True:
        if IAM == "Central":
            tasks = [
                asyncio.create_task(run_central_mode()),
            ]
        else:
            tasks = [
                asyncio.create_task(run_peripheral_mode()),
            ]

        await asyncio.gather(*tasks)

asyncio.run(main())
