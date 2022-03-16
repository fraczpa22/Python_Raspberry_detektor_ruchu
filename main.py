import smbus
import time
from time import sleep
import Adafruit_SSD1306
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from gpiozero import LED, Button
import subprocess
import math

PWR_MGMT_1   = 0x6B
SMPLRT_DIV   = 0x19
CONFIG       = 0x1A
GYRO_CONFIG  = 0x1B
INT_ENABLE   = 0x38
ACCEL_XOUT_H = 0x3B
ACCEL_YOUT_H = 0x3D
ACCEL_ZOUT_H = 0x3F

Device_Address_MPU = 0x68   # MPU6050 device address

def MPU_Init():
    # Write to power management register
    bus.write_byte_data(Device_Address_MPU, PWR_MGMT_1, 1)
def read_raw_data_MPU(addr):
    # Accelero and Gyro value are 16-bit
    high = bus.read_byte_data(Device_Address_MPU, addr)
    low = bus.read_byte_data(Device_Address_MPU, addr + 1)

    # concatenate higher and lower value
    value = ((high << 8) | low)

    # to get signed value from mpu6050
    if (value > 32768):
        value = value - 65536
    return value

bus = smbus.SMBus(1)  # or bus = smbus.SMBus(0) for older version boards

MPU_Init()

RST = None
disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST)
disp.begin()
disp.clear()
disp.display()
width = disp.width
height = disp.height
image = Image.new('1', (width, height))
draw = ImageDraw.Draw(image)
draw.rectangle((0,0,width,height), outline=0, fill=0)
padding = -2
top = padding
bottom = height-padding

os_x = 0

font = ImageFont.load_default()
draw.rectangle((0,0,width,height), outline=0, fill=0)

led = []
led.append(LED(17))
led.append(LED(27))
led.append(LED(22))
led.append(LED(23))

button = []
button.append(Button(6))
button.append(Button(13))
button.append(Button(19))
button.append(Button(26))

print("Reading Data of Accelerometer")
doklatnosc = 0.03

while True:
    end2 = 0
    end1 = 0
    Alarm = 1
    while end1 == 0:
        draw.text((os_x + 20, top + 12), "Alarm wylaczony!!", font=font, fill=255)
        disp.image(image)
        disp.display()
        for i in range(4):
            if button[i].is_pressed:
                print("Button " + str(i))
                led[i].on()
                if button[1].is_pressed:
                    for i in range(4):
                        led[0].on()
                        led[1].on()
                        led[2].off()
                        led[3].off()
                        sleep(0.3)
                        led[2].on()
                        led[3].on()
                        led[0].off()
                        led[1].off()
                        sleep(0.3)
                    end1 = 1
            else:
                led[i].off()

    x = read_raw_data_MPU(ACCEL_XOUT_H)
    y = read_raw_data_MPU(ACCEL_YOUT_H)
    z = read_raw_data_MPU(ACCEL_ZOUT_H)
    x1 = x / 16384.0
    y1 = y / 16384.0
    z1 = z / 16384.0

    while end2 == 0:
        x = read_raw_data_MPU(ACCEL_XOUT_H)
        y = read_raw_data_MPU(ACCEL_YOUT_H)
        z = read_raw_data_MPU(ACCEL_ZOUT_H)
        Ax = x / 16384.0
        Ay = y / 16384.0
        Az = z / 16384.0
        if Alarm == 0:

            draw.rectangle((0, 0, width, height), outline=0, fill=0)
            draw.text((os_x+20, top + 12), "Alarm wylaczony!!", font=font, fill=255)
            disp.image(image)
            disp.display()
            end2 = 1
        elif x1-doklatnosc < Ax < x1+doklatnosc and y1-doklatnosc < Ay < y1+doklatnosc and z1-doklatnosc < Az < z1+doklatnosc:
            draw.rectangle((0, 0, width, height), outline=0, fill=0)
            draw.text((os_x+30, top + 8), "Czujnik ruchu", font=font, fill=255)
            draw.text((os_x+30, top + 18), "nie ruszac!!", font=font, fill=255)
            disp.image(image)
            disp.display()
            x1 = x / 16384.0
            y1 = y / 16384.0
            z1 = z / 16384.0

        else:
            draw.rectangle((0, 0, width, height), outline=0, fill=0)
            draw.text((os_x + 50, top + 12), "ALARM!!", font=font, fill=255)
            disp.image(image)
            disp.display()
            for i in range(4):
                    led[i].on()
                    sleep(0.1)
                    led[i].off()
                    sleep(0.1)
            x1 = x / 16384.0
            y1 = y / 16384.0
            z1 = z / 16384.0

        for i in range(4):
            if button[i].is_pressed:
                print("Button " + str(i))
                led[i].on()
                if button[2].is_pressed:
                    Alarm = 0
                    for i in range(4):
                            led[0].on()
                            led[1].on()
                            led[2].off()
                            led[3].off()
                            sleep(0.3)
                            led[2].on()
                            led[3].on()
                            led[0].off()
                            led[1].off()
                            sleep(0.3)

            else:
                led[i].off()

        print("\tAx=%.2f g" % Ax, "\tAy=%.2f g" % Ay, "\tAz=%.2f g" % Az)
        sleep(0.1)








