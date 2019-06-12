from importlib import import_module
import os
from flask import Flask, render_template, Response, request, make_response
from functools import wraps
import cv2

app = Flask(__name__)




def auth_required(f):
    wraps(f)

    def decorated(*args, **kwargs):
        auth = request.authorization
        if auth and auth.username == 'username' and auth.password == 'password':
            return f(*args, *kwargs)
        else:
            return make_response('contraseña errónea', 401, {'WWW-Authenticate': 'Basic realm="Login required"'})
    return decorated




def find_camera(id):
    cameras = ["rtsp://admin:PCuervo03!@192.168.0.210:554/1/1",
                "rtsp://admin:PCuervo03!@192.168.0.214:554/1/1",
                "rtsp://admin:PCuervo03!@192.168.0.215:554/1/1",
                "rtsp://admin:PCuervo03!@192.168.0.216:554/1/1",
                "rtsp://admin:PCuervo03!@192.168.0.217:554/1/1"]
    return cameras[int(id)]
#  for cctv camera use rtsp://username:password@ip_address:554/user=username_password='password'_channel=channel_number_stream=0.sdp' instead of camera
#  for webcam use zero(0)
 

def gen_frames(camera_id):
     
    cam = find_camera(camera_id)
    cap=  cv2.VideoCapture(cam)
    
    while True:
        # for cap in caps:
        # # Capture frame-by-frame
        success, frame = cap.read()  # read the camera frame
        frame = cv2.resize(frame,(500,360))
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result


@app.route('/video_feed/<string:id>/', methods=["GET"])
def video_feed(id):
   
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen_frames(id),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/', methods=["GET"])
@auth_required
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True)
