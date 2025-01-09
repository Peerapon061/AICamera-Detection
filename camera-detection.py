import cv2
import paho.mqtt.client as mqtt
from ultralytics import YOLO

# MQTT connection setup
host = "10.4.41.26"
port = 1883
client = mqtt.Client()
client.username_pw_set("test", "1234")
client.connect(host)

# Load the YOLO model
model = YOLO('runs/detect/train2/weights/best.pt')

# Open a video capture object (0 for the default camera)
cap = cv2.VideoCapture(0)  # Change this to 1 if you want to use the secondary camera

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
                if(confidence>=0.6):
                    label = f"{class_name}: {confidence:.2f}"
                    (x1, y1, x2, y2) = map(int, box.xyxy[0].tolist())
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    # Display the frame with YOLO detections
    cv2.imshow('Hand Recognition with YOLO', frame)

    # Exit when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Exiting...")
        break

# Release the video capture object and close the OpenCV windows
cap.release()
cv2.destroyAllWindows()