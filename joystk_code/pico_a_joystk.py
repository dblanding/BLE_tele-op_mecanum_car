# pico_a_joystk.py (aka main.py)

import aioble
import asyncio
import bluetooth
from machine import Pin, ADC
from math import pi
import struct
from sys import exit
from geom2d import r2p, p2r

# Define UUIDs for the service and characteristic
_SERVICE_UUID = bluetooth.UUID(0x1848)
_CHARACTERISTIC_UUID = bluetooth.UUID(0x2A6E)

# IAM = "Central" # Change to 'Peripheral' or 'Central'
IAM = "Peripheral"

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

adc_x = ADC(Pin(26))
adc_y = ADC(Pin(27))
adc_z = ADC(Pin(28))

def read_joystk():
    # get joystick axis values
    js_x = adc_x.read_u16()
    js_y = adc_y.read_u16()
    js_z = adc_z.read_u16()
    
    # convert u16 values to values between -10 and +10
    x = js_x * (20 / 65535.0) - 10
    y = js_y * (20 / 65535.0) - 10
    z = js_z * (20 / 65535.0) - 10

    # rotate joystick by 45 degrees
    r, theta = r2p(x, y)
    theta -= pi/4
    x, y = p2r(r, theta)
    
    return round(x), round(y), round(z)
    
def encode_message(message):
    """ Encode a message to bytes """
    return message.encode('utf-8')

def decode_message(message):
    """ Decode a message from bytes """
    return message.decode('utf-8')

async def send_data_task(connection, characteristic):
    """ Send data to the connected device """
    while True:
        if not connection:
            print("error - no connection in send data")
            continue

        if not characteristic:
            print("error no characteristic provided in send data")
            continue
        
        x, y, z = read_joystk()
        message = f"{x}, {y}, {z}"
        print(f"sending {message}")

        try:
            msg = encode_message(message)
            characteristic.write(msg)

            await asyncio.sleep(0.1)
            response = decode_message(characteristic.read())

            #print(f"{IAM} sent: {message}, response {response}")
        except Exception as e:
            print(f"writing error {e}")
            continue

        await asyncio.sleep(0.1)

async def receive_data_task(characteristic):
    """ Receive data from the connected device """
    while True:
        try:
            data = await characteristic.read()

            if data:
                print(f"{IAM} received: {decode_message(data)}")
                await characteristic.write(encode_message("Got it"))
                await asyncio.sleep(0.1)

        except asyncio.TimeoutError:
            print("Timeout waiting for data in {ble_name}.")
            break
        except Exception as e:
            print(f"Error receiving data: {e}")
            break

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
