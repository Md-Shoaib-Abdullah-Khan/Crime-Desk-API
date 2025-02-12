from langchain_groq import ChatGroq
from flask import Flask, request, jsonify

API_KEY = "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"  # Replace with your actual API key

app = Flask(__name__)

def generate_caption(image_url, language):
    """Generates a caption for a single image."""
    

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
        return response.content  # Extract response safely

    except Exception as e:
        return f"Error: {str(e)}"

def summarize_captions(captions, language):
    #if language == 'Bangla':
        #text = "And translate it from english to bangla language."
    
    text = "I will provide you descriptions of multiple images and you have to make a summary of them. Here are the desriptions of images:"
    try:
        chat = ChatGroq(api_key=API_KEY, model_name="llama-3.3-70b-specdec")  # Use text-only model for summarization

        messages = [
            {
                "role": "user",
                "content": f"{text}\n{'. '.join(captions)}"
            }
        ]

        response = chat.invoke(messages)
        return response.content  # Extract response safely

    except Exception as e:
        return f"Error: {str(e)}"

def translate(summary, language):
    
    try:
        chat = ChatGroq(api_key=API_KEY, model_name="gemma2-9b-it")  # Use text-only model for summarization

        messages = [
            {
                "role": "user",
                "content": f"বাংলায় অনুবাদ করুন :\n\n{summary}"
            }
        ]

        response = chat.invoke(messages)
        return response.content  # Extract response safely

    except Exception as e:
        return f"Error: {str(e)}"
    
def analyze_text(text):
    """Analyzes the crime report text and determines if it is fake."""
    try:
        chat = ChatGroq(api_key=API_KEY, model_name="llama-3.2-11b")

        messages = [
            {
                "role": "user",
                "content": f"Analyze this crime report text and determine if it's misleading, fake, or exaggerated. Provide a confidence score (0-100) and reason:\n\n{text}"
            }
        ]

        response = chat.invoke(messages)
        return response.get("content", "No response from model.")  # Extract response safely

    except Exception as e:
        return f"Error: {str(e)}"

def analyze_image(image_url):
    """Analyzes an image for signs of being fake, AI-generated, or manipulated."""
    try:
        chat = ChatGroq(api_key=API_KEY, model_name="llama-3.2-11b-vision-preview")

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Analyze this image to determine if it is real, AI-generated, or manipulated."},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]
            }
        ]

        response = chat.invoke(messages)
        return response.content  # Extract response safely

    except Exception as e:
        return f"Error: {str(e)}"

def calculate_confidence(text_analysis, image_analysis):
    """Extracts confidence score from AI responses."""
    try:
        chat = ChatGroq(api_key=API_KEY, model_name="llama-3.2-11b")

        messages = [
            {
                "role": "user",
                "content": f"Given the following text and image analyses, assign a confidence score (0-100) indicating how likely this report is fake:\n\nText Analysis: {text_analysis}\n\nImage Analysis: {image_analysis}"
            }
        ]

        response = chat.invoke(messages)
        return response.get("content", "No confidence score returned.")

    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/detect_fake_report', methods=['POST'])
def detect_fake_report():
    data = request.json
    text = data.get("text")
    image_url = data.get("image_url")

    if not text and not image_url:
        return jsonify({"error": "Provide at least text or image for analysis"}), 400

    text_result = analyze_text(text) if text else "No text provided"
    image_result = analyze_image(image_url) if image_url else "No image provided"

    confidence_score = calculate_confidence(text_result, image_result)

    return jsonify({
        "text_analysis": text_result,
        "image_analysis": image_result,
        "confidence_score": confidence_score
    })
import requests
from langchain_groq import ChatGroq
from langchain.schema import SystemMessage, HumanMessage
from flask import Flask, request, jsonify

# Groq API key (make sure to keep this secret)
API_KEY = "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"

app = Flask(__name__)

# Function to analyze whether the comment is related to the crime post using Groq and Llama
def analyze_comment_relevance(comment_text: str, crime_post_text: str) -> str:
    chat = ChatGroq(api_key=API_KEY, model_name="deepseek-r1-distill-llama-70b")
    
    # Create a message prompt to determine the relevance of the comment to the crime post
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
    
    # Send the prompt to Groq's API via LangChain
    response = chat.invoke(messages)
    
    # Extract the response (assuming relevance is determined from the content)
    if "negative" in response.content.lower():
        relevance = "Negative"
    elif "positive" in response.content.lower():
        relevance = "Positive"
    else:
        relevance = "Uncertain"  # In case the response is ambiguous

    return relevance

@app.route('/analyze_comment_relevance', methods=['POST'])
def analyze_comment_relevance_api():
    data = request.json
    comment_text = data.get("comment_text")
    crime_post_text = data.get("crime_post_text")
    
    if not comment_text or not crime_post_text:
        return jsonify({"error": "Both comment and crime post text must be provided"}), 400
    
    # Analyze relevance of the comment to the crime post
    relevance = analyze_comment_relevance(comment_text, crime_post_text)
    
    # Assign points based on relevance (you can adjust the points as needed)
    points = 0
    if relevance == "Positive":
        points = 10  # Award points for relevant comments that support the post
    elif relevance == "Negative":
        points = -5  # Deduct points for comments that discredit or call the post fake
    
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
    language = data.get("language", "English")  # Default to English

    if not image_urls or not isinstance(image_urls, list):
        return jsonify({"error": "Invalid or missing 'image_urls'"}), 400

    # Generate a caption for each image
    captions = [generate_caption(img_url, language) for img_url in image_urls]

    # Generate a summary of all captions
    summary_caption = summarize_captions(captions, language)
    if language=='Bangla':
        summary_caption = translate(summary_caption, language)
    return jsonify({
        #"individual_captions": captions,
        "english_summary_caption": summary_caption

        #"language": language
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)