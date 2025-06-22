from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
import requests
import os
from datetime import datetime
import csv
from io import StringIO, BytesIO
from fpdf import FPDF
import pytz

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

API_KEY = "8783ded381a267cbffecc7a7f73acfd4"

class WeatherRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(100))
    date = db.Column(db.String(20))
    temperature = db.Column(db.Float)
    humidity = db.Column(db.Float)
    pressure = db.Column(db.Float)
    wind_speed = db.Column(db.Float)

@app.route("/", methods=["GET", "POST"])
def index():
    forecast = None
    current = None
    coords = None
    videos = []
    quote = None
    location = None

    try:
        quote_res = requests.get("https://api.quotable.io/random").json()
        quote = {
            "content": quote_res.get("content", ""),
            "author": quote_res.get("author", "")
        }
    except:
        quote = {"content": "Stay curious. Stay humble.", "author": "PM Accelerator"}

    if request.method == "POST":
        location = request.form.get("location")
        latitude = request.form.get("latitude")
        longitude = request.form.get("longitude")

        if latitude and longitude:
            url = f"http://api.openweathermap.org/data/2.5/forecast?lat={latitude}&lon={longitude}&appid={API_KEY}&units=metric"
        elif location:
            url = f"http://api.openweathermap.org/data/2.5/forecast?q={location}&appid={API_KEY}&units=metric"
        else:
            url = None

        if url:
            res = requests.get(url).json()
            if res.get("cod") == "200":
                forecast = res["list"]
                current = forecast[0]
                city_name = res.get("city", {}).get("name")
                current["city_name"] = city_name
                coords = res.get("city", {}).get("coord", {})

                # Convert UTC to US Eastern
                utc_dt = datetime.strptime(current["dt_txt"], "%Y-%m-%d %H:%M:%S")
                utc_dt = pytz.utc.localize(utc_dt)
                eastern = pytz.timezone("US/Eastern")
                local_dt = utc_dt.astimezone(eastern)
                current["dt_txt"] = local_dt.strftime("%Y-%m-%d %H:%M:%S")

                today_date = local_dt.strftime("%Y-%m-%d")
                resolved_location = location if location else f"Lat:{latitude},Lon:{longitude}"
                exists = WeatherRecord.query.filter_by(location=resolved_location, date=today_date).first()
                if not exists:
                    new_record = WeatherRecord(
                        location=resolved_location,
                        date=today_date,
                        temperature=current["main"]["temp"],
                        humidity=current["main"]["humidity"],
                        pressure=current["main"]["pressure"],
                        wind_speed=current["wind"]["speed"]
                    )
                    db.session.add(new_record)
                    db.session.commit()

                videos = [f"https://www.youtube.com/results?search_query=travel+in+{resolved_location}"]
            else:
                forecast = []
                current = None

    filter_location = request.args.get("filter_location")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    query = WeatherRecord.query
    if filter_location:
        query = query.filter(WeatherRecord.location.ilike(f"%{filter_location}%"))
    if start_date and end_date:
        query = query.filter(WeatherRecord.date >= start_date, WeatherRecord.date <= end_date)

    records = query.all()

    return render_template("index.html", forecast=forecast, current=current, coords=coords, videos=videos, records=records, quote=quote)


@app.route("/add", methods=["POST"])
def add():
    new = WeatherRecord(
        location=request.form["location"],
        date=request.form["date"],
        temperature=request.form["temp"],
        humidity=request.form["humidity"],
        pressure=request.form["pressure"],
        wind_speed=request.form["wind_speed"]
    )
    db.session.add(new)
    db.session.commit()
    return redirect(url_for("index"))

@app.route("/export/json")
def export_json():
    filter_location = request.args.get("filter_location")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    query = WeatherRecord.query
    if filter_location:
        query = query.filter(WeatherRecord.location.ilike(f"%{filter_location}%"))
    if start_date and end_date:
        query = query.filter(WeatherRecord.date >= start_date, WeatherRecord.date <= end_date)

    records = query.all()
    data = [{
        "location": r.location,
        "date": r.date,
        "temperature": r.temperature,
        "humidity": r.humidity,
        "pressure": r.pressure,
        "wind_speed": r.wind_speed
    } for r in records]
    return jsonify(data)

@app.route("/export/csv")
def export_csv():
    filter_location = request.args.get("filter_location")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    query = WeatherRecord.query
    if filter_location:
        query = query.filter(WeatherRecord.location.ilike(f"%{filter_location}%"))
    if start_date and end_date:
        query = query.filter(WeatherRecord.date >= start_date, WeatherRecord.date <= end_date)

    records = query.all()
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(["Location", "Date", "Temperature", "Humidity", "Pressure", "Wind Speed"])
    for r in records:
        cw.writerow([r.location, r.date, r.temperature, r.humidity, r.pressure, r.wind_speed])

    output = BytesIO()
    output.write(si.getvalue().encode('utf-8'))
    output.seek(0)
    return send_file(output, mimetype='text/csv', download_name='weather.csv', as_attachment=True)

@app.route("/export/pdf")
def export_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Weather Records", ln=1, align="C")

    filter_location = request.args.get("filter_location")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    query = WeatherRecord.query
    if filter_location:
        query = query.filter(WeatherRecord.location.ilike(f"%{filter_location}%"))
    if start_date and end_date:
        query = query.filter(WeatherRecord.date >= start_date, WeatherRecord.date <= end_date)

    records = query.all()
    for r in records:
        line = f"{r.date} - {r.location}: {r.temperature}°C, {r.humidity}%, {r.pressure} hPa, {r.wind_speed} m/s"
        pdf.cell(200, 10, txt=line, ln=1)

    pdf_path = "/tmp/weather.pdf"
    pdf.output(pdf_path)
    return send_file(pdf_path, as_attachment=True)

@app.route("/update/<int:id>", methods=["POST"])
def update(id):
    record = WeatherRecord.query.get_or_404(id)
    record.temperature = request.form["temperature"]
    record.humidity = request.form["humidity"]
    record.pressure = request.form["pressure"]
    record.wind_speed = request.form["wind_speed"]
    db.session.commit()
    return redirect(url_for("index"))

@app.route("/delete/<int:id>")
def delete(id):
    record = WeatherRecord.query.get_or_404(id)
    db.session.delete(record)
    db.session.commit()
    return redirect(url_for("index"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
