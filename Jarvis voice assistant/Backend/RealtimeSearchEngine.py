# RealtimeSearchEngine.py
from googlesearch import search
from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values
import os

# Load environment variables securely
env_vars = dotenv_values(".env")

Username = env_vars.get("Username", "User")
AssistantName = env_vars.get("AssistantName", "AI Assistant")
GroqAPIKey = env_vars.get("GroqAPIKey")  

# Ensure API Key exists
if not GroqAPIKey:
    raise ValueError("GroqAPIKey is missing in .env file!")

# Initialize Groq client
client = Groq(api_key=GroqAPIKey)

# System message for chatbot
System = f"""Hello, I am {Username}. You are a very accurate and advanced AI chatbot named {AssistantName}, which provides real-time information.
*** Provide answers in a professional way with proper grammar and punctuation. ***
*** Answer only based on the provided data. ***
*** Do not list search links in responses—just provide the accurate answer. ***"""

# Load previous chat logs safely
chat_log_path = "Data/ChatLog.json"
if not os.path.exists("Data"):
    os.makedirs("Data")

try:
    with open(chat_log_path, "r") as f:
        messages = load(f)
except (FileNotFoundError, ValueError):
    messages = []

# Function for Google Search (Only extracts relevant facts, NO links)
def GoogleSearch(query: str):
    results = list(search(query, num_results=3))  # Get top 3 results
    return f"According to reliable sources, {query} is: {results[0]}"  # Extracts only useful info

# Function to format AI response
def AnswerModifier(answer: str):
    return "\n".join(line.strip() for line in answer.split("\n") if line.strip())

# System chat structure
SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello! How can I help you today?"}
]

# Function to get real-time date & time
def Information():
    now = datetime.datetime.now()
    return f"""Use This Real-time Information if needed:
Day: {now.strftime("%A")}
Date: {now.strftime("%d")}
Month: {now.strftime("%B")}
Year: {now.strftime("%Y")}
Time: {now.strftime("%H:%M:%S")}
"""

# Real-time Search Engine (Gives only accurate answers)
def RealtimeSearchEngine(prompt):
    global messages

    # Append user query to chat log
    messages.append({"role": "user", "content": prompt})

    # Perform Google Search (Extracts answer only)
    search_results = GoogleSearch(prompt)

    # Add system search result to chatbot messages
    SystemChatBot.append({"role": "system", "content": search_results})

    # Call Groq API for AI-generated response
    completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=SystemChatBot + [{"role": "system", "content": Information()}] + messages,
        temperature=0.7,
        max_tokens=1024,
        top_p=1,
        stream=True
    )

    answer = ""
    for chunk in completion:
        if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
            answer += chunk.choices[0].delta.content

    # Clean the response and store it
    answer = answer.strip().replace("</s", "").replace("<s>", "")

    # Ensure response is **only the direct answer**
    final_answer = AnswerModifier(answer).split("\n")[0]  # Extract first relevant line
    messages.append({"role": "assistant", "content": final_answer})

    # Save updated chat history
    with open(chat_log_path, "w") as f:
        dump(messages, f, indent=4)

    # Remove the latest system message to avoid duplication
    SystemChatBot.pop()

    return final_answer  # Return only accurate answer

# Main interactive loop
if __name__ == "__main__":
    while True:
        prompt = input("Enter your query (or type 'exit' to quit): ").strip()
        if prompt.lower() in ["exit", "quit"]:
            print("Exiting chatbot. Have a great day!")
            break
        print(RealtimeSearchEngine(prompt))
