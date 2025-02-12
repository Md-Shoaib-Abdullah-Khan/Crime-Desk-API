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
    #if language == 'Bangla':
        #text = "And translate it from english to bangla language."
    
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