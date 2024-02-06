import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from gpiozero import DistanceSensor, Button, Buzzer, Motor, LED
from time import sleep
from tkgpio import TkCircuit
import smtplib
from email.message import EmailMessage
import ssl
import cv2
import datetime
import os
import time

def video_email(video_file_path):
    email_sender = 'gnew71669@gmail.com'
    email_password = 'wvkvaahfhuqktidt'
    email_receiver = 'testmailbme@gmail.com'

    subject = 'Recorded Video'
    body = 'This is the recorded video from a CCTV camera view!'

    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(body)

    # Attach the video file
    with open(video_file_path, 'rb') as video_file:
        video_data = video_file.read()
        em.add_attachment(video_data, maintype='application', subtype='octet-stream', filename=os.path.basename(video_file_path))

    context = ssl.create_default_context()

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(email_sender, email_password)
            smtp.sendmail(email_sender, email_receiver, em.as_string())
        print("Video email sent successfully!")
    except Exception as e:
        print(f"An error occurred while sending the email: {e}")

# Fetch the service account key JSON file contents
cred = credentials.Certificate('data.json')

# Initialize the app with a service account, granting admin privileges
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://console.firebase.google.com/u/0/project/bm425-project/database/bm425-project-default-rtdb/data/~2F'
})

# As an admin, the app has access to read and write all data, regardless of Security Rules
# Get a database reference
ref = db.reference('/command')

# Send true or false based on condition
if condition:
    ref.set(True)
else:
    ref.set(False)

configuration = {
    "name": "Smart WheelChair",
    "width": 800,
    "height": 600,
    "motors": [
        {"x": 450, "y": 50, "name": "DC1", "forward_pin": 8, "backward_pin": 9},
        {"x": 450, "y": 250, "name": "DC2", "forward_pin": 10, "backward_pin": 11},
    ],
    "buttons": [
        {"x": 20, "y": 30, "name": "FPB", "pin": 14},
        {"x": 80, "y": 30, "name": "BPB", "pin": 15},
        {"x": 160, "y": 30, "name": "LPB", "pin": 16},
        {"x": 240, "y": 30, "name": "RPB", "pin": 3},
        {"x": 300, "y": 30, "name": "SPB", "pin": 2},
        {"x": 360, "y": 30, "name": "HPB", "pin": 1},
    ],
    "distance_sensors": [
        {"x": 100, "y": 130, "name": "US1", "trigger_pin": 17, "echo_pin": 18, "min_distance": 0, "max_distance": 30},
        {"x": 100, "y": 230, "name": "US2", "trigger_pin": 19, "echo_pin": 22, "min_distance": 0, "max_distance": 30},
        {"x": 100, "y": 330, "name": "US3", "trigger_pin": 20, "echo_pin": 21, "min_distance": 0, "max_distance": 30},
        {"x": 100, "y": 430, "name": "US4", "trigger_pin": 23, "echo_pin": 5, "min_distance": 0, "max_distance": 30},
    ],
    "buzzers": [
        {"x": 550, "y": 50, "name": "buzzer", "pin": 4},
    ],
    "leds": [
        {"x": 550, "y": 110, "name": "Help_LED", "pin": 6},
    ],
}
circuit = TkCircuit(configuration)

