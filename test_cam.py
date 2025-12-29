import cv2
import mediapipe as mp
import math
import numpy as np
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# AUDIO SETUP
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

vol_min, vol_max = volume.GetVolumeRange()[0], volume.GetVolumeRange()[1]

# MEDIAPIPE
mpHands = mp.solutions.hands
hands = mpHands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.9,
    min_tracking_confidence=0.9
)
mpDraw = mp.solutions.drawing_utils

# CAMERA
cap = cv2.VideoCapture(0)

filtered_dist = 0
alpha = 0.25

while True:
    success, img = cap.read()
    if not success:
        print("❌ Camera not found.")
        break

    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            lmList = []
            h, w, c = img.shape

            for id, lm in enumerate(handLms.landmark):
                lmList.append([id, int(lm.x * w), int(lm.y * h)])

            x1, y1 = lmList[4][1], lmList[4][2]
            x2, y2 = lmList[8][1], lmList[8][2]

            # UI in white
            cv2.circle(img, (x1, y1), 8, (255, 255, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 8, (255, 255, 255), cv2.FILLED)
            cv2.line(img, (x1, y1), (x2, y2), (255, 255, 255), 2)

            raw_dist = math.hypot(x2 - x1, y2 - y1)

            filtered_dist = alpha * raw_dist + (1 - alpha) * filtered_dist
            dist = filtered_dist

            vol = np.interp(dist, [20, 180], [vol_min, vol_max])
            volume.SetMasterVolumeLevel(vol, None)

            vol_bar = np.interp(dist, [20, 180], [400, 150])
            vol_percent = np.interp(dist, [20, 180], [0, 100])

            # Volume bar (white border, gray fill)
            cv2.rectangle(img, (50, 150), (85, 400), (255, 255, 255), 2)
            cv2.rectangle(img, (50, int(vol_bar)), (85, 400), (180, 180, 180), cv2.FILLED)

            # White text
            cv2.putText(img, f"Volume: {int(vol_percent)}%", (40, 120),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 3)

            mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS,
                mpDraw.DrawingSpec(color=(255, 255, 255), thickness=2, circle_radius=2),
                mpDraw.DrawingSpec(color=(200, 200, 200), thickness=2)
            )

    cv2.imshow("Gesture Volume Control (Dark UI)", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
