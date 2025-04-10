from flask import Flask, render_template, request, url_for
from pymysql import connections
import os
import boto3
import argparse
import random

app = Flask(__name__)

# ---------------------------
# Configuration via Environment Variables
# ---------------------------

PROJECT_NAME = os.getenv('PROJECT_NAME', "Eni's Cloud Edge")
PROJECT_SLOGAN = os.getenv('PROJECT_SLOGAN', "Fast, Smart, Reliable")
IMAGE_URL = os.getenv('IMAGE_URL')  # expected: "s3://bucket-name/path/to/image"

# ---------------------------
# Download Background Image from S3
# ---------------------------

if IMAGE_URL:
    if IMAGE_URL.startswith("s3://"):
        _, bucket, key = IMAGE_URL.split("/", 2)
    else:
        parts = IMAGE_URL.split("/", 1)
        bucket, key = parts[0], parts[1] if len(parts) > 1 else ""
    s3 = boto3.client('s3')
    local_file = key.split("/")[-1] or "background.png"
    local_path = os.path.join("static", local_file)
    try:
        s3.download_file(bucket, key, local_path)
        print(f"Downloaded S3 image {bucket}/{key} to {local_path}")
    except Exception as e:
        print(f"ERROR: could not download image from S3 - {e}")

# ---------------------------
# Database Configuration using Secrets/ConfigMap
# ---------------------------

DBHOST = os.getenv("DB_HOST", "localhost")
DBUSER = os.getenv("DB_USER", "root")
DBPWD  = os.getenv("DB_PASSWORD", "")
DATABASE = os.getenv("DB_NAME", "employees")
DBPORT = int(os.getenv("DB_PORT", 3306))

db_conn = connections.Connection(
    host=DBHOST,
    port=DBPORT,
    user=DBUSER,
    password=DBPWD,
    db=DATABASE
)

# ---------------------------
# Color Support for Templates
# ---------------------------

color_codes = {
    "red": "#e74c3c",
    "green": "#16a085",
    "blue": "#89CFF0",
    "blue2": "#30336b",
    "pink": "#f4c2c2",
    "darkblue": "#130f40",
    "lime": "#C1FF9C",
}
SUPPORTED_COLORS = ",".join(color_codes.keys())
# Pick a random color if not set by command-line or environment variable
COLOR = random.choice(list(color_codes.keys()))

# ---------------------------
# Routes
# ---------------------------

@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('addemp.html',
                           color=color_codes[COLOR],
                           project_name=PROJECT_NAME,
                           project_slogan=PROJECT_SLOGAN)

@app.route("/about", methods=['GET','POST'])
def about():
    return render_template('about.html',
                           color=color_codes[COLOR],
                           project_name=PROJECT_NAME,
                           project_slogan=PROJECT_SLOGAN)
    
@app.route("/addemp", methods=['POST'])
def add_emp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    primary_skill = request.form['primary_skill']
    location = request.form['location']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()
    try:
        cursor.execute(insert_sql, (emp_id, first_name, last_name, primary_skill, location))
        db_conn.commit()
        emp_name = f"{first_name} {last_name}"
    finally:
        cursor.close()

    print("Employee addition completed...")
    return render_template('addempoutput.html',
                           name=emp_name,
                           color=color_codes[COLOR],
                           project_name=PROJECT_NAME,
                           project_slogan=PROJECT_SLOGAN)

@app.route("/getemp", methods=['GET', 'POST'])
def get_emp():
    return render_template("getemp.html",
                           color=color_codes[COLOR],
                           project_name=PROJECT_NAME,
                           project_slogan=PROJECT_SLOGAN)

@app.route("/fetchdata", methods=['GET','POST'])
def fetch_data():
    emp_id = request.form['emp_id']
    output = {}
    select_sql = "SELECT emp_id, first_name, last_name, primary_skill, location FROM employee WHERE emp_id=%s"
    cursor = db_conn.cursor()
    try:
        cursor.execute(select_sql, (emp_id,))
        result = cursor.fetchone()
        if result:
            output = {
                "emp_id": result[0],
                "first_name": result[1],
                "last_name": result[2],
                "primary_skills": result[3],
                "location": result[4]
            }
    except Exception as e:
        print(e)
    finally:
        cursor.close()

    return render_template("getempoutput.html",
                           id=output.get("emp_id", "N/A"),
                           fname=output.get("first_name", "N/A"),
                           lname=output.get("last_name", "N/A"),
                           interest=output.get("primary_skills", "N/A"),
                           location=output.get("location", "N/A"),
                           color=color_codes[COLOR],
                           project_name=PROJECT_NAME,
                           project_slogan=PROJECT_SLOGAN)

# ---------------------------
# Main – Parse Command Line Args for Color Override and Run on Port 81
# ---------------------------

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--color', required=False)
    args = parser.parse_args()

    if args.color:
        print("Color from command line argument: " + args.color)
        COLOR = args.color
        if os.getenv('APP_COLOR'):
            print("A color was set through the environment variable APP_COLOR, but command-line takes precedence.")
    elif os.getenv('APP_COLOR'):
        COLOR = os.getenv('APP_COLOR')
        print("Color from environment variable: " + COLOR)
    else:
        print("No command line argument or environment variable provided. Using random color: " + COLOR)
    
    if COLOR not in color_codes:
        print("Color not supported. Received '" + COLOR + "'. Supported colors are " + SUPPORTED_COLORS)
        exit(1)
    
    # Run Flask app on port 81 so Kubernetes/Docker can route correctly
    app.run(host='0.0.0.0', port=81, debug=True)
