"""
JARVIS AI Brain & Language Intelligence Provider
Modular provider supporting Gemini, OpenAI, or smart local rule-based heuristic synthesis.
Never exposes credentials and falls back gracefully when offline.
"""
import os
import json
from typing import Optional, Dict, Any

class AIBrain:
    def __init__(self):
        self.provider = "local"
        self._detect_provider()

    def _detect_provider(self):
        if os.getenv("GEMINI_API_KEY"):
            self.provider = "gemini"
        elif os.getenv("OPENAI_API_KEY"):
            self.provider = "openai"
        else:
            self.provider = "local"

    def generate_response(self, prompt: str, context: Optional[str] = None) -> str:
        """
        Generates conversational intelligence response using active provider,
        falling back to local smart synthesis if unavailable.
        """
        self._detect_provider()

        if self.provider == "gemini":
            try:
                from google import genai
                client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
                full_prompt = (
                    "You are J.A.R.V.I.S., an advanced British AI desktop assistant. "
                    "Be concise, direct, helpful, and natural. Keep responses under 3 sentences for pleasant speech.\n"
                )
                if context:
                    full_prompt += f"Context:\n{context}\n\n"
                full_prompt += f"User: {prompt}\nJARVIS:"
                
                resp = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=full_prompt
                )
                if resp.text:
                    return resp.text.strip()
            except Exception as e:
                print(f"[AIBrain] Gemini call failed: {e}")

        elif self.provider == "openai":
            try:
                import openai
                client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                messages = [
                    {"role": "system", "content": "You are J.A.R.V.I.S., an advanced British AI assistant. Be concise, direct, and pleasant."}
                ]
                if context:
                    messages.append({"role": "system", "content": f"Context: {context}"})
                messages.append({"role": "user", "content": prompt})

                resp = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    max_tokens=150
                )
                if resp.choices:
                    return resp.choices[0].message.content.strip()
            except Exception as e:
                print(f"[AIBrain] OpenAI call failed: {e}")

        # Ollama Local LLM Integration (from SUVI Upgrade Scaffold)
        try:
            import requests
            ollama_url = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434/api/chat")
            ollama_model = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b")
            ollama_payload = {
                "model": ollama_model,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are SUVI (Smart Unified Voice Intelligence), a helpful, personal AI assistant. "
                            "Be clear, concise, direct, and conversational. Keep responses under 3 sentences for speech."
                        )
                    },
                    {"role": "user", "content": prompt if not context else f"Context:\n{context}\n\nQuestion: {prompt}"}
                ],
                "stream": False
            }
            ollama_res = requests.post(ollama_url, json=ollama_payload, timeout=3)
            if ollama_res.status_code == 200:
                content = ollama_res.json().get("message", {}).get("content", "").strip()
                if content:
                    return content
        except Exception:
            pass

        # Local Smart Synthesizer (Zero-cost, Zero-key offline fallback)
        return self._local_synthesize(prompt, context)

    def _local_synthesize(self, prompt: str, context: Optional[str] = None) -> str:
        p_lower = prompt.lower()
        if context:
            # We have extracted context from search results or a web page
            first_part = context[:300].strip()
            if not first_part.endswith('.'):
                first_part += '.'
            return f"Based on the data retrieved: {first_part}"

        if "cybersecurity" in p_lower:
            return "Cybersecurity encompasses the protection of critical systems, networks, and data from digital exploitation and unauthorized intrusion."
        elif "ethical hacking" in p_lower:
            return "Ethical hacking involves authorized penetration testing and vulnerability assessments to reinforce system resilience."
        elif "python" in p_lower:
            return "Python is a high-level interpreted programming language renowned for its expressive syntax, broad library ecosystem, and rapid development capabilities."

        return f"Understood, sir. I have processed your inquiry regarding {prompt[:40]}."

# Global singleton
ai_brain = AIBrain()
