import os
import re
import boto3
from flask import Flask, render_template, request, send_file
from io import BytesIO

app = Flask(__name__)

# Configuration from environment
S3_IMAGE_URL  = os.environ.get('BG_IMAGE_URL')  # Expecting format: s3://eni-bucket-background/background2.png
MY_NAME       = os.environ.get('MY_NAME') or "Eni Zeqo"
PROJECT_NAME  = os.environ.get('PROJECT_NAME') or "My Project"
DB_USER       = os.environ.get('DB_USER')
DB_PASSWORD   = os.environ.get('DB_PASSWORD')
DB_HOST       = os.environ.get('DB_HOST', 'localhost')
DB_NAME       = os.environ.get('DB_NAME', 'mydatabase')

# Log the background image URL for debugging
if S3_IMAGE_URL:
    print(f"Background image URL from config: {S3_IMAGE_URL}")
else:
    print("No BG_IMAGE_URL provided; using default background.")

# Parse the bucket name from S3_IMAGE_URL
S3_BUCKET = ""
if S3_IMAGE_URL:
    match = re.match(r"s3://([^/]+)/(.+)", S3_IMAGE_URL)
    if match:
        S3_BUCKET = match.group(1)

def get_background_image():
    """
    Download the background image from S3 into a local static folder and return the object key.
    This function mimics your friend's approach.
    """
    if S3_IMAGE_URL:
        match = re.match(r"s3://([^/]+)/(.+)", S3_IMAGE_URL)
        if match:
            bucket = match.group(1)
            key = match.group(2)
            local_path = "static/background.png"
            os.makedirs("static", exist_ok=True)
            try:
                s3_client = boto3.client('s3', region_name="us-east-1")
                s3_client.download_file(bucket, key, local_path)
                print(f"[+] Downloaded {key} from {bucket} to {local_path}")
            except Exception as e:
                print(f"[!] Error downloading from S3: {e}")
            return key
        else:
            print("[!] Invalid S3_IMAGE_URL format.")
            return ""
    else:
        print("No BG_IMAGE_URL provided.")
        return ""

@app.route('/proxy-image/<path:key>')
def proxy_image(key):
    """
    Proxy endpoint to fetch the image from S3 and serve it to the browser.
    """
    s3_client = boto3.client('s3', region_name="us-east-1")
    file_obj = BytesIO()
    try:
        s3_client.download_fileobj(S3_BUCKET, key, file_obj)
        file_obj.seek(0)
        # Adjust mimetype if needed, here assumed as image/png
        return send_file(file_obj, mimetype='image/png')
    except Exception as e:
        return f"Error: {e}", 500

@app.route("/")
def home():
    background_key = get_background_image()
    return render_template("about.html",
                           project_name=MY_NAME,
                           project_slogan=PROJECT_NAME,
                           name=MY_NAME,
                           BACKGROUND_IMAGE=background_key)

@app.route("/addemp", methods=["GET"])
def addemp_form():
    background_key = get_background_image()
    return render_template("addemp.html", color="#EDEDED", BACKGROUND_IMAGE=background_key)

@app.route("/addemp", methods=["POST"])
def addemp_submit():
    emp_id = request.form.get("emp_id")
    fname = request.form.get("first_name")
    lname = request.form.get("last_name")
    skill = request.form.get("primary_skill")
    loc = request.form.get("location")
    background_key = get_background_image()
    return render_template("addempoutput.html",
                           project_name=MY_NAME,
                           project_slogan=PROJECT_NAME,
                           name=f"{fname} {lname}",
                           color="#EDEDED",
                           BACKGROUND_IMAGE=background_key)

@app.route("/getemp", methods=["GET"])
def getemp_form():
    background_key = get_background_image()
    return render_template("getemp.html", color="#EDEDED", BACKGROUND_IMAGE=background_key)

@app.route("/fetchdata", methods=["POST"])
def fetchdata():
    emp_id = request.form.get("emp_id")
    fname = "Eni"
    lname = "Zeqo"
    skill = "Python"
    loc = "Toronto"
    background_key = get_background_image()
    return render_template("getempoutput.html",
                           color="#EDEDED",
                           id=emp_id,
                           fname=fname,
                           lname=lname,
                           interest=skill,
                           location=loc,
                           BACKGROUND_IMAGE=background_key)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=81, debug=True)
