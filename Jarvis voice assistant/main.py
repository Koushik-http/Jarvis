from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QThread, pyqtSignal
from Frontend.GUI import GraphicalUserInterface
from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.SpeechToText import SpeechRecognition
from Backend.Chatbot import ChatBot
from Backend.TextToSpeech import TextToSpeech
from dotenv import dotenv_values
import sys
import os
import logging
import json
import subprocess
from subprocess import run
from time import sleep

# Configure logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

# Load environment variables
env_vars = dotenv_values(".env")
Username = env_vars.get("Username", "User")  # Default to "User" if not found
Assistantname = env_vars.get("Assistantname", "Assistant")  # Default to "Assistant" if not found
DefaultMessage = f'''{Username} : Hello {Assistantname}, How are you?
{Assistantname} : Welcome {Username}. I am doing well. How may I help you?'''

# List of supported functions
Functions = ["open", "close", "play", "system", "content", "google search", "youtube search"]

# Define TempDirectoryPath
def TempDirectoryPath(filename):
    """Return the full path for a temporary directory file."""
    temp_dir = os.path.join(os.path.dirname(__file__), 'Temp')
    os.makedirs(temp_dir, exist_ok=True)  # Ensure the Temp directory exists
    return os.path.join(temp_dir, filename)

# Define AnswerModifier
def AnswerModifier(text):
    """Modify the answer text if needed."""
    return text  # Add any necessary modification logic

# Define QueryModifier
def QueryModifier(query):
    """Modify the query if needed."""
    return query  # Add any necessary modification logic

def ShowDefaultChatIfNoChats():
    """Initialize default chat if no chat logs exist."""
    try:
        with open(r'Data\ChatLog.json', "r", encoding='utf-8') as file:
            if len(file.read()) < 5:
                with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as db_file:
                    db_file.write("")
                with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as res_file:
                    res_file.write(DefaultMessage)
    except Exception as e:
        logging.error(f"Error in ShowDefaultChatIfNoChats: {e}")

