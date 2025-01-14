import cv2
import mediapipe as mp
import paho.mqtt.client as mqtt
host = "10.4.41.26"
port = 1883
client = mqtt.Client()
client.username_pw_set("test", "1234")
client.connect(host)

# Initialize MediaPipe Hands module
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()

model = YOLO('runs/detect/train/weights/best.onnx')

# Initialize MediaPipe Drawing module for drawing landmarks
mp_drawing = mp.solutions.drawing_utils

# Open a video capture object (0 for the default camera)
cap = cv2.VideoCapture(0)  # Change this to 1 if you want to use the secondary camera

def count_fingers(hand_landmarks, handedness):
    # Define a list for the landmarks of tips of the 5 fingers (indexing from thumb to pinky)
    finger_tips = [4, 8, 12, 16, 20]
    open_fingers = 0
    
    # Count the thumb based on handedness
    if handedness == "Right":
        if hand_landmarks.landmark[finger_tips[0]].x < hand_landmarks.landmark[3].x:
            open_fingers += 1
    else:
        if hand_landmarks.landmark[finger_tips[0]].x > hand_landmarks.landmark[3].x:
            open_fingers += 1
    
    # For other fingers, compare the tip and the DIP joint
    for tip in finger_tips[1:]:
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip - 2].y:
            open_fingers += 1
    
    return open_fingers

while cap.isOpened():
    ret, frame = cap.read()
    
    if not ret:
        print("Failed to grab frame")
        break
    
    # Resize and flip the frame
    frame = cv2.resize(frame, (640, 480))
    frame = cv2.flip(frame, 1)
    
    # Convert the frame to RGB format
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Process the frame to detect hands
    results = hands.process(frame_rgb)
    
    if results.multi_hand_landmarks:
        for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            hand_type = handedness.classification[0].label
            fingers_open = count_fingers(hand_landmarks, hand_type)
            
            # Draw landmarks on the frame
            # mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Determine the action based on the number of open fingers
            if fingers_open == 0:  # All fingers closed
                client.publish("ai/hand-gesture","OFF") # Send 'OFF' to turn off the LED
                action_message = "Turn off light"

                print(action_message)
            elif fingers_open == 5:  # All fingers opened
                client.publish("ai/hand-gesture","ON") # Send 'ON' to turn on the LED
                action_message = "Turn on light"
                print(action_message)
                
            else:
                action_message = f"Intermediate state: {fingers_open} fingers open. No action taken."
                print(action_message)
 
                

            # Display action message on the frame
            cv2.putText(frame, action_message, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
            
    # Display the frame with hand landmarks
    cv2.imshow('Hand Recognition', frame)
    
    # Exit when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Exiting...")
        break

# Release the video capture object and close the OpenCV windows
cap.release()
cv2.destroyAllWindows()