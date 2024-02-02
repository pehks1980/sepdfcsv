import json
import random
import signal
import threading
from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file
import os

import sepdfcsv
import mycache1

import flask_profiler

app = Flask(__name__)

app.debug = False

app.config["UPLOAD_PDF_FOLDER"] = "pdf"
app.config["UPLOAD_MSG_FOLDER"] = "msg"

# You need to declare necessary configuration to initialize
# flask-profiler as follows:
app.config["flask_profiler"] = {
    "enabled": app.config["DEBUG"],
    "storage": {
        "engine": "sqlite"
    },
    "basicAuth": {
        "enabled": False,
        "username": "admin",
        "password": "admin"
    },
    "ignore": [
        "^/static/.*"
    ]
}
flask_profiler.init_app(app)




# import mycache


class ExportingThread(threading.Thread):
    def __init__(self, thread_id):
        self.progress = 0
        self.mode = ''
        self.thread_id = thread_id
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
        sepdfcsv.process_pdfs(self.thread_id)
        # mc = mycache.create_client()
        # for i in range(5,11):
        #    sleep(1)
        #    mycache.update_progress(mc,self.thread_id,i*10)
        # exporting_thread = mc.get(str(self.thread_id))
        # exporting_thread = mc.get(str(self.thread_id))
        # exporting_thread = eval(exporting_thread.decode())
        # if exporting_thread:
        #     exporting_thread['progress'] += 10
        #     mc.set(str(self.thread_id),exporting_thread)
        #     self.progress = exporting_thread['progress']


# index
@app.route("/")
def index():
    return render_template("index.html")


# result list dir
@app.route('/<path>')
def list_result(path):
    if path not in ('result', 'pdf', 'msg'):  # != 'result' and path != 'pdf' and path != 'msg':
        return render_template("index.html")
    initial = os.getcwd()
    os.chdir(initial)
    dir_path = os.path.join(os.getcwd(), path)
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
        if path == 'result':
            return send_file(f"result/{filename}", as_attachment=True)
        if path == 'pdf':
            return send_file(f"pdf/{filename}", as_attachment=True)

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
    thread_id = random.randint(0, 10000)
    exporting_thread = ExportingThread(thread_id)
    exporting_thread.start()

    return jsonify(
        id=thread_id,
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


# run
# @app.route("/run")
# async def run_proc():
#    result = await do_process_pdf()
#    return jsonify(result=result)


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

            if file and file.filename.endswith(".pdf"):
                file.save(os.path.join(app.config["UPLOAD_PDF_FOLDER"], file.filename))

            if file and file.filename.endswith(".msg"):
                file.save(os.path.join(app.config["UPLOAD_MSG_FOLDER"], file.filename))

        return redirect(url_for("index"))

    return render_template("upload.html")


def receiveSignal(signalNumber, frame):
    print('Received:', signalNumber)


signal.signal(signal.SIGTERM, receiveSignal)
signal.signal(signal.SIGINT, receiveSignal)

if __name__ == "__main__":
    app.run()
