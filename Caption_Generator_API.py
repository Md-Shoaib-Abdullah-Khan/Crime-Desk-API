import requests
from langchain_groq import ChatGroq
from langchain.schema import SystemMessage, HumanMessage
from flask import Flask, request, jsonify
#from dotenv import load_dotenv
#import os

#load_dotenv()

API_KEY = "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"

app = Flask(__name__)

def generate_caption(image_url):
    chat = ChatGroq(api_key=API_KEY, model_name="llama-3.2-11b-vision-preview")
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Describe what crime is occuring in this image?"
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": image_url
                    }
                }
            ]
        }
    ]
    
    response = chat.invoke(messages)
    return response.content

@app.route('/generate_caption', methods=['POST'])
def generate_caption_api():
    data = request.json
    image_url = data.get("image_url")
    
    if not image_url:
        return jsonify({"error": "No image URL provided"}), 400
    
    caption = generate_caption(image_url)
    return jsonify({"caption": caption})

if __name__ == '__main__':
    app.run()