def ReadChatLogJson():
    """Read and return chat log data from JSON file."""
    try:
        with open(r'Data\ChatLog.json', "r", encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        logging.error(f"Error reading ChatLog.json: {e}")
        return []

def ChatLogIntegration():
    """Integrate chat log data into the GUI."""
    json_data = ReadChatLogJson()
    formatted_chatlog = ""
    for entry in json_data:
        if entry["role"] == "user":
            formatted_chatlog += f"User: {entry['content']}\n"
        elif entry["role"] == "assistant":
            formatted_chatlog += f"Assistant: {entry['content']}\n"
    formatted_chatlog = formatted_chatlog.replace("User", Username + " ")
    formatted_chatlog = formatted_chatlog.replace("Assistant", Assistantname + " ")

    try:
        with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
            file.write(AnswerModifier(formatted_chatlog))
    except Exception as e:
        logging.error(f"Error in ChatLogIntegration: {e}")

def ShowChatsOnGUI(window):
    """Display chat logs on the GUI."""
    try:
        with open(TempDirectoryPath('Database.data'), 'r', encoding='utf-8') as file:
            data = file.read()
            if data:
                with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as res_file:
                    res_file.write(data)
    except Exception as e:
        logging.error(f"Error in ShowChatsOnGUI: {e}")

def ShowTextToScreen(text, window):
    """Display text on the GUI."""
    window.message_screen.chat_section.add_message(text, 'White')  # Use the add_message method

def SetMicrophoneStatus(status, window):
    """Set the microphone status in the GUI."""
    window.initial_screen.mic_icon.setText(f"Microphone: {status}")

def SetAssistantStatus(status, window):
    """Set the assistant status in the GUI."""
    window.initial_screen.status_label.setText(f"Assistant: {status}")

def GetMicrophoneStatus(window):
    """Return the current status of the microphone."""
    mic_text = window.initial_screen.mic_icon.text()
    if ": " in mic_text:
        return mic_text.split(": ")[1]
    return ""  # Return an empty string if the delimiter is not found

def GetAssistantStatus(window):
    """Return the current status of the assistant."""
    status_text = window.initial_screen.status_label.text()
    if ": " in status_text:
        return status_text.split(": ")[1]
    return ""  # Return an empty string if the delimiter is not found

def InitialExecution(window):
    """Initialize the application."""
    SetMicrophoneStatus("False", window)
    ShowTextToScreen("", window)
    ShowDefaultChatIfNoChats()
    ChatLogIntegration()
    ShowChatsOnGUI(window)

def MainExecution(window):
    """Main execution logic for the assistant."""
    try:
        logging.debug("Starting MainExecution...")
        
        TaskExecution = False
        ImageExecution = False
        ImageGenerationQuery = ""

        SetAssistantStatus("Listening...", window)
        Query = SpeechRecognition()
        logging.debug(f"User query: {Query}")
        
        ShowTextToScreen(f"{Username} : {Query}", window)
        SetAssistantStatus("Thinking...", window)
        
        Decision = FirstLayerDMM(Query)  # Pass the query to the decision-making model
        logging.debug(f"Decision: {Decision}")

        G = any([i for i in Decision if i.startswith("general")])
        R = any([i for i in Decision if i.startswith("realtime")])

        Merged_query = " and ".join(
            [" ".join(i.split()[1:]) for i in Decision if i.startswith("general") or i.startswith("realtime")]
        )
        logging.debug(f"Merged query: {Merged_query}")

        for queries in Decision:
            if "generate " in queries:
                ImageGenerationQuery = str(queries)
                ImageExecution = True
                logging.debug(f"Image generation query: {ImageGenerationQuery}")

        for queries in Decision:
            if not TaskExecution:
                if any(queries.startswith(func) for func in Functions):
                    logging.debug(f"Executing automation for query: {queries}")
                    run(Automation(list(Decision)))
                    TaskExecution = True

        if ImageExecution:
            try:
                logging.debug("Starting image generation...")
                with open(r"Frontend\Files\ImageGeneration.data", "w") as file:
                    file.write(f"{ImageGenerationQuery},True")
                p1 = subprocess.Popen(['python', r'Backend\ImageGeneration.py'],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    stdin=subprocess.PIPE, shell=False)
            except Exception as e:
                logging.error(f"Error starting ImageGeneration.py: {e}")

        if (G and R) or R:
            SetAssistantStatus("Searching...", window)
            Answer = RealtimeSearchEngine(QueryModifier(Merged_query))
            logging.debug(f"Realtime search answer: {Answer}")
            
            ShowTextToScreen(f"{Assistantname} : {Answer}", window)
            SetAssistantStatus("Answering...", window)
            TextToSpeech(Answer)
            return True
        else:
            for Queries in Decision:
                if "general" in Queries:
                    SetAssistantStatus("Thinking...", window)
                    QueryFinal = Queries.replace("general ", "")
                    Answer = ChatBot(QueryModifier(QueryFinal))
                    logging.debug(f"ChatBot answer: {Answer}")
                    
                    ShowTextToScreen(f"{Assistantname} : {Answer}", window)
                    SetAssistantStatus("Answering...", window)
                    TextToSpeech(Answer)
                    return True
                elif "realtime" in Queries:
                    SetAssistantStatus("Searching...", window)
                    QueryFinal = Queries.replace("realtime ", "")
                    Answer = RealtimeSearchEngine(QueryModifier(QueryFinal))
                    logging.debug(f"Realtime search answer: {Answer}")
                    
                    ShowTextToScreen(f"{Assistantname} : {Answer}", window)
                    SetAssistantStatus("Answering...", window)
                    TextToSpeech(Answer)
                    return True
                elif "exit" in Queries:
                    QueryFinal = "Okay, Bye!"
                    Answer = ChatBot(QueryModifier(QueryFinal))
                    logging.debug(f"Exit response: {Answer}")
                    
                    ShowTextToScreen(f"{Assistantname} : {Answer}", window)
                    SetAssistantStatus("Answering...", window)
                    TextToSpeech(Answer)
                    os._exit(1)
    except Exception as e:
        logging.error(f"Error in MainExecution: {e}")

class MicrophoneThread(QThread):
    update_signal = pyqtSignal(str, str)  # Signal to update the GUI with text and color

    def __init__(self, window):
        super().__init__()
        self.window = window

    def run(self):
        while True:
            try:
                CurrentStatus = GetMicrophoneStatus(self.window)
                logging.debug(f"Microphone status: {CurrentStatus}")
                
                if CurrentStatus == "True":
                    logging.debug("Microphone is active. Starting MainExecution...")
                    MainExecution(self.window)
                else:
                    AIStatus = GetAssistantStatus(self.window)
                    logging.debug(f"Assistant status: {AIStatus}")
                    
                    if "Available..." in AIStatus:
                        sleep(0.1)  # Add a small delay to prevent CPU overload
                    else:
                        SetAssistantStatus("Available...", self.window)
            except Exception as e:
                logging.error(f"Error in MicrophoneThread: {e}")

if __name__ == "__main__":
    # Start the PyQt5 application
    app = QApplication(sys.argv)
    window = GraphicalUserInterface()  # Use the GraphicalUserInterface class

    # Initialize the application
    InitialExecution(window)

    # Start the microphone thread
    mic_thread = MicrophoneThread(window)
    mic_thread.start()

    window.show()
    sys.exit(app.exec_())