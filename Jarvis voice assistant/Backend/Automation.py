# Automation.py
from AppOpener import close, open as appopen
from webbrowser import open as webopen
from pywhatkit import search, playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import webbrowser
import subprocess
import requests
import keyboard
import asyncio
import os
import logging
from typing import List, Generator, AsyncGenerator

# Load environment variables
env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# List of CSS classes for web scraping
class_list = [
    "zCubwf", "hgKElc", "LTKOO sY7ric", "Z0Lcw", "gsrt vk_bk FzvWSb YwPhnf", "pclqee",
    "tw-Data-text tw-text-small tw-ta", "IZ6rdc", "O5uR6d LTKOO", "vlzY6d",
    "webanswers-webanswers_table__webanswers_table", "dDoNo ikb4Bb gsrt",
    "sXLaOe", "LWkfKe", "VQF4g", "qv3Wpe", "kno-rdesc", "SPZz6b"
]

# User agent for web requests
useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"

# Initialize Groq client
client = Groq(api_key=GroqAPIKey)

# System chatbot configuration
SystemChatBot = [
    {"role": "system", "content": f"Hello, I am {os.environ.get('Username', 'User')}, You are a very accurate and advanced AI chatbot named {os.environ.get('AssistantName', 'Assistant')} which also has real-time up-to-date information from the internet."}
]

# Professional responses
professional_responses = [
    "Your satisfaction is my top priority; feel free to reach out if there's anything else I can help you with.",
    "I'm here to help you with any questions or concerns you may have.",
]

# Message history
messages = []


# Function to perform a Google search
def GoogleSearch(topic: str) -> bool:
    try:
        search(topic)
        return True
    except Exception as e:
        logging.error(f"Google search failed: {e}")
        return False


# Function to generate content using AI
def ContentWriterAI(prompt: str) -> str:
    messages.append({"role": "user", "content": prompt})

    completion = client.chat.completions.create(
        model="mixtral-8x7b-32768",
        messages=SystemChatBot + messages,
        max_tokens=2048,
        temperature=0.7,
        top_p=1,
        stream=True,
        stop=None
    )

    answer = ""
    for chunk in completion:
        if chunk.choices[0].delta.content:
            answer += chunk.choices[0].delta.content

    answer = answer.replace("</s>", "")
    messages.append({"role": "assistant", "content": answer})
    return answer


# Function to create and open content in Notepad
def Content(topic: str) -> bool:
    try:
        topic = topic.replace("Content ", "")
        content_by_ai = ContentWriterAI(topic)

        file_path = rf"Data\{topic.lower().replace(' ', '_')}.txt"
        os.makedirs("Data", exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content_by_ai)

        subprocess.Popen(["notepad.exe", file_path])
        return True
    except Exception as e:
        logging.error(f"Content creation failed: {e}")
        return False


# Function to search on YouTube
def YoutubeSearch(topic: str) -> bool:
    try:
        url = f"https://www.youtube.com/results?search_query={topic}"
        webopen(url)
        return True
    except Exception as e:
        logging.error(f"YouTube search failed: {e}")
        return False


# Function to play a video on YouTube
def PlayYoutube(query: str) -> bool:
    try:
        playonyt(query)
        return True
    except Exception as e:
        logging.error(f"Playing YouTube video failed: {e}")
        return False


# Function to open an application or search for it online
def OpenApp(app: str, sess=requests.Session()) -> bool:
    try:
        appopen(app, match_closest=True, output=True, throw_error=True)
        return True
    except Exception as e:
        logging.warning(f"App not found locally, searching online: {e}")

        def extract_links(html: str) -> List[str]:
            soup = BeautifulSoup(html, "html.parser")
            links = soup.find_all("a", {'jsname': 'UWckNb'})
            return [link.get('href') for link in links]

        def search_google(query: str) -> str:
            url = f"https://www.google.com/search?q={query}"
            headers = {'User-Agent': useragent}
            response = sess.get(url, headers=headers)
            return response.text if response.status_code == 200 else None

        html = search_google(app)
        if html:
            links = extract_links(html)
            if links:
                webopen(links[0])
                return True

        logging.error(f"Failed to find app online: {app}")
        return False


# Function to close an application
def CloseApp(app: str) -> bool:
    try:
        if "chrome" in app.lower():
            os.system("taskkill /f /im chrome.exe")
        else:
            close(app, match_closest=True, output=True, throw_error=True)
        return True
    except Exception as e:
        logging.error(f"Failed to close app: {e}")
        return False


# Function to handle system commands
def System(command: str) -> bool:
    try:
        if command == "mute":
            keyboard.press_and_release("volume mute")
        elif command == "unmute":
            keyboard.press_and_release("volume mute")
        elif command == "volume up":
            keyboard.press_and_release("volume up")
        elif command == "volume down":
            keyboard.press_and_release("volume down")
        else:
            logging.warning(f"Unknown system command: {command}")
            return False
        return True
    except Exception as e:
        logging.error(f"System command failed: {e}")
        return False


# Function to translate and execute commands asynchronously
async def TranslateAndExecute(commands: List[str]) -> AsyncGenerator[str, None]:
    func = []
    for command in commands:
        if command.startswith("open "):
            app_name = command.removeprefix("open ")
            if app_name != "file":
                func.append(asyncio.to_thread(OpenApp, app_name))
        elif command.startswith("close "):
            app_name = command.removeprefix("close ")
            func.append(asyncio.to_thread(CloseApp, app_name))
        elif command.startswith("play "):
            query = command.removeprefix("play ")
            func.append(asyncio.to_thread(PlayYoutube, query))
        elif command.startswith("content "):
            topic = command.removeprefix("content ")
            func.append(asyncio.to_thread(Content, topic))
        elif command.startswith("google search "):
            query = command.removeprefix("google search ")
            func.append(asyncio.to_thread(GoogleSearch, query))
        elif command.startswith("youtube search "):
            query = command.removeprefix("youtube search ")
            func.append(asyncio.to_thread(YoutubeSearch, query))
        elif command.startswith("system "):
            cmd = command.removeprefix("system ")
            func.append(asyncio.to_thread(System, cmd))
        else:
            logging.warning(f"No function found for command: {command}")

    results = await asyncio.gather(*func)
    for result in results:
        yield result


# Function to automate command execution
async def Automation(commands: List[str]) -> bool:
    async for result in TranslateAndExecute(commands):
        logging.info(result)
    return True


