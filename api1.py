from flask import Flask, request, Response
from flask_cors import CORS
from deep_translator import GoogleTranslator
from openai import OpenAI
from langdetect import detect, DetectorFactory
import re
import json
import os

app = Flask(__name__)
CORS(app)

# ==========================
# ✅ OpenAI API Configuration
# ==========================
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
print("OPENAI_API_KEY Loaded" if OPENAI_API_KEY else "OPENAI_API_KEY missing - GPT responses disabled")

# ==========================
# ✅ Gold Investment Facts
# ==========================
gold_investment_facts = {
    "basic": "Investing in gold helps hedge against inflation. Digital gold allows you to invest without physically storing it.",
    "purchase_suggestion": "Would you like to purchase digital gold via the Simplify Money app? It’s a convenient and safe way to start investing in gold.",
    "disclaimer": "This is general financial guidance. Please consult a certified advisor before making investment decisions."
}

# ==========================
# ✅ Gold-related Keywords
# ==========================
keywords = [
    r"\bgold\b", r"\bdigital gold\b", r"\binvest\b", r"\bpurchase gold\b", r"\bbuy gold\b",
    r"\byellow metal\b", r"\bsona\b", r"\binvestment\b",
    r"\bसोना\b", r"\bडिजिटल गोल्ड\b"
]

# ==========================
# ✅ Session Memory (per user_id)
# ==========================
session_memory = {}

# ==========================
# ✅ Language Detection Setup
# ==========================
DetectorFactory.seed = 0  # ensures consistent results

def detect_language(query: str) -> str:
    """Detect the input language of the query."""
    try:
        return detect(query)  # returns ISO 639-1 code, e.g., 'en', 'hi', 'mr'
    except Exception as e:
        print(f"⚠️ Language detection failed: {e}")
        return "en"

# ==========================
# ✅ Gold Investment Query Check
# ==========================
def is_gold_investment_query(query: str) -> bool:
    """
    Returns True if the query matches any gold-related keywords.
    Automatically translates to English for keyword matching.
    """
    try:
        translated_query = GoogleTranslator(source='auto', target='en').translate(query).lower()
    except Exception as e:
        print(f"⚠️ Translation failed: {e}")
        translated_query = query.lower()
    
    return any(re.search(pattern, translated_query) for pattern in keywords)

# ==========================
# ✅ GPT-based Query Classifier
# ==========================
def classify_query(query: str) -> str:
    """Use GPT to classify queries into categories: gold, finance_general, or other."""
    try:
        if not client:
            # Heuristic fallback if no OpenAI key
            return "gold" if is_gold_investment_query(query) else "other"
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Classify the user query into one of: 'gold', 'finance_general', 'other'. Reply with one word only."},
                {"role": "user", "content": query}
            ],
            temperature=0
        )
        return completion.choices[0].message.content.strip().lower()
    except Exception as e:
        print(f"⚠️ Classification failed: {e}")
        return "other"

# ==========================
# ✅ GPT Query Handler
# ==========================
def ask_gpt(query: str, category: str, history: list) -> str:
    """Ask GPT with category context and language enforcement."""
    try:
        if not client:
            # Fallback deterministic message without external API
            detected_lang = detect_language(query)
            if category == "gold" or is_gold_investment_query(query):
                return "आप सोने में निवेश पर विचार कर रहे हैं। डिजिटल गोल्ड एक आसान और सुरक्षित विकल्प है।" if detected_lang == "hi" else "You are considering gold investment. Digital gold is an easy and safe option."
            return "मैं आपके वित्तीय प्रश्नों में सहायता कर सकता हूँ।" if detected_lang == "hi" else "I can help with your personal finance questions."
        detected_lang = detect_language(query)

        system_prompt = f"""
You are Kuber AI, a friendly, human-like financial assistant.
Always reply in {detected_lang}, the same language as the user's query.
Be empathetic, helpful, and engaging.
Use emojis sparingly when appropriate.
"""
        if category == "gold":
            system_prompt += "Focus your answer on gold investments, digital gold, and related advice."
        elif category == "finance_general":
            system_prompt += "Provide helpful personal finance guidance, savings, SIPs, or insurance suggestions."

        # Build message history for context
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(history[-3:])  # last 3 messages
        messages.append({"role": "user", "content": query})

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=300
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"⚠️ GPT request failed: {e}")
        return "I'm here to assist with finance and gold investments. Could you please rephrase your question?"

# ==========================
# ✅ Flask API Endpoint
# ==========================
@app.route('/api/query', methods=['POST'])
def handle_query():
    data = request.json
    user_id = data.get("userId", "default")
    user_query = data.get("userQuery", "").strip()

    if not user_query:
        return Response(json.dumps({"message": "Please provide a valid query."}, ensure_ascii=False),
                        mimetype='application/json; charset=utf-8', status=400)

    # Initialize session memory
    if user_id not in session_memory:
        session_memory[user_id] = {
            "history": [],
            "last_intent": None,
            "last_redirect": False
        }

    history = session_memory[user_id]["history"]

    # ==========================
    # ✅ Yes/No Follow-up Detection
    # ==========================
    yes_patterns = [r"\byes\b", r"\bहाँ\b", r"\bhaan\b", r"\bहो\b"]
    no_patterns = [r"\bno\b", r"\bनहीं\b", r"\bnahin\b"]

    if session_memory[user_id]["last_redirect"]:
        if any(re.search(p, user_query, re.IGNORECASE) for p in yes_patterns):
            session_memory[user_id]["last_redirect"] = False
            history.append({"role": "user", "content": user_query})
            response_payload = {
                "message": "Great! Redirecting you to the Simplify Money app to purchase digital gold 💰.",
                "redirectToPurchase": True
            }
            return Response(json.dumps(response_payload, ensure_ascii=False),
                            mimetype='application/json; charset=utf-8')
        elif any(re.search(p, user_query, re.IGNORECASE) for p in no_patterns):
            session_memory[user_id]["last_redirect"] = False
            history.append({"role": "user", "content": user_query})
            response_payload = {
                "message": "No worries! You can explore gold investment anytime. Let me know if you want guidance.",
                "redirectToPurchase": False
            }
            return Response(json.dumps(response_payload, ensure_ascii=False),
                            mimetype='application/json; charset=utf-8')

    # ==========================
    # ✅ Classify Query
    # ==========================
    category = classify_query(user_query)

    # ==========================
    # ✅ Gold Shortcut
    # ==========================
    if category == "gold" or is_gold_investment_query(user_query):
        session_memory[user_id]["last_intent"] = "gold_purchase"
        session_memory[user_id]["last_redirect"] = True
        history.append({"role": "user", "content": user_query})
        response_payload = {
            "education": gold_investment_facts["basic"],
            "action": gold_investment_facts["purchase_suggestion"],
            "disclaimer": gold_investment_facts["disclaimer"],
            "redirectToPurchase": True
        }
    else:
        session_memory[user_id]["last_intent"] = category
        session_memory[user_id]["last_redirect"] = False
        history.append({"role": "user", "content": user_query})
        gpt_answer = ask_gpt(user_query, category, history)
        history.append({"role": "assistant", "content": gpt_answer})
        response_payload = {
            "message": gpt_answer,
            "previousContext": [msg["content"] for msg in history[-3:]],
            "redirectToPurchase": False
        }

    return Response(json.dumps(response_payload, ensure_ascii=False),
                    mimetype='application/json; charset=utf-8')

# ==========================
# ✅ Run Flask App
# ==========================
if __name__ == "__main__":
    app.run(debug=True, port=3000)
