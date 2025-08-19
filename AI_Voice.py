import vosk
import pyaudio
import json
import os
import time
import requests
import pyttsx3
import sys
deepseek_key = "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"
chats = []
if sys.platform == "win32":
    engine = pyttsx3.init(driverName="sapi5")
elif sys.platform == "darwin":
    engine = pyttsx3.init(driverName="nsss")
else:
    engine = pyttsx3.init(driverName="espeak")
model_path = os.path.join(os.getcwd(), "model")
model = vosk.Model(model_path)
SPEECH_TIMEOUT = 8.0 
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000,input=True, frames_per_buffer=8000)
stream.start_stream()
rec = vosk.KaldiRecognizer(model, 16000)
import threading

recording = True

def deepseek_reply(user_message):
    global recording,stream
    recording=False
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {deepseek_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://127.0.0.1",
        "X-Title": "My DeepSeek"
    }
    if len(chats) > 0:
        payload = {
            "model": "deepseek/deepseek-chat-v3-0324:free",
            "messages": [
                {"role":"system","content":"Never use emojis in your answers,always write URLs once, starting with http/https, never inside () or []. Leave a blank line above and below links. You are DeepSeek AI. For titles, don’t use markdown (#, ##, **)."},
                *chats,
                {"role": "user", "content": user_message}
            ]
        }
    else:
        payload = {
            "model": "deepseek/deepseek-chat-v3-0324:free",
            "messages": [
                {"role":"system","content":"Never use emojis in your answers,always write URLs once, starting with http/https, never inside () or []. Leave a blank line above and below links. You are DeepSeek AI. For titles, don’t use markdown (#, ##, **)."},
                {"role": "user", "content": user_message}
            ]
        }
    chats.append({"role": "user", "content": user_message})
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        result = response.json()
        result = result["choices"][0]["message"]["content"]
        chats.append({"role": "assistant", "content": result})
        if len(chats) > 10:
            del chats[:2]
        print("DeepSeek: ", result)
        engine.stop()
        stream.stop_stream()
        stream.close()
        engine.say(result)
        engine.runAndWait()
        
        # listen()
    else:
        print(f'Error : {response.status_code} - {response.reason}')
        engine.stop()
        stream.stop_stream()
        stream.close()
        engine.say(f'Error : {response.status_code} - {response.reason}')
        engine.runAndWait()
    recording=True


def listen():
    global recording,stream
    stream.stop_stream()
    stream.close()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000,input=True, frames_per_buffer=8000)
    stream.start_stream()
    print("Speak ...")
    last_speech_time = time.time()
    question = ""
    while recording:
        data = stream.read(4000, exception_on_overflow=False)
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            text = result.get("text", "")
            if text:
                question += " " + text
                last_speech_time = time.time()
                # print(f"\rYou: {question}")
        else:
            partial = json.loads(rec.PartialResult())
            partial_text = partial.get("partial", "")
            if partial_text:
                print(f"\rYou: {question.strip()} {partial_text}", end="")
        if time.time() - last_speech_time > SPEECH_TIMEOUT and question.strip():
            print(f"\rYou: {question.strip()}")
            # print("the strip")
            # deepseek_reply(utterance.strip())
            # question = ""
            # last_speech_time = time.time()
            return question.strip()
try:
    while True:
        if recording:
            user_input = listen()
            if user_input:
                print("Waiting for assistant reply ...")
                deepseek_reply(user_input)
except KeyboardInterrupt:
    print("\nStopping...")
    stream.stop_stream()
    stream.close()
    p.terminate()
# def deepseek_reply(user_message):
#     url = "https://openrouter.ai/api/v1/chat/completions"
#     headers = {
#         "Authorization": f"Bearer {deepseek_key}",
#         "Content-Type": "application/json",
#         "HTTP-Referer": "http://127.0.0.1",
#         "X-Title": "My DeepSeek"
#     }
#     if len(chats) > 0:
#         payload = {
#             "model": "deepseek/deepseek-chat-v3-0324:free",
#             "messages": [
#                 {"role":"system","content":"Never use emojis in your answers,always write URLs once, starting with http/https, never inside () or []. Leave a blank line above and below links. You are DeepSeek AI by DeepSeek, never OpenAI or ChatGPT. For titles, don’t use markdown (#, ##, **). If content has <a>, convert it to a plain http/https link."},
#                 *chats,
#                 {"role": "user", "content": user_message}
#             ]
#         }
#     else:
#         payload = {
#             "model": "deepseek/deepseek-chat-v3-0324:free",
#             "messages": [
#                 {"role":"system","content":"Never use emojis in your answers,always write URLs once, starting with http/https, never inside () or []. Leave a blank line above and below links. You are DeepSeek AI by DeepSeek, never OpenAI or ChatGPT. For titles, don’t use markdown (#, ##, **). If content has <a>, convert it to a plain http/https link."},
#                 {"role": "user", "content": user_message}
#             ]
#         }
#     chats.append({"role": "user", "content": user_message})
#     response = requests.post(url, headers=headers, json=payload)
#     if response.status_code == 200:
#         result = response.json()
#         result = result["choices"][0]["message"]["content"]
#         chats.append({"role": "assistant", "content": result})
#         if len(chats) > 10:
#             del chats[:2]
#         print("DeepSeek: ", result)
#         engine.say(result)
#         engine.runAndWait()
#         # listen()
#     else:
#         print(f'⚠️ Error : {response.status_code} - {response.reason}')
#         engine.say(f'Error : {response.status_code} - {response.reason}')


