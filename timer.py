from time import sleep
import max7219
from machine import Pin, SoftSPI
import network
import ntptime
import time
lim=0
t=3
l=16
spi = SoftSPI(baudrate=10000000, polarity=1, phase=0, sck=Pin(18), mosi=Pin(23),miso=Pin(32))
spi2 = SoftSPI(baudrate=10000000, polarity=1, phase=0, sck=Pin(4), mosi=Pin(2),miso=Pin(32))
spi3 = SoftSPI(baudrate=10000000, polarity=1, phase=0, sck=Pin(12), mosi=Pin(14),miso=Pin(32))
ss = Pin(5, Pin.OUT)
ss2 = Pin(19, Pin.OUT)
ss3 = Pin(27, Pin.OUT)
display = max7219.Matrix8x8(spi, ss, l)
display2 = max7219.Matrix8x8(spi2, ss2, l)
display3 = max7219.Matrix8x8(spi3, ss3, l)
B1=Pin(21, Pin.IN, Pin.PULL_UP)
B2=Pin(22, Pin.IN, Pin.PULL_UP)
B3=Pin(0, Pin.IN, Pin.PULL_UP)
B4=Pin(15, Pin.IN, Pin.PULL_UP)
B1s = B1.value()
B2s = B2.value()
B3s = False  
B4s = B4.value()
ciclo = False
modo_reloj_activo = False

def reloj_callback(pin):
    global modo_reloj_activo
    modo_reloj_activo = not modo_reloj_activo  # Alterna el modo
    print("Modo reloj activado" if modo_reloj_activo else "Modo reloj desactivado")
# Función para conectar a la red Wi-Fi
def conectar():
    red = "TP-Link_0C7D"
    contraseña = "86497640"
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(red, contraseña)
    while not wlan.isconnected():
        time.sleep(1)
    print("Conexión Wi-Fi establecida")   
def reloj(pin):
    conectar()
    try:
        ntptime.settime()
        print("Hora sincronizada")
    except Exception as e:
        print("Error al sincronizar la hora:", e)

    # Mostrar hora en las pantallas
    while modo_reloj_activo:
        utc = time.localtime()
        tm = time.localtime(time.mktime(utc) - (6 * 3600))  # Ajuste de zona horaria
        hora2 = "{:02}:{:02}:{:02}".format(tm[3], tm[4], tm[5])
        
        display.fill(0)
        display2.fill(0)
        display3.fill(0)
        display3.large_text(hora2, 0, 1, t)
        display2.large_text(hora2, 0, -7, t)
        display.large_text(hora2, 0, -15, t)
        
        display.show()
        display2.show()
        display3.show()
        sleep(1)
        
def boton_callback(pin):
    global B3s, ciclo
    if pin.value() == 0:  
        if not B3s:  
            B3s = True  
            if ciclo:  
                ciclo = False
                #print("STOP")
            else:  
                ciclo = True
                #print("START")
        sleep(0.3)  
    else:
        B3s = False
segundos=lim%60
minutos=int(lim/60)%60
#horas=int(lim/3600)
def display_print(minutos,segundos):
    display.fill(0)
    display2.fill(0)
    display3.fill(0)
    display3.large_text(f"{minutos:02}:{segundos:02}", 8,1, t)
    display2.large_text(f"{minutos:02}:{segundos:02}", 8,-7, t)
    display.large_text(f"{minutos:02}:{segundos:02}",8,-15, t)
    display.show()
    display2.show()
    display3.show()
def display_print_start():
    display.fill(0)
    display2.fill(0)
    display3.fill(0)
    display3.large_text("START", 0,1, t)
    display2.large_text("START", 0,-7, t)
    display.large_text("START", 0,-15, t)
    display.show()
    display2.show()
    display3.show()
def display_print_stop():
    display.fill(0)
    display2.fill(0)
    display3.fill(0)
    display3.large_text("STOP", 0,1, t)
    display2.large_text("STOP", 0,-7, t)
    display.large_text("STOP", 0,-15, t)
    display.show()
    display2.show()
    display3.show()
def aumentar_minutos(pin):
    global lim, minutos
    lim += 60
    minutos += 1
    print(f"Cuenta regresiva:{minutos:02}:{segundos:02}")
    display_print(minutos,segundos)
def disminuir_minutos(pin):
    global lim, minutos
    lim -= 60
    minutos -= 1
    if minutos<0:
        minutos=0
        #lim=0
    print(f"Cuenta regresiva:{minutos:02}:{segundos:02}")
    display_print(minutos,segundos)
B1.irq(trigger=Pin.IRQ_FALLING, handler=disminuir_minutos)
B2.irq(trigger=Pin.IRQ_FALLING, handler=aumentar_minutos)
B3.irq(trigger=Pin.IRQ_FALLING, handler=boton_callback)
B4.irq(trigger=Pin.IRQ_FALLING, handler=reloj_callback)
def timer():
        sleep(1)
        for x in range (lim,0,-1):
            if not ciclo:  
                break
            segundos=x%60
            minutos=int(x/60)%60
            #horas=int(x/3600)
            display_print(minutos,segundos)
            print(f"{minutos:02}:{segundos:02}")
            sleep(1)
        

while True:
    if ciclo:
        display_print_start()
        print("START")
        timer()
        B3.irq(trigger=Pin.IRQ_FALLING, handler=boton_callback)
        lim=0
        segundos=0
        minutos=0
        display_print_stop()
        print("STOP")
        ciclo = False
    if modo_reloj_activo:
        reloj(None)
    sleep(0.1)
