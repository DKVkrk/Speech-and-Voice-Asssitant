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

def play_music(song_name=None):
    song_dir = os.path.expanduser("~/Music")
    songs = os.listdir(song_dir)
    if song_name:
        songs = [song for song in songs if song_name.lower() in song.lower()]
    if songs:
        song = random.choice(songs)
        os.startfile(os.path.join(song_dir, song))
        speak(f"Playing {song}")
    else:
        speak("No matching song found.")

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

def get_news():
    url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={NEWS_API_KEY}"
    try:
        response = requests.get(url)
        news_data = response.json()
        if news_data["status"] == "ok":
            articles = news_data["articles"][:5]
            speak("Here are the top 5 latest news headlines:")
            for i, article in enumerate(articles, 1):
                speak(article["title"])
                print(f"{i}. {article['title']}")
        else:
            speak("Couldn't fetch the news.")
    except Exception as e:
        speak("Error occurred while fetching news.")
        print(e)

def chat_with_ai(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", 
            messages=[{"role": "user", "content": prompt}]
        )
        reply = response['choices'][0]['message']['content']
        speak(reply)
        print("AI:", reply)
    except Exception as e:
        speak("Sorry, I couldn't process that.")
        print(e)

def download_youtube_video(query):
    speak(f"Searching YouTube for {query}")
    search = VideosSearch(query, limit=1)
    result = search.result()["result"]
    if result:
        video_url = result[0]["link"]
        video_title = result[0]["title"]
        speak(f"Found: {video_title}. Downloading now.")
        try:
            yt = YouTube(video_url)
            stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
            stream.download(output_path=".", filename="downloaded_video.mp4")
            speak("Download completed. Saved as downloaded_video.mp4")
        except Exception as e:
            speak("Download failed.")
            print("Error:", e)
    else:
        speak("Couldn't find any video.")

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

# ====== PDF Summarization Function ======
def summarize_pdf():
    speak("Please tell me the full file path of the PDF you want to summarize.")
    pdf_path = takecommand()
    if not pdf_path:
        speak("I did not get the file path. Please try again later.")
        return

    # Fix common speech recognition path issues (e.g., spaces)
    pdf_path = pdf_path.replace(" slash ", "/").replace(" backslash ", "\\").replace(" ", "")
    print(f"User provided PDF path: {pdf_path}")

    if not os.path.exists(pdf_path):
        speak("Sorry, I could not find the file. Please check the path and try again.")
        return

    try:
        with open(pdf_path, "rb") as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            # Read first 5 pages or less
            for page_num in range(min(5, len(pdf_reader.pages))):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + " "
            if not text.strip():
                speak("Sorry, I could not extract text from the PDF.")
                return

            # Use sumy for summarization
            parser = PlaintextParser.from_string(text, Tokenizer("english"))
            summarizer = LsaSummarizer()
            summary = summarizer(parser.document, 5)  # 5 sentences summary

            speak("Here is the summary of the PDF:")
            for sentence in summary:
                print(sentence)
                speak(str(sentence))

    except Exception as e:
        speak("Sorry, an error occurred while summarizing the PDF.")
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
