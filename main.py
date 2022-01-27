# */
# * @Henry Medina
# * @author John Heber Mendoza
# * @Universidad del Area Andina
# */

from machine import Pin, ADC, I2C
import utime
from ssd1306 import SSD1306_I2C
from hcsr04 import HCSR04
from time import sleep
from dht import DHT11
from utime import sleep
import network, time, urequests

def conectaWifi (red, password):
      global miRed
      miRed = network.WLAN(network.STA_IF)     
      if not miRed.isconnected():              #Si no está conectado…
          miRed.active(True)                   #activa la interface
          miRed.connect(red, password)         #Intenta conectar con la red
          print('Conectando a la red', red +"…")
          timeout = time.time ()
          while not miRed.isconnected():           #Mientras no se conecte..
              if (time.ticks_diff (time.time (), timeout) > 10):
                  return False
      return True

sensorDHT = DHT11(Pin(32))
file = open("otro.csv", "w")

led_rojo = Pin(25, Pin.OUT)
led_verde = Pin(13, Pin.OUT)
led_azul = Pin(14, Pin.OUT)

ancho = 128
alto = 64
tamaño = 9

medidor = HCSR04 (trigger_pin = 21, echo_pin = 22)# Sensor ultrasonido
i2c = I2C(0, scl=Pin(5), sda=Pin(23))
oled = SSD1306_I2C(ancho, alto, i2c)

sensor = ADC(Pin(36))
sensor.width(ADC.WIDTH_12BIT)  # permite regular la precisión de lectura
sensor.atten(ADC.ATTN_11DB) # permite trabajar con 3.3v

# Calibrar.... de acuerdo a las especificaciones del sensor
#sensor = ADC(Pin(39))
#sensor.atten(ADC.ATTN_11DB) # calibrar de 0 a 3.6 v
#sensor.atten(ADC.ATTN_11DB) # establecer resolucion de 10 bits hasta 1023


print(i2c.scan())

if conectaWifi ("DIRECTV_19455A", "Medina1985"):

    print ("Conexión exitosa!")
    print('Datos de la red (IP/netmask/gw/DNS):', miRed.ifconfig())
    
    url = "https://api.thingspeak.com/update?api_key=VB8X3ICJ2J97VG4L"

while True:
    # sensor
    oled.fill(0)
    try:
        distan = round((tamaño-medidor.distance_cm ())/tamaño*100,0)
        distanc = medidor.distance_cm ()
        distancia = str(round((tamaño-medidor.distance_cm ())/tamaño*100)) + "  %"
        print ("Llenado = ", distancia)
        print ("Llenado = ", distan)
        print ("Llenado = ", distanc)
        sleep (1)
    except:
        print ("Error!")
        
    utime.sleep_ms(1)
    sensorDHT.measure()
    temp = sensorDHT.temperature()
    hum = sensorDHT.humidity()
    kelvin = temp + 273
    print(str("T={:02d} ºC, H={:02d} %  K= {:02d} k   ".format(temp, hum, kelvin) ))
    
    lectura =  round(((4095-int(sensor.read()))*1200)/4095)
    print(lectura)
    utime.sleep_ms(1)

       
    #mostrar en pantalla oled
    oled.text("INFORMACION TANQUE:", 0, 0)
    oled.text("Llenado:", 0, 10)
    oled.text(distancia, 65, 10)
    oled.text("Tempera:",0,20)
    oled.text(str(temp)+"  C",65,20)
    oled.text("Humedad:",0,30)                
    oled.text(str(hum)+"  %",65,30)
    oled.text("Kelvin : ",0,40)                
    oled.text(str(kelvin)+ " k",65,40)
    oled.text("Aire   : ",0,50)
    oled.text(str(lectura)+ " PPM",65,50)
    oled.show()
    utime.sleep_ms(1)
    #oled.fill(1)
    #oled.show()
    #utime.sleep(4)
    
    if distan < 30:
        
        led_rojo.value(1)
        led_verde.value(0)
        led_azul.value(0)
        
    elif distan < 70 and distan >= 30:
        
        led_rojo.value(0)
        led_verde.value(0)
        led_azul.value(1)
        
    elif distan >= 70:
        
        led_rojo.value(0)
        led_verde.value(1)
        led_azul.value(0)
    
    else:
        led_rojo.value(0)
        led_verde.value(0)
        led_azul.value(0)
    
    utime.sleep_ms(1)
    
    respuesta = urequests.get(url+"&field1="+str(distan)+"&field2="+str(temp)+"&field3="+str(hum)+"&field4="+str(lectura)+"&field5="+str(kelvin))
    print(respuesta.text)
    print (respuesta.status_code)
    respuesta.close ()
else:
    print ("Imposible conectar")
    miRed.active (False)