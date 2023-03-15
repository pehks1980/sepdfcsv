from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file
import os
import sepdfcsv

app = Flask(__name__)

app.config["UPLOAD_PDF_FOLDER"] = "pdf"
app.config["UPLOAD_MSG_FOLDER"] = "msg"


# index
@app.route("/")
def index():
    return render_template("index.html")


# result list dir
@app.route('/<path>')
def list_result(path):
    if path != 'result' and path != 'pdf' and path != 'msg':
        return render_template("index.html")
    initial = os.getcwd()
    os.chdir(initial)
    dir_path = os.path.join(os.getcwd(), path)
    directory = os.listdir(dir_path)
    ext = ('.csv','.pdf','.msg','.zip')
    files = sorted([file for file in directory if file.endswith(ext)], reverse=True)
    return render_template('list_dir.html', path=path, files=files)


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
async def do_process_pdf():
    # Some asynchronous operation that takes time to complete
    # ...
    sepdfcsv.process_pdfs()
    return "done"


# run
@app.route("/run")
async def run_proc():
    result = await do_process_pdf()
    return jsonify(result=result)


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


if __name__ == "__main__":
    app.run(debug=True)
