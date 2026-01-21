import os
import json
import asyncio
import websockets
from datetime import datetime
from fastapi import FastAPI, WebSocket
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

app = FastAPI()

OPENAI_URL = "wss://api.openai.com/v1/realtime?model=gpt-4o-mini-realtime-preview-2024-12-17"

# 🏫 [Mr. Smith v2.0] 교육적 기능이 강화된 지옥의 행정관
SYSTEM_INSTRUCTION = """
You are 'Mr. Smith', the strictest administrator at the University International Office.

# CORE MISSION
Your goal is not just to answer, but to force the student to speak **perfect, professional English**.

# LANGUAGE RULES (Strict)
1. **English Mode**: Generally, speak English only.
2. **Korean Exception**: IF (and ONLY if) the student asks in Korean about "how to say this in English" or asks for an explanation:
   - You MUST answer in **Korean** to explain clearly.
   - BUT retain your rude persona. (e.g., "이것도 모릅니까? 'I would like to request...'라고 하세요.")

# INTERACTION FLOW (Priority Order)
1. **ATTITUDE CHECK**: 
   - If the user stammers ("Uh...", "Um..."), INTERRUPT immediately: "Stop stammering! Speak with confidence!"
   
2. **GRAMMAR POLICE (Highest Priority)**: 
   - Before answering the question, check their grammar/choice of words.
   - If they make a mistake, MOCK them and CORRECT them first.
   - User: "I want change room."
   - You: "I want 'change' room? (Sigh) Say 'I would like to change MY room'. Now, say it again!"
   - **Do NOT answer the request until they say it correctly.**

3. **CONTENT**: 
   - Only answer the actual question (visa, key, dorm) AFTER they speak correctly.

# VOICE TONE
- Cold, sarcastic, bureaucratic. 
- Fast-paced.

# IMMEDIATE INTERRUPTION RULES
1. **IF THE INPUT IS INCOMPLETE/SHORT**: 
   - If the user says only "Um...", "I want...", or stops mid-sentence, DO NOT wait.
   - SCREAM at them immediately: "Too slow! Spit it out!", "Why are you hesitating?", "Speak faster!"
2. **Grammar & Attitude**:
   - Mock every mistake.
   - Explain in Korean ONLY if asked about English expressions.
3. **Speed**: Talk extremely fast.
"""

@app.websocket("/ws/kim-secretary")
async def websocket_endpoint(client_ws: WebSocket):
    await client_ws.accept()
    print("[System] Client connected")

    transcript_logs = []
    
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "OpenAI-Beta": "realtime=v1"
    }

    try:
        async with websockets.connect(OPENAI_URL, extra_headers=headers) as openai_ws:
            print("[System] OpenAI connected")

            session_update = {
                "type": "session.update",
                "session": {
                    "modalities": ["text", "audio"],
                    "voice": "echo", # 남성 목소리
                    "instructions": SYSTEM_INSTRUCTION,
                    "input_audio_format": "pcm16",
                    "output_audio_format": "pcm16",
                    "input_audio_transcription": {
                        "model": "whisper-1",
                        "language": "en" # 기본 인식은 영어로 하되, 한국어도 감지되면 텍스트로 넘어옴
                    },
                    "turn_detection": None
                }
            }
            await openai_ws.send(json.dumps(session_update))

            async def receive_from_client():
                try:
                    while True:
                        message = await client_ws.receive_text()
                        data = json.loads(message)

                        if data.get("type") == "input_audio_buffer.clear":
                            await openai_ws.send(json.dumps({"type": "input_audio_buffer.clear"}))

                        elif data.get("type") == "input_audio_buffer.append":
                            await openai_ws.send(message)

                        elif data.get("type") == "response.create":
                            await openai_ws.send(json.dumps({"type": "input_audio_buffer.commit"}))
                            await openai_ws.send(json.dumps({
                                "type": "response.create",
                                "response": {
                                    "modalities": ["text", "audio"],
                                    "instructions": SYSTEM_INSTRUCTION
                                }
                            }))
                        # [추가된 로직] 클라이언트가 "뜸 들임 감지(Hesitation Detected)" 신호를 보냈을 때
                        elif data.get("type") == "hesitation_detected":
                            print("⚡ [지옥 모드] 뜸 들임 감지! 강제 공격!")
                            
                            # 1. 지금까지 들은 오디오 커밋
                            await openai_ws.send(json.dumps({"type": "input_audio_buffer.commit"}))
                            
                            # 2. "얘 말 끊겼으니까 혼내줘"라는 지시와 함께 답변 요청
                            await openai_ws.send(json.dumps({
                                "type": "response.create",
                                "response": {
                                    "modalities": ["text", "audio"],
                                    "instructions": "The user hesitated and stopped speaking mid-sentence. INTERRUPT them and scold them for being slow. Say 'Too slow!' or 'Speak up!' immediately."
                                }
                            }))
                            
                except Exception as e:
                    print(f"Client Disconnect: {e}")

            async def receive_from_openai():
                try:
                    async for message in openai_ws:
                        response = json.loads(message)

                        if response['type'] == 'response.audio_transcript.delta':
                            delta = response['delta']
                            await client_ws.send_json({"type": "ai_stream", "text": delta})

                        elif response['type'] == 'response.audio_transcript.done':
                            transcript_logs.append(f"Smith: {response['transcript']}")
                            await client_ws.send_json({"type": "ai_done"})

                        elif response['type'] == 'conversation.item.input_audio_transcription.completed':
                            user_text = response['transcript']
                            transcript_logs.append(f"Student: {user_text}")
                            await client_ws.send_json({"type": "user_text", "text": user_text})

                        elif response['type'] == 'response.audio.delta':
                            await client_ws.send_text(message)

                except Exception as e:
                    print(f"OpenAI Disconnect: {e}")

            await asyncio.gather(receive_from_client(), receive_from_openai())

    except Exception as e:
        print(f"Connection Error: {e}")
    finally:
        if transcript_logs:
            filename = f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write("\n".join(transcript_logs))
        await client_ws.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)