# def listen():
#     print("Speak ...")
#     last_speech_time = time.time()
#     question = ""
#     while True:
#         data = stream.read(4000, exception_on_overflow=False)
#         if rec.AcceptWaveform(data):
#             result = json.loads(rec.Result())
#             text = result.get("text", "")
#             if text:
#                 question += " " + text
#                 last_speech_time = time.time()
#                 # print(f"\rYou: {question}")
#         else:
#             partial = json.loads(rec.PartialResult())
#             partial_text = partial.get("partial", "")
#             if partial_text:
#                 print(f"\rYou: {question.strip()} {partial_text}", end="")
#         if time.time() - last_speech_time > SPEECH_TIMEOUT and question.strip():
#             print(f"\rYou: {question.strip()}")
#             # print("the strip")
#             # deepseek_reply(utterance.strip())
#             # question = ""
#             # last_speech_time = time.time()
#             return question.strip()
# try:
#     while True:
#         user_input = listen()
#         print("Waiting for assistant reply ...")
#         stream.stop_stream()
#         stream.close()
#         deepseek_reply(user_input) 
#         stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000,input=True, frames_per_buffer=8000)
#         stream.start_stream()
# except KeyboardInterrupt:
#     print("\nStopping...")
#     stream.stop_stream()
#     stream.close()
#     p.terminate()
# finally:
#     stream.stop_stream()
#     stream.close()
#     p.terminate()

































# import vosk
# import pyaudio
# import json
# import os
# import time
# import requests
# import pyttsx3
# import sys
# deepseek_key = "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"
# chats = []
# if sys.platform == "win32":
#     engine = pyttsx3.init(driverName="sapi5")
# elif sys.platform == "darwin":
#     engine = pyttsx3.init(driverName="nsss")
# else:
#     engine = pyttsx3.init(driverName="espeak")
# model_path = os.path.join(os.getcwd(), "model")
# model = vosk.Model(model_path)
# SPEECH_TIMEOUT = 5.0 
# p = pyaudio.PyAudio()
# stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000,input=True, frames_per_buffer=8000)
# stream.start_stream()
# rec = vosk.KaldiRecognizer(model, 16000)

# def deepseek_reply(user_message):
#     url = "https://openrouter.ai/api/v1/chat/completions"
#     headers = {
#         "Authorization": f"Bearer {deepseek_key}",
#         "Content-Type": "application/json",
#         "HTTP-Referer": "http://127.0.0.1",
#         "X-Title": "My DeepSeek"
#     }
#     if len(chats) > 0:
#         payload = {
#             "model": "deepseek/deepseek-chat-v3-0324:free",
#             "messages": [
#                 {"role":"system","content":"Always write URLs once, starting with http/https, never inside () or []. Leave a blank line above and below links. You are DeepSeek AI by DeepSeek, never OpenAI or ChatGPT. For titles, don’t use markdown (#, ##, **). If content has <a>, convert it to a plain http/https link."},
#                 *chats,
#                 {"role": "user", "content": user_message}
#             ]
#         }
#     else:
#         payload = {
#             "model": "deepseek/deepseek-chat-v3-0324:free",
#             "messages": [
#                 {"role":"system","content":"Always write URLs once, starting with http/https, never inside () or []. Leave a blank line above and below links. You are DeepSeek AI by DeepSeek, never OpenAI or ChatGPT. For titles, don’t use markdown (#, ##, **). If content has <a>, convert it to a plain http/https link."},
#                 {"role": "user", "content": user_message}
#             ]
#         }
#     chats.append({"role": "user", "content": user_message})
#     if len(chats) > 10:
#         del chats[:2]
#     response = requests.post(url, headers=headers, json=payload)
#     if response.status_code == 200:
#         result = response.json()
#         result = result["choices"][0]["message"]["content"]
#         chats.append({"role": "assistant", "content": result})
#         print("DeepSeek:", result)
#         engine.say(result)
#         engine.runAndWait()
#         # listen()
#     else:
#         print(f'⚠️ Error : {response.status_code} - {response.reason}')


# def listen():
#     print("Speak ...")
#     last_speech_time = time.time()
#     utterance = ""
#     while True:
#         data = stream.read(4000, exception_on_overflow=False)
#         if rec.AcceptWaveform(data):
#             result = json.loads(rec.Result())
#             text = result.get("text", "")
#             if text:
#                 utterance += " " + text
#                 last_speech_time = time.time()
#                 print(f"\rYou: {utterance}")
#         else:
#             partial = json.loads(rec.PartialResult())
#             partial_text = partial.get("partial", "")
#             if partial_text:
#                 print(f"\rYou (speaking): {utterance.strip()} {partial_text}", end="")
#         if time.time() - last_speech_time > SPEECH_TIMEOUT and utterance.strip():
#             print("You:", utterance.strip())
#             deepseek_reply(utterance.strip())
#             utterance = ""
#             last_speech_time = time.time()
# try:
#     listen()
# except KeyboardInterrupt:
#     print("\nStopping...")
# finally:
#     stream.stop_stream()
#     stream.close()
#     p.terminate()
