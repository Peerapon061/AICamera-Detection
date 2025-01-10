import cv2
import paho.mqtt.client as mqtt
from ultralytics import YOLO
import string
import random
import mysql.connector

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
    print("Not Connect")


# MQTT connection setup
host = "10.4.41.248"
port = 1883
client = mqtt.Client()
client.username_pw_set("test", "1234")
client.connect(host)

confident_round=10

def on_connect(client, userdata, flags, rc):
    # subscribe ไปยัง topic ที่ต้องการ
    client.subscribe("reset/value")
client.on_connect = on_connect

def on_message(client, userdata, msg):
    if msg.topic == "topic1":
        print(f"Message received on topic1: {msg.payload.decode()}")
    elif msg.topic == "topic2":
        print(f"Message received on topic2: {msg.payload.decode()}")
client.on_message = on_message
    

def generate_random_code():
    characters = string.ascii_uppercase + string.digits  # Letters (A-Z) and numbers (0-9)
    code = ''.join(random.choice(characters) for _ in range(5))  # Generate a random 5-character code
    return code

# Load the YOLO model
model = YOLO('runs/detect/train2/weights/best.pt')

def open_camera():
    created_RedeemCode=True
    # Open a video capture object (0 for the default camera)
    cap = cv2.VideoCapture(1)  # Change this to 1 if you want to use the secondary camera

    while cap.isOpened():
        ret, frame = cap.read()

        if not ret:
            print("Failed to grab frame")
            break

        # Resize and flip the frame
        frame = cv2.resize(frame, (640, 480))
        frame = cv2.flip(frame, 1)

        # Perform YOLO detection
        results = model(frame)

        # Process the detection results
        for result in results:
            boxes = result.boxes  # Bounding boxes detected
            if boxes is not None:
                for box in boxes:
                    # Extract class ID and confidence score
                    class_id = int(box.cls.item())
                    confidence = box.conf.item()
                    class_name = model.names[class_id]  # Get class name from model

                    # Display class name and confidence on the frame
                    label = f"{class_name}: {confidence:.2f}"
                    (x1, y1, x2, y2) = map(int, box.xyxy[0].tolist())
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                    if(confidence>=0.555 and created_RedeemCode):
                        client.publish("createNew/redeemCode",generate_random_code())
                        created_RedeemCode = False

        # Display the frame with YOLO detections
        cv2.imshow('Camera Detection', frame)

        # Exit when 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Exiting...")
            break

    # Release the video capture object and close the OpenCV windows
    cap.release()
    cv2.destroyAllWindows()

open_camera()
