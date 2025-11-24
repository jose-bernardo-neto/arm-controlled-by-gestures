import cv2
import mediapipe as mp
from pyfirmata import Arduino as setArduinoBoard, util, SERVO
from time import sleep as delay
from math import sqrt, ceil

# Definindo a porta e os pinos do LED
port = "/dev/ttyUSB0"
board = setArduinoBoard(port)
led_pin = board.get_pin('d:4:o')
dir_pin = board.get_pin('d:13:o')
servo_pin = [11,9]
board.digital[servo_pin[0]].mode = SERVO
board.digital[servo_pin[1]].mode = SERVO

# Configurando Mediapipe para detecção de mãos
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# Inicializando captura de vídeo
cap = cv2.VideoCapture(0)
hands = mp_hands.Hands()

def calculate_distance(point1, point2):
    return sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)

def move_servo(angle,INDEX):
    board.digital[servo_pin[INDEX]].write(angle)
    print(f"Servo {INDEX} movido para {angle} graus")

def is_hand_open(hand_landmarks):
    index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    index_finger_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP]
    middle_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
    middle_finger_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP]
    ring_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
    ring_finger_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_MCP]
    pinky_tip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]
    pinky_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_MCP]
    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    thumb_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_CMC]
    
    index_dist = calculate_distance(index_finger_tip, index_finger_mcp)
    middle_dist = calculate_distance(middle_finger_tip, middle_finger_mcp)
    ring_dist = calculate_distance(ring_finger_tip, ring_finger_mcp)
    pinky_dist = calculate_distance(pinky_tip, pinky_mcp)
    thumb_dist = calculate_distance(thumb_tip, thumb_mcp)
    
    avg_dist = (index_dist + middle_dist + ring_dist + pinky_dist + thumb_dist) / 5
    avg_dist = ceil(avg_dist * 100)
    
    return avg_dist < 7

while True:
    data, image = cap.read()
    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
    results = hands.process(image)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
            index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            
            hand_open = is_hand_open(hand_landmarks)
            
            if hand_open:
                led_pin.write(0)
                move_servo(180,0)
            else:
                led_pin.write(1)
                move_servo(0,0)
            
            hand_x = index_finger_tip.x - wrist.x
            
            if hand_x > 0.05:
                dir_pin.write(1)  # Mão virada para a esquerda
                move_servo(0,1)

            elif hand_x < -0.05:
                dir_pin.write(0)  # Mão virada para a direita
                move_servo(180,1)

            else:
                dir_pin.write(0)  # Mão alinhada horizontalmente
                move_servo(90,1)
                
            delay(0.01)
    else:
        led_pin.write(0)
        dir_pin.write(0)
        delay(0.01)
    
    cv2.imshow('HandTracker', image)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()


