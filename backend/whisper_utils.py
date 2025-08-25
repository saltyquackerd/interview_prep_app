# Whisper utilities
import whisper
import tempfile
import os

model = whisper.load_model("small")

def transcribe_audio_file(file):
	with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
		tmp.write(file)
		tmp_path = tmp.name
	result = model.transcribe(tmp_path)
	os.remove(tmp_path)
	return result["text"]
