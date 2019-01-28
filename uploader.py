
import os
import time
from flask import Flask, jsonify, request
app = Flask(__name__)

UPLOAD_FOLDER = '/home/ryan/precise/upload'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
@app.route('/precise/upload', methods=['POST'])
def home():
    uploads = request.files
    for precisefile in uploads:
        fn = uploads[precisefile].filename
        if fn == 'audio':
            name = (str(int(time.time()))) + ".wav"
            uploads[precisefile].save(os.path.join(app.config['UPLOAD_FOLDER'], name))
            print("Saved audio file")
        if fn == 'metadata':
            name =  (str(int(time.time()))) + ".meta"
            uploads[precisefile].save(os.path.join(app.config['UPLOAD_FOLDER'], name))
            print("Saved metadata file")

    return jsonify({"status":"ok"})


app.run(debug=True,host='0.0.0.0')

