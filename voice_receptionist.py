"""
BMSH Voice Receptionist — Upgraded
------------------------------------
Supports: Book | Cancel | Reschedule
Collects: name, department, date, time
Sends to : Flask API at http://127.0.0.1:5000
"""

import sounddevice as sd
from scipy.io.wavfile import write
import whisper
import re
import os
import requests
from datetime import datetime, timedelta

from gtts import gTTS
from playsound import playsound

# ── CONFIG ────────────────────────────────────────────────────
BASE_URL    = "http://127.0.0.1:5000"
SAMPLE_RATE = 16000
DURATION    = 5       # seconds to record per turn
model       = whisper.load_model("base")

# ── DOCTORS MAP (matches DB seed) ─────────────────────────────
DOCTORS = {
    "dermatology":   "Dr. Alluri Ramakrishnan Raju",
    "dermatologist": "Dr. Alluri Ramakrishnan Raju",
    "gynecology":    "Dr. Sita Devi",
    "gynecologist":  "Dr. Sita Devi",
    "cardiology":    "Dr. Krishna Murthy",
    "cardiologist":  "Dr. Krishna Murthy",
    "neurology":     "Dr. Priya Sharma",
    "neurologist":   "Dr. Priya Sharma",
    "orthopedics":   "Dr. Kiran Reddy",
    "orthopedist":   "Dr. Kiran Reddy",
    "pediatrics":    "Dr. Lakshmi Devi",
    "pediatrician":  "Dr. Lakshmi Devi",
    "emergency":     "Dr. Suresh Babu",
    "ent":           "Dr. Prakash Rao",
    "ophthalmology": "Dr. Ravi Shankar",
    "psychiatry":    "Dr. Vijaya Lakshmi",
    "oncology":      "Dr. Sunita Reddy",
    "pulmonology":   "Dr. Ramesh Babu",
    "endocrinology": "Dr. Meena Kumari",
}

# ── SPEAK ─────────────────────────────────────────────────────
def speak(text):
    print(f"\n🤖 AI: {text}")
    try:
        tts = gTTS(text=text, lang='en')
        tts.save("voice.mp3")
        playsound("voice.mp3")
        os.remove("voice.mp3")
    except Exception as e:
        print(f"  [Speech error: {e}]")

# ── RECORD ────────────────────────────────────────────────────
def record_audio():
    print("\n🎤 Listening... (speak now)")
    audio = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1)
    sd.wait()
    write("audio.wav", SAMPLE_RATE, audio)
    return "audio.wav"

# ── TRANSCRIBE ────────────────────────────────────────────────
def transcribe():
    file   = record_audio()
    result = model.transcribe(file, language="en")
    text   = result["text"].strip()
    print(f"👤 You: {text}")
    return text, text.lower()

# ── EXTRACT NAME ──────────────────────────────────────────────
def extract_name(text):
    patterns = [
        r"my name is ([A-Za-z]+(?:\s[A-Za-z]+)?)",
        r"i am ([A-Za-z]+(?:\s[A-Za-z]+)?)",
        r"this is ([A-Za-z]+(?:\s[A-Za-z]+)?)",
        r"name[:\s]+([A-Za-z]+(?:\s[A-Za-z]+)?)",
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            return m.group(1).strip().title()
    return None

# ── EXTRACT DATE ──────────────────────────────────────────────
def extract_date(text):
    today = datetime.today()

    # relative days
    if "today"     in text: return today.strftime("%Y-%m-%d")
    if "tomorrow"  in text: return (today + timedelta(days=1)).strftime("%Y-%m-%d")
    if "day after" in text: return (today + timedelta(days=2)).strftime("%Y-%m-%d")

    # weekdays
    days = ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]
    for i, day in enumerate(days):
        if day in text:
            diff = (i - today.weekday()) % 7
            if diff == 0: diff = 7
            return (today + timedelta(days=diff)).strftime("%Y-%m-%d")

    # numeric: "25th", "march 25", "25 march"
    months = {"january":1,"february":2,"march":3,"april":4,"may":5,"june":6,
              "july":7,"august":8,"september":9,"october":10,"november":11,"december":12}

    for month_name, month_num in months.items():
        if month_name in text:
            m = re.search(r'(\d{1,2})', text)
            if m:
                day_num = int(m.group(1))
                year    = today.year if month_num >= today.month else today.year + 1
                try:
                    return datetime(year, month_num, day_num).strftime("%Y-%m-%d")
                except:
                    pass

    # fallback: bare number like "25th" or "on the 15"
    m = re.search(r'\b(\d{1,2})\b', text)
    if m:
        day_num = int(m.group(1))
        candidate = today.replace(day=day_num) if day_num >= today.day else \
                    (today.replace(month=today.month+1, day=day_num) if today.month < 12
                     else today.replace(year=today.year+1, month=1, day=day_num))
        try:
            return candidate.strftime("%Y-%m-%d")
        except:
            pass

    return None