@circuit.run
def main():
    buzzer = Buzzer(4)
    DC1 = Motor(8, 9)
    DC2 = Motor(10, 11)
    State = ["Idle", "Forward", "Backward", "Left", "Right", "Obstacle Detected", "Recording", "Help", "Emergency"]

    US1 = DistanceSensor(18, 17)
    US2 = DistanceSensor(22, 19)
    US3 = DistanceSensor(21, 20)
    US4 = DistanceSensor(5, 23)

    FPB = Button(14)
    BPB = Button(15)
    LPB = Button(16)
    RPB = Button(3)
    SPB = Button(2)
    HPB = Button(1)
    HELP_LED = LED(6)

    def help_email():
        email_sender = 'gnew71669@gmail.com'
        email_password = 'wvkvaahfhuqktidt'
        email_receiver = 'testmailbme@gmail.com'

        subject = 'HELP!!'
        body = '''Help is needed by the patient!
    Please check what is the matter?'''

        em = EmailMessage()
        em['From'] = email_sender
        em['To'] = email_receiver
        em['Subject'] = subject
        em.set_content(body)

        context = ssl.create_default_context()

        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
                smtp.login(email_sender, email_password)
                smtp.sendmail(email_sender, email_receiver, em.as_string())
            print("Help email sent successfully!")
        except Exception as e:
            print(f"An error occurred while sending the email: {e}")

    def FPB_pressed():
        global current_state
        DC1.forward()
        DC2.forward()
        buzzer.off()
        current_state = "Forward"
        print("FPB is pressed, moving:", current_state)

    def BPB_pressed():
        global current_state
        DC1.backward()
        DC2.backward()
        buzzer.off()
        current_state = "Backward"
        print("BPB is pressed, moving:", current_state)

    def LPB_pressed():
        global current_state
        DC1.backward()
        DC2.forward()
        buzzer.off()
        current_state = "Left"
        print("LPB is pressed, moving:", current_state)

    def RPB_pressed():
        global current_state
        DC1.forward()
        DC2.backward()
        buzzer.off()
        current_state = "Right"
        print("RPB is pressed, moving:", current_state)

    def SPB_pressed():
        global current_state
        DC1.stop()
        DC2.stop()
        buzzer.off()
        HELP_LED.off()  # Turn off LED
        current_state = "Idle"
        print("SPB is pressed, Current State:", current_state)

    def HPB_pressed():
        global current_state
        DC1.stop()
        DC2.stop()
        buzzer.off()
        current_state = "Help"
        print("HPB is pressed, Current State:", current_state)
        HELP_LED.on()  # Turn on LED
        help_email()  # Send help email
        print("Help is on the way!!!!")

    def stop_motors():
        global current_state
        DC1.stop()
        DC2.stop()
        buzzer.off()
        current_state = "Idle"
        print("Button released. Current State:", current_state)

    FPB.when_pressed = FPB_pressed
    FPB.when_released = stop_motors
    BPB.when_pressed = BPB_pressed
    BPB.when_released = stop_motors
    LPB.when_pressed = LPB_pressed
    LPB.when_released = stop_motors
    RPB.when_pressed = RPB_pressed
    RPB.when_released = stop_motors
    SPB.when_pressed = SPB_pressed
    SPB.when_released = stop_motors
    HPB.when_pressed = HPB_pressed

    obstacle_threshold = 0.05
    current_state = "Idle"

    def get_dist1():
        return US1.distance

    def get_dist2():
        return US2.distance

    def get_dist3():
        return US3.distance

    def get_dist4():
        return US4.distance

    cap = cv2.VideoCapture(0)
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    body_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_fullbody.xml")

    detection = False
    detection_stopped_time = None
    timer_started = False
    SECONDS_TO_RECORD_AFTER_DETECTION = 5

    frame_size = (int(cap.get(3)), int(cap.get(4)))
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = None

    while True:
        _, frame = cap.read()

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        bodies = body_cascade.detectMultiScale(gray, 1.3, 5)

        for face in faces:
            cv2.rectangle(frame, (face[0], face[1]), (face[0] + face[2], face[1] + face[3]), (0, 255, 0), 2)

        if len(faces) + len(bodies) > 0:
            if detection:
                timer_started = False
            else:
                detection = True
                current_time = datetime.datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
                video_filename = f"{current_time}.mp4"
                out = cv2.VideoWriter(video_filename, fourcc, 20, frame_size)
                print("Started Recording!")

        elif detection:
            if timer_started:
                if time.time() - detection_stopped_time >= SECONDS_TO_RECORD_AFTER_DETECTION:
                    detection = False
                    timer_started = False
                    out.release()
                    print('Stop Recording!')
                    video_email(video_filename)

            else:
                timer_started = True
                detection_stopped_time = time.time()

        if detection:
            out.write(frame)

        cv2.imshow("Camera", frame)

        if cv2.waitKey(1) == ord('k'):
            break

    if out is not None:
        out.release()

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
