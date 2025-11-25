from openai import OpenAI
import os, uuid

_client = None
def get_client():
    global _client
    if not _client: _client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
    return _client

def transcribe_audio(file_path):
    with open(file_path, "rb") as f:
        return get_client().audio.transcriptions.create(model="whisper-1", file=f).text

def generate_speech(text):
    return get_client().audio.speech.create(model="tts-1", voice="alloy", input=text[:4096]).content

def save_temp_audio(file_obj):
    path = os.path.join("/tmp" if os.path.exists("/tmp") else "temp", f"{uuid.uuid4()}.webm")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    file_obj.save(path)
    return path

def cleanup_temp_file(path):
    if os.path.exists(path): os.remove(path)