# ── EXTRACT TIME ──────────────────────────────────────────────
def extract_time(text):
    # "10:30 AM", "ten thirty", "3 pm" etc.
    m = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)', text, re.IGNORECASE)
    if m:
        hour   = int(m.group(1))
        minute = int(m.group(2)) if m.group(2) else 0
        meridiem = m.group(3).upper()
        return f"{hour:02d}:{minute:02d} {meridiem}"

    # word numbers
    word_hours = {"one":1,"two":2,"three":3,"four":4,"five":5,"six":6,
                  "seven":7,"eight":8,"nine":9,"ten":10,"eleven":11,"twelve":12}
    for word, num in word_hours.items():
        if word in text:
            meridiem = "PM" if ("afternoon" in text or "pm" in text or num < 8) else "AM"
            return f"{num:02d}:00 {meridiem}"
    return None

# ── EXTRACT DEPARTMENT ────────────────────────────────────────
def extract_department(text):
    for dept in DOCTORS:
        if dept in text:
            return dept, DOCTORS[dept]
    return None, None

# ── API CALLS ─────────────────────────────────────────────────
def api_book(name, doctor, department, date, time):
    try:
        r = requests.post(f"{BASE_URL}/api/voice/book", json={
            "name": name, "doctor": doctor,
            "department": department, "date": date, "time": time
        }, timeout=5)
        return r.json()
    except Exception as e:
        print(f"  [API error: {e}]")
        return {"success": False, "message": "Could not reach server."}

def api_cancel(name, date=None):
    try:
        r = requests.post(f"{BASE_URL}/api/voice/cancel", json={"name": name, "date": date or ""}, timeout=5)
        return r.json()
    except Exception as e:
        print(f"  [API error: {e}]")
        return {"success": False, "message": "Could not reach server."}

def api_reschedule(name, new_date, new_time):
    try:
        r = requests.post(f"{BASE_URL}/api/voice/reschedule", json={
            "name": name, "new_date": new_date, "new_time": new_time
        }, timeout=5)
        return r.json()
    except Exception as e:
        print(f"  [API error: {e}]")
        return {"success": False, "message": "Could not reach server."}

# ─────────────────────────────────────────────────────────────
#  BOOKING FLOW
# ─────────────────────────────────────────────────────────────
def flow_book():
    appt = {"name": None, "department": None, "doctor": None, "date": None, "time": None}

    speak("Sure! Let's book an appointment. Which department do you need? "
          "For example: Cardiology, Dermatology, Neurology, Pediatrics...")

    # Department
    for _ in range(3):
        _, text = transcribe()
        dept, doctor = extract_department(text)
        if dept:
            appt["department"] = dept
            appt["doctor"]     = doctor
            speak(f"Great! You selected {dept.title()}. The doctor available is {doctor}.")
            break
        speak("Sorry, I didn't catch the department. Please say the department name again.")
    else:
        speak("I couldn't identify the department. Let's start over.")
        return

    # Name
    speak("May I know your full name please?")
    for _ in range(3):
        spoken, text = transcribe()
        name = extract_name(text) or (spoken.strip().title() if len(spoken.split()) <= 3 else None)
        if name:
            appt["name"] = name
            speak(f"Thank you, {name}.")
            break
        speak("Could you please repeat your name?")
    else:
        speak("I couldn't get your name. Let's start over.")
        return

    # Date
    speak("What date would you like? You can say 'tomorrow', a weekday like 'Monday', or a date like 'March 25th'.")
    for _ in range(3):
        _, text = transcribe()
        date = extract_date(text)
        if date:
            appt["date"] = date
            readable = datetime.strptime(date, "%Y-%m-%d").strftime("%A, %B %d")
            speak(f"Got it — {readable}.")
            break
        speak("Sorry, I didn't catch the date. Please say it again.")
    else:
        speak("I couldn't get the date. Let's start over.")
        return

    # Time
    speak("What time works for you? For example: 10 AM, 2:30 PM, 4 in the afternoon.")
    for _ in range(3):
        spoken, text = transcribe()
        time = extract_time(text)
        if time:
            appt["time"] = time
            speak(f"Perfect — {time}.")
            break
        speak("Sorry, I didn't catch the time. Please say it again.")
    else:
        speak("I couldn't get the time. Let's start over.")
        return

    # Confirm
    speak(f"Let me confirm: Appointment with {appt['doctor']} in {appt['department'].title()}, "
          f"on {datetime.strptime(appt['date'],'%Y-%m-%d').strftime('%A %B %d')} at {appt['time']}. "
          f"Shall I go ahead and book this? Say yes or no.")

    _, text = transcribe()
    if "yes" in text or "confirm" in text or "sure" in text or "okay" in text:
        result = api_book(appt["name"], appt["doctor"], appt["department"], appt["date"], appt["time"])
        if result.get("success"):
            speak(f"Your appointment is confirmed! {appt['name']}, your appointment with {appt['doctor']} "
                  f"is booked on {datetime.strptime(appt['date'],'%Y-%m-%d').strftime('%B %d')} at {appt['time']}. "
                  f"Please arrive 15 minutes early. Thank you!")
        else:
            speak(f"Sorry, I couldn't book the appointment. {result.get('message','')}")
    else:
        speak("No problem, appointment not booked. Is there anything else I can help you with?")


