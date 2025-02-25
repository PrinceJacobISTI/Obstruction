from flask import Flask, render_template, Response, jsonify
import cv2

app = Flask(__name__)

camera = cv2.VideoCapture(0)  # Change to video file path if using a recorded video
obstruction_detected = False

def generate_frames():
    global obstruction_detected
    while True:
        success, frame = camera.read()
        if not success:
            break

        # Simulate obstruction detection (you can replace this with real AI logic)
        if cv2.waitKey(1) & 0xFF == ord('o'):  # Press 'o' to simulate obstruction
            obstruction_detected = True
        elif cv2.waitKey(1) & 0xFF == ord('c'):  # Press 'c' to clear obstruction
            obstruction_detected = False

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
