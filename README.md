
# 🌤️ Weather App by Jitendra Sai





## 🚀 How to Run This Project

### ✅ Prerequisites

- Python 3.9 or later installed
- An API key from [OpenWeatherMap](https://openweathermap.org/api)

---

### 🧱 Project Setup

1. **Clone or download this repository:**

```bash
git clone https://github.com/jitendrasaiv/weather-app-python.git
cd weather-app-python
```

2. **(Optional) Create a virtual environment:**

```bash
python -m venv venv
source venv/bin/activate       # On Windows: venv\Scripts\activate
```

3. **Install required Python packages:**

```bash
pip install flask flask_sqlalchemy requests fpdf
```

4. **Set your OpenWeatherMap API key in `app.py`:**

Edit this line:

```python
API_KEY = "your_api_key_here"
```

Replace `"your_api_key_here"` with your actual OpenWeatherMap API key.

---

### ▶️ Running the App

Start the Flask server by running:

```bash
python app.py
```

Visit your app at: [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 📁 Project Structure

```
weather-app/
│
├── app.py                # Main Flask app
├── weather.db            # Auto-generated SQLite DB
├── templates/
│   └── index.html        # Jinja2 HTML Template
├── static/               # (Optional) Static files
└── README.md             # This file
```

---

## 📝 Example Use Cases

- **Get Weather**: Enter a city → View current & 5-day forecast
- **Store**: Automatically saves current weather data to DB
- **Manage Records**: Add, update, or delete any weather entry
- **Search & Export**: Filter by date/location → Export to CSV, JSON, or PDF

---

## 👤 About the Author

**Jitendra Sai Vigrahala**  
📍 Tallahassee, FL  
📧 jv23c@fsu.edu  


---

## 📜 License

This project is for educational and demonstration purposes only. Free to use and modify.
