from langchain_groq import ChatGroq
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")

app = Flask(__name__)

def generate_caption(image_url, language):
    
    text = "Analyze the image and provide a detailed summary of what crime is happening in that image."
    try:
        chat = ChatGroq(api_key=API_KEY, model_name="llama-3.2-11b-vision-preview")

        messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": text
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

    except Exception as e:
        return f"Error: {str(e)}"

def summarize_captions(captions, language):
    
    text = "I will provide you descriptions of multiple images and you have to make a summary of them. Here are the desriptions of images:"
    try:
        chat = ChatGroq(api_key=API_KEY, model_name="llama-3.3-70b-specdec")  

        messages = [
            {
                "role": "user",
                "content": f"{text}\n{'. '.join(captions)}"
            }
        ]

        response = chat.invoke(messages)
        return response.content  

    except Exception as e:
        return f"Error: {str(e)}"

def translate(summary, language):
    
    try:
        chat = ChatGroq(api_key=API_KEY, model_name="gemma2-9b-it") 

        messages = [
            {
                "role": "user",
                "content": f"বাংলায় অনুবাদ করুন :\n\n{summary}"
            }
        ]

        response = chat.invoke(messages)
        return response.content 

    except Exception as e:
        return f"Error: {str(e)}"
    


def analyze_comment_relevance(comment_text: str, crime_post_text: str) -> str:
    chat = ChatGroq(api_key=API_KEY, model_name="deepseek-r1-distill-llama-70b")
    

    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": f"Is the following comment related to the crime post described below? If the comment discredits or calls the post fake, respond with 'Negative'. If the comment supports the post, respond with 'Positive'.\n\nCrime Post: {crime_post_text}\n\nComment: {comment_text}"
                }
            ]
        }
    ]
    

    response = chat.invoke(messages)
    

    if "negative" in response.content.lower():
        relevance = "Negative"
    elif "positive" in response.content.lower():
        relevance = "Positive"
    else:
        relevance = "Uncertain"  

    return relevance

@app.route('/analyze_comment_relevance', methods=['POST'])
def analyze_comment_relevance_api():
    data = request.json
    comment_text = data.get("comment_text")
    crime_post_text = data.get("crime_post_text")
    
    if not comment_text or not crime_post_text:
        return jsonify({"error": "Both comment and crime post text must be provided"}), 400
    
 
    relevance = analyze_comment_relevance(comment_text, crime_post_text)
    
 
    points = 0
    if relevance == "Positive":
        points = 10 
    elif relevance == "Negative":
        points = -5  
    
    return jsonify({
        "comment": comment_text,
        "crime_post": crime_post_text,
        "relevance": relevance,
        "points": points
    })

@app.route('/generate_caption', methods=['POST'])
def generate_caption_api():
    data = request.json
    image_urls = data.get("image_urls")
    language = data.get("language", "English")

    if not image_urls or not isinstance(image_urls, list):
        return jsonify({"error": "Invalid or missing 'image_urls'"}), 400


    captions = [generate_caption(img_url, language) for img_url in image_urls]

 
    summary_caption = summarize_captions(captions, language)
    if language=='Bangla':
        summary_caption = translate(summary_caption, language)
    return jsonify({
 
        "english_summary_caption": summary_caption
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)