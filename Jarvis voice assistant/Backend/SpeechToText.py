# SpeechToText.py
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
import os
import mtranslate as mt

# Load environment variables
env_vars = dotenv_values(".env")
InputLanguage = env_vars.get("InputLanguage", "en-US")  # Default to English if not found

# HTML File for Speech Recognition
HtmlCode = '''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;

        function startRecognition() {
            recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.lang = '';
            recognition.continuous = true;

            recognition.onresult = function(event) {
                const transcript = event.results[event.results.length - 1][0].transcript;
                output.textContent = transcript;
            };

            recognition.start();
        }

        function stopRecognition() {
            recognition.stop();
        }
    </script>
</body>
</html>'''

# Update HTML to include correct language setting
HtmlCode = HtmlCode.replace("recognition.lang = '';", f"recognition.lang = '{InputLanguage}';")

# Write HTML file
os.makedirs("Data", exist_ok=True)
with open("Data/Voice.html", "w") as f:
    f.write(HtmlCode)

# Get full path of the HTML file
current_dir = os.getcwd()
Link = f"file:///{current_dir}/Data/Voice.html"

# Selenium WebDriver Setup (Run in Headless Mode)
chrome_options = Options()
chrome_options.add_argument("--headless=new")  # Runs without opening a window
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--use-fake-device-for-media-stream")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Function to Modify Query
def QueryModifier(Query):
    return Query.lower().strip().capitalize()

# Function to Translate Speech
def UniversalTranslation(Text):
    return mt.translate(Text, "en", "auto").capitalize()

# Speech Recognition Function (Only Print Recognized Text)
def SpeechRecognition():
    driver.get(Link)
    driver.find_element(By.ID, "start").click()
    
    last_text = ""  # Store previous text
    while True:
        try:
            current_text = driver.find_element(By.ID, "output").text.strip()
            
            if current_text and current_text != last_text:  # Process only if new text is detected
                last_text = current_text
                driver.find_element(By.ID, "end").click()
                
                if "en" in InputLanguage.lower():
                    print(QueryModifier(current_text))  # Directly print without extra messages
                else:
                    print(QueryModifier(UniversalTranslation(current_text)))
                
                break  # Exit loop after recognizing a single input
            
            time.sleep(1.0)  # Reduce CPU usage
        except Exception as e:
            break  # Exit on error

# Main Loop
if __name__ == "__main__":
    while True:
        SpeechRecognition()
