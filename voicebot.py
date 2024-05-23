import whisper
import numpy as np
from transformers import AutoProcessor, AutoModel
import gradio as gr
from transformers import pipeline

import google.generativeai as genai

target_dtype = np.int16
max_range = np.iinfo(target_dtype).max

key = 'AIzaSyDvOkraZ_VcxdTxhzxR23RcSWrc6SMHo50'

genai.configure(api_key=key)

model = whisper.load_model('large')

model3 = genai.GenerativeModel('gemini-1.5-pro-latest')

# processor = AutoProcessor.from_pretrained("suno/bark")
model2 = pipeline(task="text-to-speech", model="suno/bark")
# synthesised_rate = model2.generation_config.sample_rate

def split_text_into_chunks(text, chunk_size=10):
    words = text.split()
    chunks = [' '.join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
    return chunks


def tts(text):
    return (np.array(model2(
        text
    )['audio'])*32767).astype(np.int16).T

def stt(audio):
    if audio is None:
        return ""

    audio = whisper.load_audio(audio)
    result = model.transcribe(audio,language='en')
    print(result['text'])
    return result["text"]

def processinput(audio):
    text = stt(audio)
    response = model3.generate_content(text)
    print(response.text)
    chunks = split_text_into_chunks(response.text)
    audiochunks = []
    i=0
    for chunk in chunks:
        print('chunk',i, chunk)
        speech = tts(chunk)
        print('chunk',i,speech.shape)
        audiochunks.append(speech)
        i=i+1
    fullaudio = np.concatenate(audiochunks)
    print('fullaudio',fullaudio.shape)
    return 24000, fullaudio
        
demo = gr.Interface(
    processinput,
    gr.Audio(sources=["microphone"], type="filepath"),
    outputs=gr.Audio(label="Generated Speech",autoplay=True)
)

demo.launch()