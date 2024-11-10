from pyfirmata import Arduino as setArduinoBoard, SERVO, util
from time import sleep as delay

# Inicialização da placa e pinos
board = setArduinoBoard("/dev/ttyUSB0")
servo_pin = 11
led_pin = board.get_pin('d:13:o')

# Configuração do pino do servo
board.digital[servo_pin].mode = SERVO

# Iniciar comunicação com a placa
it = util.Iterator(board)
it.start()

# Função para mover o servo
def move_servo(angle):
    board.digital[servo_pin].write(angle)
    print(f"Servo movido para {angle} graus")

# Loop principal
while True:
    led_pin.write(1)
    move_servo(0)
    delay(1)
    led_pin.write(0)
    move_servo(180)
    delay(1)



