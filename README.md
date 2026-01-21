# 🎙️ Taylor
**AI Voice Coaching Agent (Project by Team Calli)**

> **Real-time English conversation coach designed for Business & Travel scenarios.**
> Powered by OpenAI Realtime API (WebSocket/Async).

## 💡 Overview
**Taylor** is a voice-first AI agent developed by **Calli**, aimed at helping non-native speakers practice English in realistic scenarios. Unlike traditional TTS/STT pipelines, Taylor utilizes **OpenAI's Realtime API** to achieve ultra-low latency and natural turn-taking.

This project was developed as a **Rapid Prototype** to solve a personal pain point: the lack of accessible, real-time speaking practice partners.

## 🚀 Key Features
- **True Real-time Interaction:** Leverages **OpenAI Realtime API** for fluid, interruption-friendly conversations without the lag of traditional transcoding.
- **Scenario-Based Coaching:** Supports 15+ roleplay scenarios including *Business Negotiation, Hotel Check-in,* and *Casual Small Talk*.
- **Direct Audio Streaming:** Implemented raw audio streaming logic using Python AsyncIO for seamless bi-directional communication.

## 🛠 Tech Stack
- **Core Engine:** OpenAI Realtime API (GPT-4o Audio)
- **Protocol:** WebSockets
- **Language:** Python (AsyncIO)

## 🎯 How It Works
1. The user starts the conversation with a specific topic (e.g., "Salary Negotiation").
2. **Taylor** initiates the dialogue with a scenario-specific opening.
3. The system streams audio directly to/from OpenAI, allowing for instant feedback.
4. Taylor responds with natural dialogue, adopting a strict but helpful persona.

## 🔜 Future Improvements
- **Dashboard:** Visualize "Grammar Accuracy" and vocabulary usage over time.
- **Dual Modes:**
  - *Practice Mode:* Strict persona for intensive training.
  - *Realtime Mode:* Instant assistance for real-world conversations (e.g., translating/hinting during a meeting).

---
*Created by Hyuntae Jeong.*
