import os
import boto3
from flask import Flask, request, render_template

app = Flask(__name__)

# Configuration from environment
S3_IMAGE_URL  = os.environ.get('BG_IMAGE_URL')
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

def get_presigned_url():
    """
    Generate a presigned URL for the S3 object if BG_IMAGE_URL is in s3:// format.
    Returns the presigned URL (valid for 1 hour) if successful, else returns S3_IMAGE_URL unchanged.
    """
    if not S3_IMAGE_URL or not S3_IMAGE_URL.startswith("s3://"):
        # Either no URL provided or it is already a normal URL.
        return S3_IMAGE_URL
    try:
        # Parse the bucket name and object key from the S3 URL
        parts = S3_IMAGE_URL.replace("s3://", "").split("/", 1)
        bucket_name = parts[0]
        object_key = parts[1] if len(parts) > 1 else ""
        s3_client = boto3.client('s3')
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': object_key},
            ExpiresIn=3600  # URL valid for 1 hour
        )
        print(f"Generated presigned URL: {presigned_url}")
        return presigned_url
    except Exception as e:
        print(f"ERROR generating presigned URL: {e}")
        return S3_IMAGE_URL

# ----------------
# ROUTE 1: Home (about.html)
# ----------------
@app.route("/")
def home():
    # Generate a presigned URL for the background image
    bg_url = get_presigned_url()
    # Display the 'about.html' template, passing the presigned URL along with other variables.
    return render_template("about.html",
                           project_name=MY_NAME,
                           project_slogan=PROJECT_NAME,
                           name=MY_NAME,
                           bg_image_url=bg_url)

# ----------------
# ROUTE 2: Add Employee (GET -> Show the form)
# ----------------
@app.route("/addemp", methods=["GET"])
def addemp_form():
    return render_template("addemp.html", color="#EDEDED")

# ----------------
# ROUTE 2b: Add Employee (POST -> Process the form and show output)
# ----------------
@app.route("/addemp", methods=["POST"])
def addemp_submit():
    emp_id = request.form.get("emp_id")
    fname = request.form.get("first_name")
    lname = request.form.get("last_name")
    skill = request.form.get("primary_skill")
    loc = request.form.get("location")
    return render_template("addempoutput.html",
                           project_name=MY_NAME,
                           project_slogan=PROJECT_NAME,
                           name=f"{fname} {lname}",
                           color="#EDEDED")

# ----------------
# ROUTE 3: Get Employee (GET -> Show the form)
# ----------------
@app.route("/getemp", methods=["GET"])
def getemp_form():
    return render_template("getemp.html", color="#EDEDED")

# ----------------
# ROUTE 3b: Fetch Employee Data (POST -> Query DB, show output)
# ----------------
@app.route("/fetchdata", methods=["POST"])
def fetchdata():
    emp_id = request.form.get("emp_id")
    # Simulate a query result
    fname = "Eni"
    lname = "Zeqo"
    skill = "Python"
    loc = "Toronto"
    return render_template("getempoutput.html",
                           color="#EDEDED",
                           id=emp_id,
                           fname=fname,
                           lname=lname,
                           interest=skill,
                           location=loc)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=81, debug=True)
