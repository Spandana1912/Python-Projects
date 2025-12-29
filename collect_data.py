import cv2
import os

DATA_PATH = "collected_data"

# Create main data folder if not present
if not os.path.exists(DATA_PATH):
    os.makedirs(DATA_PATH)

# Create 10 folders for digits 0–9
for i in range(10):
    folder = os.path.join(DATA_PATH, str(i))
    if not os.path.exists(folder):
        os.makedirs(folder)

cap = cv2.VideoCapture(0)

current_label = input("Enter the digit label you want to collect (0-9): ").strip()
print("Press 'q' to quit.")

count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    cv2.imshow("Collecting Data - Press q to stop", frame)

    # save every frame inside the correct folder
    save_path = os.path.join(DATA_PATH, current_label, f"{count}.jpg")
    cv2.imwrite(save_path, frame)
    count += 1

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print(f"[INFO] Saved {count} images for label {current_label}.")