# ─────────────────────────────────────────────────────────────
#  CANCEL FLOW
# ─────────────────────────────────────────────────────────────
def flow_cancel():
    speak("I'll help you cancel an appointment. May I know your name?")

    name = None
    for _ in range(3):
        spoken, text = transcribe()
        name = extract_name(text) or spoken.strip().title()
        if name:
            speak(f"Looking up appointment for {name}.")
            break

    if not name:
        speak("I couldn't get your name. Please try again.")
        return

    result = api_cancel(name)
    if result.get("success"):
        speak(result.get("message", "Your appointment has been cancelled."))
    else:
        speak(f"Sorry, {result.get('message','I could not find your appointment.')}")


# ─────────────────────────────────────────────────────────────
#  RESCHEDULE FLOW
# ─────────────────────────────────────────────────────────────
def flow_reschedule():
    speak("I'll help you reschedule. May I know your name?")

    name = None
    for _ in range(3):
        spoken, text = transcribe()
        name = extract_name(text) or spoken.strip().title()
        if name:
            break

    if not name:
        speak("I couldn't get your name. Please try again.")
        return

    speak(f"Thank you {name}. What is the new date you'd like?")
    new_date = None
    for _ in range(3):
        _, text = transcribe()
        new_date = extract_date(text)
        if new_date:
            readable = datetime.strptime(new_date, "%Y-%m-%d").strftime("%A, %B %d")
            speak(f"New date: {readable}.")
            break
        speak("Sorry, please say the date again.")

    if not new_date:
        speak("Couldn't get the new date. Please try again.")
        return

    speak("And what time would you like?")
    new_time = None
    for _ in range(3):
        _, text = transcribe()
        new_time = extract_time(text)
        if new_time:
            speak(f"New time: {new_time}.")
            break
        speak("Sorry, please say the time again.")

    if not new_time:
        speak("Couldn't get the new time. Please try again.")
        return

    result = api_reschedule(name, new_date, new_time)
    if result.get("success"):
        speak(result.get("message", "Your appointment has been rescheduled."))
    else:
        speak(f"Sorry, {result.get('message','Could not reschedule.')}")


# ─────────────────────────────────────────────────────────────
#  MAIN LOOP
# ─────────────────────────────────────────────────────────────
def main():
    speak("Welcome to Bhimavaram Multi-Speciality Hospital. "
          "I can help you book, cancel, or reschedule an appointment. How may I assist you?")

    while True:
        input("\n📞 Press Enter to speak (or Ctrl+C to exit)...")

        spoken, text = transcribe()

        if not spoken:
            speak("I didn't catch that. Please try again.")
            continue

        # Exit
        if any(w in text for w in ["bye", "goodbye", "exit", "quit", "thank you that's all"]):
            speak("Thank you for contacting Bhimavaram Multi-Speciality Hospital. Stay healthy, take care!")
            break

        # Greeting
        if any(w in text for w in ["hello", "hi ", "hey", "good morning", "good afternoon"]):
            speak("Hello! How can I help you today? I can book, cancel, or reschedule an appointment.")
            continue

        # Intent detection
        is_cancel      = any(w in text for w in ["cancel", "cancellation", "remove appointment"])
        is_reschedule  = any(w in text for w in ["reschedule", "change appointment", "move appointment", "shift appointment"])
        is_book        = any(w in text for w in ["book", "appointment", "schedule", "see a doctor", "consult"])

        if is_cancel:
            flow_cancel()
        elif is_reschedule:
            flow_reschedule()
        elif is_book:
            flow_book()
        else:
            speak("I can help you book, cancel, or reschedule an appointment. Which would you like?")


if __name__ == '__main__':
    main()