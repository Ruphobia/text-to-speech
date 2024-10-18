#!/usr/bin/python3.11
import requests

# --- Server Configuration ---
API_URL = "http://localhost:8888/synthesize"

def send_text_to_api(text):
    try:
        # Make a POST request to the API with the text
        response = requests.post(API_URL, data={'text': text})

        # Check if the request was successful
        if response.status_code == 200:
            print(f"Request successful: '{text}' played by the server.")
        else:
            print(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    print("Enter text to synthesize (type 'exit' to quit):")

    while True:
        text = input("> ")

        # Exit condition
        if text.lower() == 'exit':
            print("Exiting...")
            break

        # Send the text to the API for speech synthesis
        send_text_to_api(text)

if __name__ == "__main__":
    main()
