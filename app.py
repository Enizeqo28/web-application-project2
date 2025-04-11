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

def download_background_image():
    """Download the background image from S3 to local storage (if URL is provided)."""
    if not S3_IMAGE_URL:
        return  # No URL, nothing to do
    try:
        url = S3_IMAGE_URL
        bucket_name = url.replace("s3://", "").split("/")[0]
        object_key = "/".join(url.replace("s3://", "").split("/")[1:])
        
        local_path = "static/background.png"
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        
        s3 = boto3.resource('s3')
        s3.Bucket(bucket_name).download_file(object_key, local_path)
        print(f"Downloaded background image from S3: s3://{bucket_name}/{object_key} -> {local_path}")
    except Exception as e:
        print(f"ERROR downloading S3 image: {e}")

# ----------------
# ROUTE 1: Home (about.html)
# ----------------
@app.route("/")
def home():
    # Display the 'about.html' template
    return render_template("about.html",
                           project_name=MY_NAME,
                           project_slogan=PROJECT_NAME,
                           name=MY_NAME)

# ----------------
# ROUTE 2: Add Employee (GET -> Show the form)
# ----------------
@app.route("/addemp", methods=["GET"])
def addemp_form():
    # 'addemp.html' uses a <form> to POST data to /addemp
    # Pass a background color or any variable the template needs
    return render_template("addemp.html", color="#EDEDED")

# ----------------
# ROUTE 2b: Add Employee (POST -> Process the form and show output)
# ----------------
@app.route("/addemp", methods=["POST"])
def addemp_submit():
    # Collect form data
    emp_id = request.form.get("emp_id")
    fname = request.form.get("first_name")
    lname = request.form.get("last_name")
    skill = request.form.get("primary_skill")
    loc = request.form.get("location")

    # Optionally, insert into DB here if needed
    # e.g. cursor.execute("INSERT INTO employees ...", (emp_id, fname, lname, skill, loc))
    # connection.commit()

    # Display the addempoutput.html page
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

    # Here you would query the DB for this employee ID
    # Example: 
    # cursor.execute("SELECT first_name, last_name, primary_skill, location FROM employees WHERE emp_id = %s", (emp_id,))
    # row = cursor.fetchone()  # (fname, lname, skill, location)
    # For now, let's simulate:
    fname = "John"
    lname = "Doe"
    skill = "Python"
    loc = "USA"

    return render_template("getempoutput.html",
                           color="#EDEDED",
                           id=emp_id,
                           fname=fname,
                           lname=lname,
                           interest=skill,
                           location=loc)

if __name__ == "__main__":
    # Download the background image at startup
    download_background_image()
    # Listen on port 81 as required
    app.run(host="0.0.0.0", port=81, debug=True)
