import cv2
from flask import Flask, render_template, Response, jsonify

app = Flask(__name__)

camera = cv2.VideoCapture(0)  # 0 for webcam, or use a video file
obstruction_detected = False

# Define the fixed bounding box (Region of Interest - ROI)
ROI_X, ROI_Y, ROI_WIDTH, ROI_HEIGHT = 200, 150, 300, 300  # Adjust as needed
    
def generate_frames():
    global obstruction_detected

    while True:
        success, frame = camera.read()
        if not success:
            break

        # Convert frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # Detect edges in the ROI only
        roi = blurred[ROI_Y:ROI_Y + ROI_HEIGHT, ROI_X:ROI_X + ROI_WIDTH]
        edges = cv2.Canny(roi, 50, 150)

        # Find objects inside the ROI
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        detected = False  # Assume no obstruction

        for contour in contours:
            if cv2.contourArea(contour) > 500:  # Adjust sensitivity
                detected = True  # Obstruction detected
                break

        obstruction_detected = detected  # Update status

        # Draw the fixed bounding box on the frame
        color = (0, 0, 255) if obstruction_detected else (0, 255, 0)  # Red if blocked, Green if clear
        cv2.rectangle(frame, (ROI_X, ROI_Y), (ROI_X + ROI_WIDTH, ROI_Y + ROI_HEIGHT), color, 3)

        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/alert-status')
def alert_status():
    return jsonify({'obstruction': obstruction_detected})

if __name__ == '__main__':
    app.run(debug=True)
