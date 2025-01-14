import cv2
import paho.mqtt.client as mqtt
from ultralytics import YOLO
import string
import random
import mysql.connector
import json

# Database Connection
con = mysql.connector.connect(
    host="10.4.41.66",
    port=3306,
    user="root",
    password="root",
    database="app"
)
if con.is_connected():
    print("Connected to the database")
else:
    print("Not Connected")

# MQTT Setup
host = "mqtt.bookmark.scnd.app"
port = 1883
client = mqtt.Client()
client.username_pw_set("iothack", "iot1234")
client.connect(host)

# Global Variables
is_detect_from_ultrasonic = False
is_duplicate_RedeemCode = True
limit_round = 0

def generate_random_code():
    characters = string.ascii_uppercase + string.digits  # Letters (A-Z) and numbers (0-9)
    return ''.join(random.choice(characters) for _ in range(5))  # Generate a random 5-character code

# Load the YOLO Model
model = YOLO('runs/detect/train/weights/best.pt')

def open_camera():
    global is_detect_from_ultrasonic, limit_round, is_duplicate_RedeemCode

    cap = cv2.VideoCapture(0)# Open camera (0 for default)
    width = 1280  # Desired width
    height = 720  # Desired height

    # Set properties
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    
    if not cap.isOpened():
        print("Error: Camera not accessible.")
        return

    try:
        while cap.isOpened() and is_detect_from_ultrasonic and limit_round <= 1000:
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame")
                break

            # Resize and flip the frame
            frame = cv2.resize(frame, (1920, 1080))
            frame = cv2.flip(frame, 1)

            # Perform YOLO detection
            results = model(frame)

            # Process Detection Results
            for result in results:
                boxes = result.boxes
                if boxes is not None and con.is_connected():
                    for box in boxes:
                        class_id = int(box.cls.item())
                        confidence = box.conf.item()
                        class_name = model.names[class_id]

                        if (confidence >= 0.6 and class_name=="bottle")or(confidence >= 0.1 and class_name=="can"):
                            while (is_duplicate_RedeemCode):
                                redeem_code = generate_random_code()
                                cursor = con.cursor()
                                query2 = "SELECT redeem_code FROM trash_records WHERE redeem_code = %s"
                                values_check = (redeem_code,)  # Ensure values is a tuple
                                cursor.execute(query2, values_check)
                                result = cursor.fetchone()
                                if not result:
                                    is_duplicate_RedeemCode=False
                            message_data = {
                                "item": class_name,
                                "code": redeem_code
                            }
                            query_insert = "INSERT INTO trash_records (trash_type, redeem_code) VALUES (%s, %s)"
                            values_insert = (class_name, redeem_code)
                            cursor.execute(query_insert, values_insert)
                            con.commit()
                            print("Record inserted successfully.")
                            client.publish("bottleSeparator/trash", json.dumps(message_data))
                            is_detect_from_ultrasonic = False
                            limit_round = 0
                            is_duplicate_RedeemCode=True
                        else:
                            limit_round += 1

            # Timeout for detection round
            if limit_round == 1000:
                client.publish("bottleSeparator/trash", json.dumps({"item": "Not_Both", "code": "Not_Both"}))

            # Display Detection Frame
            cv2.imshow('Camera Detection', frame)

            # Break if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Exiting...")
                break
    except Exception as e:
        print(f"Error during camera operation: {e}")
    finally:
        cap.release()
        cv2.destroyAllWindows()

def on_connect(client, userdata, flags, rc):
    client.subscribe("bottleSeparator/camera")

def on_message(client, userdata, msg):
    global is_detect_from_ultrasonic
    if msg.topic == "bottleSeparator/camera":
        print(f"Message received: {msg.payload.decode()}")
        is_detect_from_ultrasonic = True

client.on_connect = on_connect
client.on_message = on_message
client.loop_start()

try:
    while True:
        if is_detect_from_ultrasonic:
            limit_round = 0
            open_camera()
except KeyboardInterrupt:
    print("Stopping MQTT client...")
    client.loop_stop()
    client.disconnect()
