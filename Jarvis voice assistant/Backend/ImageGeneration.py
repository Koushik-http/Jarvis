# ImageGeneration.py
import asyncio
import os
from random import randint
from PIL import Image
import requests
from dotenv import load_dotenv
from time import sleep

# Load environment variables
load_dotenv()
api_key = os.getenv("HuggingFaceAPIKey")

if not api_key:
    print("Error: HuggingFaceAPIKey not found in environment variables!")
    exit(1)

# API URL & Headers
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1"
HEADERS = {"Authorization": f"Bearer {api_key}"}

def open_images(prompt):
    folder_path = "Data"
    prompt = prompt.replace(" ", "_")
    
    files = [os.path.join(folder_path, f"{prompt}{i}.jpg") for i in range(1, 5)]
    existing_files = [f for f in files if os.path.exists(f)]
    
    if not existing_files:
        print("No images found to open.")
        return
    
    for image_path in existing_files:
        try:
            img = Image.open(image_path)
            print(f"Opening image: {image_path}")
            img.show()
            sleep(1)
        except IOError:
            print(f"Unable to open {image_path}")

async def query(payload, retries=3):
    backoff = 5  # Initial delay
    for attempt in range(retries):
        try:
            response = await asyncio.to_thread(requests.post, API_URL, headers=HEADERS, json=payload, timeout=30)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            if hasattr(e, 'response') and e.response is not None and e.response.status_code == 429:
                print(f"Rate limit exceeded. Retrying in {backoff} seconds...")
                await asyncio.sleep(backoff)
                backoff *= 2  # Exponential backoff
            else:
                print(f"API request failed: {e}")
                return None
    print("All retries failed.")
    return None

async def generate_image(prompt: str):
    tasks = []
    os.makedirs("Data", exist_ok=True)  # Ensure folder exists

    for i in range(4):
        payload = {
            "inputs": f"{prompt}, quality=4k, sharpness=maximum, Ultra High details, high resolution",
            "seed": randint(0, 1000000)
        }
        task = asyncio.create_task(query(payload))
        tasks.append(task)
        await asyncio.sleep(5)  # Add a 5-second delay between requests

    image_bytes_list = await asyncio.gather(*tasks)
    
    for i, image_bytes in enumerate(image_bytes_list):
        if image_bytes:
            image_path = os.path.join("Data", f"{prompt.replace(' ', '_')}{i+1}.jpg")
            try:
                with open(image_path, "wb") as f:
                    f.write(image_bytes)
                print(f"Saved image: {image_path}")
            except Exception as e:
                print(f"Error saving image {i+1}: {e}")
        else:
            print(f"Failed to generate image {i+1}")

def GenerateImages(prompt: str):
    asyncio.run(generate_image(prompt))
    open_images(prompt)

def main():
    file_path = r"Frontend\Files\ImageGeneration.data"
    while True:
        try:
            if os.path.getsize(file_path) == 0:
                sleep(1)
                continue

            with open(file_path, "r") as f:
                data = f.read().strip()

            if not data:
                sleep(1)
                continue

            prompt, status = data.split(",")
            
            if status.strip().lower() == "true":
                print("Generating Images ...")
                GenerateImages(prompt=prompt.strip())
                
                with open(file_path, "w") as f:
                    f.write("False,False")
                break  # Exit after processing
            else:
                sleep(1)
        except Exception as e:
            print(f"Error: {e}")
            sleep(1)

if __name__ == "__main__":
    main()
