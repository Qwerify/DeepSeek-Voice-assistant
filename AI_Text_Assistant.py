import requests
import re
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
app=FastAPI()
deepseek_key="your open router deepseek key"
chats=[]
while True:
    user_message=input(">>>")
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {deepseek_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://127.0.0.1",
        "X-Title": "My DeepSeek"   
    }
    if len(chats)>0:
        payload = {
            "model": "deepseek/deepseek-chat",
            "messages": [
                {"role":"system","content":f"Never put a link (url) between brackets () nor []. When you provide a URL to the user, just type it once without repeating it. Always start URLs with http or https, leave a space above and below the link. You are DeepSeek AI, developed by DeepSeek. Never say you are from OpenAI or that you are ChatGPT. When making styled titles, never use markdown headers like # or ##. or **bold** style (e.g., **Title**) for titles, and never use the others even if the user asks for it.If there is any <a> in the contents convert it into a symple http or https link before answering"},
                *chats,
                {"role": "user", "content": user_message}
            ]
        }
    else:
        payload = {
            "model": "deepseek/deepseek-chat",
            "messages": [
                {"role":"system","content":f"Never put a link (url) between brackets () nor []. When you provide a URL to the user, just type it once without repeating it. Always start URLs with http or https, leave a space above and below the link. You are DeepSeek AI, developed by DeepSeek. Never say you are from OpenAI or that you are ChatGPT. When making styled titles, never use markdown headers like # or ##. or **bold** style (e.g., **Title**) for titles, and never use the others even if the user asks for it.If there is any <a> in the contents convert it into a symple http or https link before answering"},
                {"role": "user", "content": user_message}
            ]
        }
    chats.append({"role":"user", "content":user_message})
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code==200:
        result = response.json()
        result=result["choices"][0]["message"]["content"]
        chats.append({"role":"assistant", "content":result})
        print(result)
    elif response.status_code == 429:
        print(f'⚠️ Error : {response.status_code} - {response.reason}')
    else :
        print(f'⚠️ Error : {response.status_code} - {response.reason}')
