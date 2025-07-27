# 🆘 AI-Powered Emergency Response Assistant

A real-time emergency detection and alert system that captures voice commands, identifies the type of emergency using simple NLP, locates the user with GPS, and sends an alert email to emergency contacts.

---

## 🚀 Features

- 🎤 **Voice Recognition**: Speak your emergency using your device's mic.
- 🧠 **AI-based Classification**: Detects the type of emergency (fire, medical, accident, etc.).
- 📍 **Live Location Tracking**: Uses browser geolocation API.
- 📧 **Instant Alerts**: Sends emergency emails to a contact with message + location.

---

## 🛠 Tech Stack

| Frontend  | Backend   | AI/NLP | Alerts     |
|-----------|-----------|--------|------------|
| HTML/CSS/JS | Python Flask | Rule-based NLP | Gmail SMTP |

---

## 📦 Folder Structure

Emergency-Assistant/
│
├── backend/
│ ├── app.py # Main Flask server
│ ├── classifier.py # Classifies emergency messages
│ ├── email_alert.py # Sends email alerts
│ └── requirements.txt # Flask dependency
│
└── templates/
└── index.html # Frontend voice UI

