# backend.py

import logging

# Import all backend modules
from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.SpeechToText import SpeechRecognition
from Backend.Chatbot import ChatBot
from Backend.TextToSpeech import TextToSpeech


# Define a function to initialize and run all backend components
def initialize_backend():
    """Initialize all backend components."""
    logging.info("Initializing backend components...")
    
    # Initialize SpeechRecognition
    speech_recognizer = SpeechRecognition()
    logging.info("SpeechRecognition initialized.")
    
    # Initialize ChatBot
    chatbot = ChatBot()
    logging.info("ChatBot initialized.")
    
    # Initialize TextToSpeech
    text_to_speech = TextToSpeech()
    logging.info("TextToSpeech initialized.")
    
    # Initialize RealtimeSearchEngine
    search_engine = RealtimeSearchEngine()
    logging.info("RealtimeSearchEngine initialized.")
    
    # Initialize Automation
    automation = Automation()
    logging.info("Automation initialized.")
    
    # Initialize ImageGeneration (if applicable)

    
    logging.info("All backend components initialized successfully.")
    return {
        "speech_recognizer": speech_recognizer,
        "chatbot": chatbot,
        "text_to_speech": text_to_speech,
        "search_engine": search_engine,
        "automation": automation,

    }

def run_backend():
    """Run all backend components."""
    logging.info("Running backend components...")
    
    # Example: Run SpeechRecognition and process the query
    query = SpeechRecognition.listen()
    logging.info(f"User query: {query}")
    
    # Process the query using the decision-making model
    decision = FirstLayerDMM(query)
    logging.info(f"Decision: {decision}")
    
    # Execute actions based on the decision
    if "general" in decision:
        response = ChatBot.generate_response(decision)
        TextToSpeech.speak(response)
    elif "realtime" in decision:
        response = RealtimeSearchEngine.search(decision)
        TextToSpeech.speak(response)
    elif "automation" in decision:
        Automation.execute(decision)
    
    
    logging.info("Backend execution completed.")

if __name__ == "__main__":
    # Initialize and run the backend
    backend_components = initialize_backend()
    run_backend()