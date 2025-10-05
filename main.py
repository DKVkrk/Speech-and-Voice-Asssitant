import pyttsx3
import datetime
import speech_recognition as sr
import wikipedia
import webbrowser as wb
import os
import random
import pyautogui
import pyjokes
import requests
import openai
import pywhatkit
from pytube import YouTube
from youtubesearchpython import VideosSearch

# New imports for PDF summarization
import PyPDF2
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer

# ====== Setup Section ======
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)  # female voice
engine.setProperty('rate', 150)

OPENAI_API_KEY = "your-openai-api-key"
NEWS_API_KEY = "aa5f031bfc0645a8a059486886d2ff1d"
openai.api_key = OPENAI_API_KEY

# ====== Voice and Speak Functions ======
def speak(audio):
    engine.say(audio)
    engine.runAndWait()

# ====== Utility Functions ======
def time():
    current_time = datetime.datetime.now().strftime("%I:%M:%S %p")
    speak("The current time is")
    speak(current_time)
    print("The current time is", current_time)

def date():
    now = datetime.datetime.now()
    speak("The current date is")
    speak(f"{now.day} {now.strftime('%B')} {now.year}")
    print(f"The current date is {now.day}/{now.month}/{now.year}")

def wishme():
    speak("Welcome back!")
    hour = datetime.datetime.now().hour
    if 4 <= hour < 12:
        speak("Good morning!")
    elif 12 <= hour < 16:
        speak("Good afternoon!")
    elif 16 <= hour < 24:
        speak("Good evening!")
    else:
        speak("Good night!")
    assistant_name = load_name()
    speak(f"{assistant_name} at your service. How may I help you today?")

def screenshot():
    img = pyautogui.screenshot()
    img_path = os.path.join(os.getcwd(), "screenshot.png")
    img.save(img_path)
    speak("Screenshot taken and saved.")

def takecommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        try:
            audio = r.listen(source, timeout=5)
        except sr.WaitTimeoutError:
            speak("Timeout. Please try again.")
            return None
    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language="en-in")
        print("User said:", query)
        return query.lower()
    except:
        speak("Sorry, I did not catch that.")
        return None



def set_name():
    speak("What would you like to name me?")
    name = takecommand()
    if name:
        with open("assistant_name.txt", "w") as file:
            file.write(name)
        speak(f"Alright, I will be called {name} from now on.")

def load_name():
    try:
        with open("assistant_name.txt", "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        return "Devesh"

def search_wikipedia(query):
    speak("Searching Wikipedia...")
    try:
        result = wikipedia.summary(query, sentences=2)
        speak(result)
        print(result)
    except:
        speak("Couldn't find anything on Wikipedia.")

def search_youtube(query):
    speak("Searching YouTube...")
    search_url = f"https://www.youtube.com/results?search_query={query}"
    wb.open(search_url)

def search_google(query):
    speak("Searching Google...")
    search_url = f"https://www.google.com/search?q={query}"
    wb.open(search_url)






# Voice-Controlled WhatsApp Messaging
def send_whatsapp_message(query):
    try:
        if "send whatsapp message to" in query:
            speak("What is the phone number with country code?")
            number = takecommand()
            if not number:
                return
            speak("What should I say?")
            message = takecommand()
            if not message:
                return
            pywhatkit.sendwhatmsg_instantly(f"+{number}", message)
            speak("Message sent successfully.")
    except Exception as e:
        speak("Sorry, I couldn't send the message.")
        print("Error:", e)



# ====== Main Program Loop ======
if __name__ == "__main__":
    wishme()
    while True:
        query = takecommand()
        if not query:
            continue

        if "time" in query:
            time()

        elif "date" in query:
            date()

        elif "wikipedia" in query:
            query = query.replace("wikipedia", "").strip()
            search_wikipedia(query)

        elif "play music" in query:
            song_name = query.replace("play music", "").strip()
            play_music(song_name)

        elif "open youtube" in query:
            wb.open("https://www.youtube.com")

        elif "open google" in query:
            wb.open("https://www.google.com")

        elif "search youtube for" in query:
            query = query.replace("search youtube for", "").strip()
            search_youtube(query)

        elif "search google for" in query:
            query = query.replace("search google for", "").strip()
            search_google(query)

        elif "change your name" in query:
            set_name()

        elif "screenshot" in query:
            screenshot()

        elif "tell me a joke" in query:
            joke = pyjokes.get_joke()
            speak(joke)
            print(joke)

        elif "news" in query or "headlines" in query:
            get_news()

        elif "chat" in query or "ai mode" in query:
            speak("AI chat mode activated. Ask me anything.")
            while True:
                ai_query = takecommand()
                if ai_query in ["exit", "stop", "quit"]:
                    speak("Exiting AI mode.")
                    break
                elif ai_query:
                    chat_with_ai(ai_query)

        elif "download video" in query:
            speak("Which video would you like to download?")
            video_query = takecommand()
            if video_query:
                download_youtube_video(video_query)

        elif "send whatsapp message" in query:
            send_whatsapp_message(query)

        elif "summarize pdf" in query or "pdf summary" in query:
            summarize_pdf()

        elif "shutdown" in query:
            speak("Shutting down. Goodbye!")
            os.system("shutdown /s /f /t 1")
            break

        elif "restart" in query:
            speak("Restarting system...")
            os.system("shutdown /r /f /t 1")
            break

        elif "offline" in query or "exit" in query:
            speak("Going offline. Have a good day!")
            break

