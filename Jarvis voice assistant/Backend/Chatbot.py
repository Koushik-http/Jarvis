from groq import Groq
import openai
from json import load, dump, JSONDecodeError
import datetime
from dotenv import dotenv_values

# Load environment variables
env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
AssistantName = env_vars.get("AssistantName")

GroqAPIKey = "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"
OpenAIAPIKey = "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"

# Initialize Clients
groq_client = Groq(api_key=GroqAPIKey)
openai.api_key = OpenAIAPIKey

# System prompt
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {AssistantName} with real-time information.
*** Reply only in English, even if the question is in Hindi. ***
*** Keep answers short and do not mention your training data. ***
"""

SystemChatBot = [{"role": "system", "content": System}]

# Load chat history safely
chat_log_path = r"Data\ChatLog.json"

def load_chat_log():
    try:
        with open(chat_log_path, "r") as f:
            messages = load(f)
        return messages[-10:]  # Keep only last 10 messages
    except (FileNotFoundError, JSONDecodeError):
        return []

def save_chat_log(messages):
    with open(chat_log_path, "w") as f:
        dump(messages, f, indent=4)

# Generate real-time information
def RealtimeInformation():
    now = datetime.datetime.now()
    return f"Day: {now.strftime('%A')}, Date: {now.strftime('%d %B %Y')}, Time: {now.strftime('%H:%M:%S')}."

# Function to handle chatbot response
def ChatBot(Query, use_groq=True, retry_count=0):
    if retry_count > 2:
        return "Error: Unable to process your request. Try again later."

    messages = load_chat_log()
    messages.append({"role": "user", "content": Query})

    try:
        if use_groq:
            completion = groq_client.chat.completions.create(
                model="llama3-8b-8192",  # ✅ Faster & Lighter Model
                messages=SystemChatBot + [{"role": "system", "content": RealtimeInformation()}] + messages,
                max_tokens=300,  # ✅ Reduce token usage
                temperature=0.5,  # ✅ Make responses concise
                top_p=0.8  
            )
        else:
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=SystemChatBot + [{"role": "system", "content": RealtimeInformation()}] + messages,
                max_tokens=105,
                temperature=0.5,
                top_p=0.8
            )

        # ✅ Correct way to access the response
        Answer = completion.choices[0].message.content.strip()

        # Update chat log
        messages.append({"role": "assistant", "content": Answer})
        save_chat_log(messages)

        return Answer
    except Exception as e:
        print(f"Error: {e}")
        return ChatBot(Query, use_groq, retry_count=retry_count + 1)

# Run chatbot in loop
if __name__ == "__main__":
    use_groq = True  
    while True:
        user_input = input("Enter Your Question: ")
        print(ChatBot(Query=user_input, use_groq=use_groq))
