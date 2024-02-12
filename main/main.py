import json
import random
import signal
import threading
import uuid
from datetime import timedelta

from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file, session
from flask_session import Session
import os

import sepdfcsv
import mycache1

app = Flask(__name__)
# Check if FLASK_SECRET_KEY environment variable is set
if 'FLASK_SECRET_KEY' not in os.environ:
    print("ERROR: FLASK_SECRET_KEY environment variable is not set. Please set the secret key and try again.")
    exit(1)

# Set Flask secret key from environment variable
app.secret_key = os.environ['FLASK_SECRET_KEY']

# Set session lifetime to 1 hour (3600 seconds)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)

app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
Session(app)
app.debug = True

# from werkzeug.middleware.profiler import ProfilerMiddleware
app.config["UPLOAD_PDF_FOLDER"] = "pdf"
app.config["UPLOAD_MSG_FOLDER"] = "msg"
app.config["CACHE_URL"] = "http://127.0.0.1:8000"


# app.wsgi_app = ProfilerMiddleware(app.wsgi_app,restrictions=[5], profile_dir='.')
# import mycache

class ExportingThread(threading.Thread):
    def __init__(self, thread_id, sess_id):
        self.progress = 0
        self.mode = ''
        self.thread_id = thread_id
        self.sess_id = sess_id
        # Get the memcached client object
        client = mycache1.create_client()
        my_thread = {
            "progress": self.progress,
            "mode": self.mode,
        }
        str_mythread = json.dumps(my_thread)
        # Store the dictionary in memcached with a key "my_key" for 60 seconds
        client.set(str(thread_id), str_mythread)
        super().__init__()

    def run(self):
        # Your exporting stuff goes here ...
        sepdfcsv.process_pdfs(self.thread_id, self.sess_id)


# index
@app.route("/")
def index():
    sess_number = random.randint(1000, 2000)  # uuid.uuid4()
    if 'sid' not in session:
        session['sid'] = f"{sess_number}"
        # initial = os.getcwd()
        ##os.chdir(initial)
        for path in ('result', 'pdf', 'msg'):
            targ_path = os.path.join(os.getcwd(), path, f"_{session['sid']}")
            os.mkdir(targ_path)
    return render_template("index.html")


# result list dir
@app.route('/<path>')
def list_result(path):
    if 'sid' not in session:
        return render_template("index.html")
    if path not in ('result', 'pdf', 'msg'):
        # != 'result' and path != 'pdf' and path != 'msg':
        return render_template("index.html")
    initial = os.getcwd()
    os.chdir(initial)
    dir_path = os.path.join(os.getcwd(), path, f"_{session['sid']}")
    directory = os.listdir(dir_path)
    ext = ('.csv', '.pdf', '.msg', '.zip')
    file_creation_dates = []
    # Iterate through the files and get their creation dates
    for file_name in directory:
        if file_name.endswith(ext):
            file_path = os.path.join(dir_path, file_name)

            # Check if the file exists (in case of broken symlinks or other issues)
            if os.path.exists(file_path):
                creation_time = os.path.getctime(file_path)
                file_creation_dates.append((file_name, creation_time))

    # Sort the list of files based on their creation dates
    files = sorted(file_creation_dates, key=lambda x: x[1], reverse=True)
    files_sorted = [file[0] for file in files]
    # files = sorted([file for file in directory if file.endswith(ext)], reverse=True)
    return render_template('list_dir.html', path=path, files=files_sorted)


# open a file from link
@app.route("/<path>/<filename>")
def open_file(path, filename):
    try:
        if path == 'result' and 'sid' in session:
            return send_file(f"result/_{session['sid']}/{filename}", as_attachment=True)
        if path == 'pdf' and 'sid' in session:
            return send_file(f"pdf/_{session['sid']}/{filename}", as_attachment=True)

    except Exception as e:
        return str(e)


# async run script processing pdf dir
# async def do_process_pdf():
# Some asynchronous operation that takes time to complete
# ...
@app.route("/run")
def process():
    # sepdfcsv.process_pdfs()
    # return "done"
    return render_template("processing.html")


@app.route("/startproc")
def startprocess():
    if "sid" in session:
        thread_id = random.randint(0, 10000)
        exporting_thread = ExportingThread(thread_id, f"{session['sid']}")
        exporting_thread.start()

        return jsonify(
            id=thread_id,
        )

    return jsonify(
        id=-1,
    )


@app.route('/progress/<int:thread_id>')
def progress(thread_id):
    mc = mycache1.create_client()
    try:
        exporting_thread = mc.get(str(thread_id))
        data_dict = json.loads(exporting_thread['value'])
    except Exception as e:
        data_dict = {}
    if data_dict:
        progress = data_dict.get('progress')
        mode = data_dict.get('mode')
        return jsonify(
            progress=str(progress),
            mode=mode,
        )
    else:
        return jsonify(
            progress='err',
            mode='err',
        )


# upload selected pdf files
@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        if "files" not in request.files:
            return redirect(request.url)

        files = request.files.getlist("files")

        for file in files:
            if file.filename == "":
                return redirect(request.url)

            if file and file.filename.endswith(".pdf") and 'sid' in session:
                file.save(os.path.join(app.config["UPLOAD_PDF_FOLDER"], f"_{session['sid']}",file.filename))

            if file and file.filename.endswith(".msg") and 'sid' in session:
                file.save(os.path.join(app.config["UPLOAD_MSG_FOLDER"], f"_{session['sid']}",file.filename))

        return redirect(url_for("index"))

    return render_template("upload.html")


def receiveSignal(signalNumber, frame):
    print('Received:', signalNumber)
    signal.signal(signal.SIGTERM, receiveSignal)
    signal.signal(signal.SIGINT, receiveSignal)

if __name__ == "__main__":
    app.run()
