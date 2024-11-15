from flask import Flask, request, jsonify, session, render_template
import numpy as np
#import google.generativeai as genai
from azure.cognitiveservices.speech import SpeechConfig, SpeechSynthesizer
import azure.cognitiveservices.speech as speechsdk
from azure.cognitiveservices.speech.audio import AudioOutputConfig
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS  # Import CORS
import os
from groq import Groq               
import time 
from coversational_rag import ConversationalRAG 
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
CORS(app)  # Allow only specific origin 
app.secret_key = os.urandom(24)  # Securely set the secret key for Flask sessions

# Initialize ConversationalRAG once
pdf_directory = "documentation/"
pdf_paths = [os.path.join(pdf_directory, f) for f in os.listdir(pdf_directory) if (f.endswith('.csv') or f.endswith('.pdf'))]
conversational_rag = ConversationalRAG(file_paths=pdf_paths, api_key=os.environ.get("GROQ_API_KEY"))

@app.before_request
def initialize_user_session():
    if "session_id" not in session:
        session["session_id"] = generate_unique_session_id()  # Generate a unique ID for each user

@app.route('/ask', methods=['POST'])
def ask():
    user_question = request.json.get("question", "")
    user_session_id = session["session_id"]
    
    # Use the single instance of ConversationalRAG with each user's session_id
    answer = conversational_rag.qa_with_memory(user_question, user_session_id)
    
    return {"answer": answer}

def generate_unique_session_id():
    # This can be any unique generator; for simplicity, you could use UUIDs
    import uuid
    return str(uuid.uuid4())
       

@app.route('/llm', methods=['POST'])
def qa_with_memory():
    data = request.get_json()  # Parse the incoming JSON data
    text = data.get('text')  # Get the 'text' field from the JSON
    
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    if text:
        # Use Flask session for session ID
        session_id = session.get("session_id", None)
        if not session_id:
            session_id = os.urandom(8).hex()  # Generate unique session ID if not set
            session["session_id"] = session_id

        # Call the qa_with_memory method and get the answer
        answer = conversational_rag.qa_with_memory(text, session_id)[0]
        response_data = {
        'text': f'{answer}'  # Example response
        }
    return jsonify(response_data), 200  # Return a JSON respons    

# Function for interacting with LLM
""" def gemini_llm(audio_string):
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(audio_string)
    return response.text if response else ""  # Handle empty responses gracefully
 """
def groq_llm(text):
    client = Groq(
        # This is the default and can be omitted
        api_key=os.environ.get("GROQ_API_KEY"),
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a weeb who loves hentai and can give any manga sauce when asked. You should not include any asteriks or any special characters."
            },
            {
                "role": "user",
                "content": text,
            }
        ],
        model="llama-3.1-8b-instant",
    )

    return chat_completion.choices[0].message.content

# Azure TTS function
def azure_tts(text):    
    speech_config = SpeechConfig(subscription=os.environ.get("AZURE_API_KEY"), region=os.environ.get("AZURE_REGION"))
    audio_config = AudioOutputConfig(filename="output.wav")
    speech_config.speech_synthesis_voice_name = 'en-US-AndrewMultilingualNeural'
    
    synthesizer = SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
    result = synthesizer.speak_text_async(text).get()

    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("Speech synthesized successfully.")
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print(f"Speech synthesis canceled: {cancellation_details.reason}")
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print(f"Error details: {cancellation_details.error_details}")

@app.route('/stt', methods=['POST'])
def stt():
    try:    
        client = Groq(api_key = os.environ.get('GROQ_API_KEY'))

        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400

        audio_file = request.files['audio']
        filename = "temp_audio.wav"
        audio_file.save(filename)

        with open(filename, "rb") as file:
            transcription = client.audio.transcriptions.create(
                file=(filename, file.read()),
                model="whisper-large-v3",
                prompt="Specify context or spelling",  
                response_format="json",  
                language="en",  
                temperature=0.0  
            )
        os.remove(filename)  
        # Return transcription text in a JSON format
        return jsonify({'text': transcription.text})
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return jsonify({'error': f"An error occurred: {str(e)}"}), 500       


@app.route('/sts', methods=['POST'])
def sts():
    try:    
        client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400

        audio_file = request.files['audio']
        filename = "temp_audio.wav"
        audio_file.save(filename)
        with open(filename, "rb") as file:
            transcription = client.audio.transcriptions.create(
                file=(filename, file.read()),
                model="whisper-large-v3",
                prompt="Specify context or spelling",  
                response_format="json",  
                language="en",  
                temperature=0.0  
            )
        os.remove(filename)  # Clean up 
        # llm response   
        llm_response =  groq_llm(transcription.text)
        # text to speech implementation
        if os.path.exists("output.wav"):
            os.remove("output.wav")  # Remove the previous output file if exists
        azure_tts(llm_response)  # Call your TTS function to generate 'output.wav'
        audio_path = 'output.wav'  # Path to the synthesized WAV file
        try:
            return send_file(audio_path, mimetype='audio/wav')  # Serve the WAV file
        except Exception as e:
            return jsonify({"error": str(e)}), 500  # Return error response
        finally:
            os.remove("output.wav")

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return jsonify({'error': f"An error occurred: {str(e)}"}), 500 
""" 
# API endpoint for LLM
@app.route('/ai', methods=['POST'])
def generate_llm_response():
    data = request.get_json()  # Parse the incoming JSON data
    text = data.get('text')  # Get the 'text' field from the JSON
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    if text:
        llm_response = gemini_llm(text)
        response_data = {
        'text': f'{llm_response}'  # Example response
        }
    return jsonify(response_data), 200  # Return a JSON respons          
 """
# API endpoint for TTS
@app.route('/tts', methods=['POST'])
def tts():
    data = request.get_json()  # Get JSON data from the request
    text = data.get('text')  # Retrieve 'text' from JSON payload
    
    if text:
        if os.path.exists("output.wav"):
            os.remove("output.wav")  # Remove the previous output file if exists
        
        azure_tts(text)  # Call your TTS function to generate 'output.wav'
        audio_path = 'output.wav'  # Path to the synthesized WAV file

        try:
            return send_file(audio_path, mimetype='audio/wav')  # Serve the WAV file
        except Exception as e:
            return jsonify({"error": str(e)}), 500  # Return error response
    else:
        return jsonify({"error": "No text provided"}), 400  # Handle missing text
    
@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':     
    app.run(host='0.0.0.0', port=5000, debug=False)
