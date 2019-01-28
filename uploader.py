import os
import time
from flask import Flask, jsonify, request
app = Flask(__name__)

UPLOAD_FOLDER = '/home/pi/precise/upload'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
@app.route('/precise/upload', methods=['POST'])
def home():
    wavfile = request.files['audio']
    metafile = request.files['metadata']
    name = str(int(time.time())) + ".wav"
    wavfile.save(os.path.join(app.config['UPLOAD_FOLDER'], name))
    metafile.save(os.path.join(app.config['UPLOAD_FOLDER'], name))
    return jsonify({"status":"ok"})
        
app.run(debug=True,host='0.0.0.0')
