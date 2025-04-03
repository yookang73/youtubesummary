from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import openai
import re

app = Flask(__name__)

openai.api_key = "YOUR_OPENAI_API_KEY"  # 여기에 실제 OpenAI 키 넣어줘도 되고, Railway에 환경변수로 설정해도 돼

def extract_video_id(url):
    match = re.search(r"v=([a-zA-Z0-9_-]{11})", url)
    return match.group(1) if match else None

def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([line['text'] for line in transcript])
    except (TranscriptsDisabled, NoTranscriptFound):
        return None

def summarize_text(text):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that summarizes YouTube video transcripts."},
            {"role": "user", "content": f"Please summarize this transcript:\n\n{text}"}
        ],
        temperature=0.7,
        max_tokens=500
    )
    return response.choices[0].message['content']

@app.route("/summarize", methods=["POST"])
def summarize():
    data = request.get_json()
    url = data.get("url")
    video_id = extract_video_id(url)

    if not video_id:
        return jsonify({"error": "Invalid YouTube URL"}), 400

    transcript = get_transcript(video_id)
    if not transcript:
        return jsonify({"error": "Transcript not available"}), 404

    summary = summarize_text(transcript)

    return jsonify({
        "title": f"YouTube Video - {video_id}",
        "summary": summary,
        "url": url
    })

if __name__ == "__main__":
    app.run(debug=True)
