from flask import Flask, render_template, request, send_file
from pathlib import Path
from pysilk import decode_file
import zipfile
import uuid

app = Flask(__name__)

UPLOAD = Path("uploads")
OUTPUT = Path("output")

UPLOAD.mkdir(exist_ok=True)
OUTPUT.mkdir(exist_ok=True)


def is_silk_file(file_path):
    try:
        with open(file_path, "rb") as f:
            header = f.read(10)

        return b"#!SILK_V3" in header

    except Exception:
        return False


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/convert", methods=["POST"])
def convert():

    files = request.files.getlist("file")

    if not files:
        return "没有选择文件", 400

    wav_files = []

    for file in files:

        if file.filename == "":
            continue

        silk_path = UPLOAD / file.filename

        file.save(silk_path)

        if not is_silk_file(silk_path):
            continue

        wav_path = OUTPUT / f"{silk_path.stem}.wav"

        try:

            wav_data = decode_file(
                str(silk_path),
                to_wav=True
            )

            with open(wav_path, "wb") as f:
                f.write(wav_data)

            wav_files.append(wav_path)

        except Exception as e:
            print(f"转换失败: {e}")

    if not wav_files:
        return "没有发现有效的 SILK 文件", 400

    if len(wav_files) == 1:

        return send_file(
            wav_files[0],
            as_attachment=True
        )

    zip_name = f"{uuid.uuid4()}.zip"

    zip_path = OUTPUT / zip_name

    with zipfile.ZipFile(
        zip_path,
        "w",
        zipfile.ZIP_DEFLATED
    ) as zipf:

        for wav_file in wav_files:

            zipf.write(
                wav_file,
                wav_file.name
            )

    return send_file(
        zip_path,
        as_attachment=True
    )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000
    )