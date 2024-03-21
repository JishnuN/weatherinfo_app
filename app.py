from flask import Flask,render_template,request
import requests
from dotenv import load_dotenv
import os
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime,timedelta


load_dotenv()
API_KEY = os.getenv("API_KEY")
USER_NAME = os.getenv('user')
PASSWORD = os.getenv('pin')
HOST = os.getenv('host')
DB_NAME = os.getenv('db_name')


app = Flask(__name__)


#CONNECTION DB
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{USER_NAME}:{PASSWORD}@{HOST}/{DB_NAME}'

#Initialize the database
db = SQLAlchemy(app)
app.app_context().push()


#Create model
class weather_data(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  data = db.Column(db.JSON)
  latitude = db.Column(db.Float)
  longitude = db.Column(db.Float)
  time_added = db.Column(db.DateTime) 

db.create_all()


@app.route("/")
def home():
  return render_template("layout.html",title = "Weather Info")


@app.route("/weatherinfo")
def weather_info(API_KEY=API_KEY):
  
  lat = request.args.get("latitude")
  lon = request.args.get("longitude")

  try:

    now = datetime.now()
    ten_minutes_ago = now - timedelta(minutes=10)
    data = weather_data.query.filter(weather_data.latitude==lat,weather_data.longitude==lon, weather_data.time_added >= ten_minutes_ago).first()

    if data:
        wdata = data.data
        title = wdata.get('current').get('condition').get('text')
        icon =  wdata.get('current').get('condition').get('icon')
        print('from db')
        return render_template("index.html",data=wdata,title=title,icon=icon)
    
    else:
        response = requests.get(f"https://api.weatherapi.com/v1/current.json?key={API_KEY}&q={lat}/{lon}")

        if response.status_code == 200:
            wdata = response.json()
            new_data = weather_data(data=wdata, latitude=lat, longitude=lon, time_added=now)
            db.session.add(new_data)
            db.session.commit()
            title = wdata.get('current').get('condition').get('text')
            icon =  wdata.get('current').get('condition').get('icon')
            print('from internet')
            return render_template("index.html",data=wdata,title=title,icon=icon)
        
        else:
            msg = response.json()
            error = msg.get('error').get('message') 
            return render_template("error.html",message = error)
        
  except:
    return "error while fetching data"
  

if __name__ == "__main__":
  app.run(debug=True)
