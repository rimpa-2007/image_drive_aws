import os
import boto3
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)

# AWS S3 Configuration
BUCKET_NAME = "rimpa-image-drive-2026"
REGION_NAME = "ap-southeast-2"

# Initializing boto3 client
s3 = boto3.client("s3", region_name=REGION_NAME)


@app.route("/")
def index():
  images = []
  try:
    response = s3.list_objects_v2(Bucket=BUCKET_NAME)
    if "Contents" in response:
      for obj in response["Contents"]:
        file_key = obj["Key"]
        image_url = (
            f"https://{BUCKET_NAME}.s3.{REGION_NAME}.amazonaws.com/{file_key}"
        )
        images.append({"name": file_key, "url": image_url})
  except Exception as e:
    print(f"Error fetching images: {e}")

  return render_template("index.html", images=images)


@app.route("/upload", methods=["POST"])
def upload_file():
  if "image" not in request.files:
    return redirect(url_for("index"))

  file = request.files["image"]
  if file.filename != "":
    try:
      # S3-te upload kora ebong content-type auto-detect kora
      s3.upload_fileobj(
          file,
          BUCKET_NAME,
          file.filename,
          ExtraArgs={"ContentType": file.content_type},
      )
    except Exception as e:
      print(f"Upload failed: {e}")

  return redirect(url_for("index"))


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000, debug=True)