import gradio as gr
import base64
import numpy as np
import soundfile as sf
import os
import requests
import json

API_URL = "https://api.runpod.ai/v2/ipr1tauv9hwdj5/runsync"
API_KEY = "RGSAJXYD4L2EXGH4BB3S5OX3E1VAW4J5QSGHB1UB"
API_URL2 = "https://api.runpod.ai/v2/llama2-13b-chat/runsync"
PASSCODE = "aragorn"
def audio_to_base64(audio, passcode):
    # Check if the passcode is correct
    if passcode != PASSCODE:
        return "Speak, friend, and enter. Alas, your passcode is not the key to these gates. Access denied in the land of Mordor."

    sr, data = audio
    # Save audio data to a temporary file
    temp_file = "temp.wav"
    sf.write(temp_file, data, sr, format='wav')
    
    # Read the temporary file as binary and encode it to base64
    with open(temp_file, "rb") as audio_file:
        base64_audio = base64.b64encode(audio_file.read()).decode("utf-8")
    
    # Remove the temporary file
    os.remove(temp_file)
    
    response_text = send_to_api(base64_audio)
    response_json = json.loads(response_text)
    output_text = response_json["output"]["segments"][0]["text"]
    
    # Make the second API call
    second_api_response = second_api_call(output_text)
    
    return second_api_response

def send_to_api(base64_audio):
    payload = {
        "input": {
            "audio_base64": base64_audio,
            "model": "tiny",
            "transcription": "plain text",
            "translate": True,
            "language": "en",
            "temperature": 0,
            "best_of": 5,
            "beam_size": 5,
            "patience": 1,
            "suppress_tokens": "-1",
            "condition_on_previous_text": False,
            "temperature_increment_on_fallback": 0.2,
            "compression_ratio_threshold": 2.4,
            "logprob_threshold": -1,
            "no_speech_threshold": 0.6,
            "word_timestamps": False,
            "initial_prompt": "You are a voice assistant for Bhuvan Portal by ISRO"
        },
        "enable_vad": True
    }
    
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": API_KEY
    }

    response = requests.post(API_URL, json=payload, headers=headers)

    return response.text

def second_api_call(prompt_text):
    
    payload = {
        "input": {
            "prompt": prompt_text,
            "sampling_params": {
                "max_tokens": 2048,
                "n": 1,
                "best_of": None,
                "presence_penalty": 0,
                "frequency_penalty": 0,
                "temperature": 0.5,
                "top_p": 1,
                "top_k": -1,
                "use_beam_search": False,
                "stop": ["USER"],
                "ignore_eos": False,
                "logprobs": None
            }
        }
    }

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": API_KEY
    }

    response = requests.post(API_URL2, json=payload, headers=headers)
    
    response_json = json.loads(response.text)
    output_text = response_json["output"]["text"][0]  # Extract the "text" field
    output_text = output_text.replace("\\n", "\n")  # Replace "\n" with an actual new line
    
    return output_text

def passcode_entry(passcode):
    if passcode == "aragorn":
        return "Passcode correct. You can now use the voice assistant."
    else:
        return "Incorrect passcode. Access denied."

demo = gr.Interface(
    fn=audio_to_base64,
    inputs=["microphone", gr.Textbox(label="Enter Passcode")],
    outputs="text",
    title="Dual Model Inference Test",
    description="Speak into the microphone and see the LLM response. (Faster Whisper tiny + llama13B)",
    theme='WeixuanYuan/Soft_dark'
)

if __name__ == "__main__":
    demo.launch()
