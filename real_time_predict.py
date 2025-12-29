import cv2
import mediapipe as mp
import numpy as np
from tensorflow.keras.models import load_model

# Load the CNN model that was trained on 64x64 images
model = load_model("gesture_model.h5")

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

IMG_SIZE = 64  # Model input size

cap = cv2.VideoCapture(0)

with mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
) as hands:

    predicted_digit = -1

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        h, w, c = frame.shape
        imgRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(imgRGB)

        if result.multi_hand_landmarks:
            hand_landmarks = result.multi_hand_landmarks[0]

            # Draw landmarks
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Get bounding box of hand
            xs = [lm.x for lm in hand_landmarks.landmark]
            ys = [lm.y for lm in hand_landmarks.landmark]

            x_min, x_max = int(min(xs) * w), int(max(xs) * w)
            y_min, y_max = int(min(ys) * h), int(max(ys) * h)

            # Expand bounding box slightly
            margin = 20
            x_min = max(x_min - margin, 0)
            y_min = max(y_min - margin, 0)
            x_max = min(x_max + margin, w)
            y_max = min(y_max + margin, h)

            # Crop the hand region
            hand_img = frame[y_min:y_max, x_min:x_max]

            if hand_img.size > 0:
                # Resize to model input
                hand_img = cv2.resize(hand_img, (IMG_SIZE, IMG_SIZE))
                hand_img = hand_img.astype("float32") / 255.0
                hand_img = np.expand_dims(hand_img, axis=0)

                # Predict digit
                pred = model.predict(hand_img, verbose=0)
                predicted_digit = np.argmax(pred)

        # UI box
        cv2.rectangle(frame, (0, 0), (220, 80), (0, 0, 0), -1)
        cv2.putText(frame, f"Digit: {predicted_digit}", (10, 55),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)

        cv2.imshow("Real-time Gesture Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
