from flask import Flask, render_template, jsonify, request
from src.helpers import download_hugging_face_embeddings
from langchain_pinecone import PineconeVectorStore
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from dotenv import load_dotenv
from src.prompts import system_prompt
from src.voice_helpers import transcribe_audio, generate_speech, save_temp_audio, cleanup_temp_file
from src.monitoring import log_query, log_metrics, log_voice_metrics, log_error
import os, base64, time

app = Flask(__name__)
load_dotenv()

if not (os.environ.get('PINECONE_API_KEY') and os.environ.get('OPENAI_API_KEY')):
    raise EnvironmentError("Keys missing")

docsearch = PineconeVectorStore.from_existing_index(
    index_name="medical-chatbot", embedding=download_hugging_face_embeddings()
)
retriever = docsearch.as_retriever(search_type="similarity", search_kwargs={"k": 3})

chain = (
    {"context": retriever | (lambda docs: "\n\n".join(d.page_content for d in docs)), "input": RunnablePassthrough()}
    | ChatPromptTemplate.from_template(system_prompt + "\n\nQuestion: {input}")
    | ChatOpenAI(model="gpt-4o-mini", temperature=0.2, max_tokens=500)
    | StrOutputParser()
)

@app.route("/")
def index(): return render_template("index.html")

@app.route("/stats")
def stats():
    return jsonify({"model": "gpt-4o-mini"})

@app.route("/get", methods=["GET", "POST"])
@log_query
def chat():
    start = time.time()
    msg = request.form.get("msg") or request.args.get("msg")
    if not msg: return jsonify({"error": "No input"}), 400

    try:
        answer = chain.invoke(msg)
        log_metrics("/get", msg, answer, time.time() - start)
        return jsonify({"answer": answer})
    except Exception as e:
        log_error("/get", str(e))
        return jsonify({"error": str(e)}), 500

@app.route("/transcribe", methods=["POST"])
def transcribe():
    if 'file' not in request.files: return jsonify({"error": "No file"}), 400
    temp = save_temp_audio(request.files['file'])
    try: return jsonify({"text": transcribe_audio(temp)})
    except Exception as e: return jsonify({"error": str(e)}), 500
    finally: cleanup_temp_file(temp)

@app.route("/text-to-speech", methods=["POST"])
def text_to_speech():
    if not (text := request.json.get("text")): return jsonify({"error": "No text"}), 400
    try:
        return jsonify({"audio_base64": base64.b64encode(generate_speech(text)).decode('utf-8')})
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route("/voice-query", methods=["POST"])
@log_query
def voice_query():
    start = time.time()
    if 'file' not in request.files: return jsonify({"error": "No file"}), 400
    
    temp = save_temp_audio(request.files['file'])
    try:
        if not (trans := transcribe_audio(temp)): return jsonify({"error": "Transcribe failed"}), 400
        
        answer = chain.invoke(trans)
        
        log_voice_metrics("/voice-query", 0, trans, answer, time.time() - start)
        return jsonify({
            "text": trans, "answer": answer,
            "audio_base64": base64.b64encode(generate_speech(answer)).decode('utf-8')
        })
    except Exception as e:
        log_error("/voice-query", str(e))
        return jsonify({"error": str(e)}), 500
    finally: cleanup_temp_file(temp)

    
if __name__ == '__main__':
    # Development mode
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8080)),
        debug=os.environ.get("DEBUG", "False").lower() == "true"
    )
