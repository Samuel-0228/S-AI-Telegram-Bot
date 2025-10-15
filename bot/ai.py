import glob
import os
import traceback
from datetime import datetime
from openai import OpenAI
from .config import OPENAI_KEY, AAU_NEWS_BOT, MODULES_BOT, GROQ_KEY

# Primary OpenAI client
client_openai = None
if OPENAI_KEY:
    try:
        client_openai = OpenAI(api_key=OPENAI_KEY)
    except Exception:
        client_openai = None

# Optional Groq fallback client (if GROQ_KEY provided)
client_groq = None
if GROQ_KEY:
    try:
        client_groq = OpenAI(
            api_key=GROQ_KEY, base_url="https://api.groq.com/openai/v1")
    except Exception:
        client_groq = None

# final escalation handle (you can change in config if you want)
ADMIN_HANDLE = "@AAU_STUDENTSBOT"


def _log_error(user_message: str, notes: str, exc: Exception = None):
    try:
        os.makedirs("data", exist_ok=True)
        with open(os.path.join("data", "error_log.txt"), "a", encoding="utf-8") as f:
            f.write(f"[{datetime.utcnow().isoformat()}] User: {user_message}\n")
            f.write(f"Notes: {notes}\n")
            if exc:
                f.write("Exception:\n")
                f.write("".join(traceback.format_exception(
                    type(exc), exc, exc.__traceback__)))
            f.write("-" * 80 + "\n")
    except Exception:
        # Never raise from logging
        pass


def save_to_results(user_message: str, bot_response: str):
    """Log each conversation into data/result.txt (for analytics / review)."""
    try:
        os.makedirs("data", exist_ok=True)
        with open(os.path.join("data", "result.txt"), "a", encoding="utf-8") as log:
            log.write(
                f"[{datetime.utcnow().isoformat()}] User: {user_message}\n")
            log.write(f"Bot: {bot_response}\n")
            log.write("-" * 60 + "\n")
    except Exception as e:
        # don't let logging break the bot
        _log_error(user_message, "Failed to save result", e)


def load_aau_files() -> dict:
    """
    Load all data/*.txt files (except result/error files) and return dict:
      { filename_without_ext: file_text }
    """
    files = sorted(glob.glob(os.path.join("data", "*.txt")))
    data_files = {}
    for file in files:
        name = os.path.basename(file)
        if name in ("result.txt", "error_log.txt"):
            continue
        key = os.path.splitext(name)[0]
        try:
            with open(file, "r", encoding="utf-8") as f:
                data_files[key] = f.read()
        except Exception as e:
            _log_error("", f"Failed reading file {file}", e)
    return data_files


def call_model(client: OpenAI, model: str, system_prompt: str, user_message: str) -> str:
    """Call model and return text. Exceptions are propagated to caller."""
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt.strip()},
            {"role": "user", "content": user_message},
        ],
    )
    return response.choices[0].message.content.strip()


def local_search(user_message: str) -> str | None:
    """
    Simple keyword-based local search across data/*.txt files.
    Returns a short excerpt or None if nothing relevant was found.
    """
    data_files = load_aau_files()
    if not data_files:
        return None

    # tokenize simple keywords from user message
    tokens = [t.lower() for t in user_message.split() if len(t) > 2]
    if not tokens:
        return None

    # score each file by number of token occurrences
    scores = {}
    for key, text in data_files.items():
        lower_text = text.lower()
        count = sum(lower_text.count(tok) for tok in tokens)
        if count > 0:
            scores[key] = count

    if not scores:
        return None

    # pick best file
    best_file = max(scores, key=scores.get)
    best_text = data_files.get(best_file, "")
    # try to find sentences containing tokens
    sentences = []
    for sent in best_text.splitlines():
        s_low = sent.lower()
        if any(tok in s_low for tok in tokens):
            if sent.strip():
                sentences.append(sent.strip())
        if len(sentences) >= 4:
            break

    if sentences:
        header = f"💡 Based on our AAU data ({best_file.replace('_', ' ').title()}):\n\n"
        excerpt = "\n".join(sentences)
        return header + excerpt
    else:
        # fallback: return first 300 chars of file as a hint
        snippet = best_text.strip()[:1000].strip()
        if snippet:
            header = f"💡 Based on our AAU data ({best_file.replace('_', ' ').title()}):\n\n"
            return header + snippet
    return None


def generate_reply(user_message: str) -> str:
    """
    4-layer response pipeline:
      1) OpenAI if available
      2) Groq fallback
      3) Local keyword search
      4) Admin escalation message
    Returns the final reply string (always a user-friendly string).
    """
    # compose system prompt with AAU data embedded (but keep it compact)
    aau_files = load_aau_files()
    # We will include small summaries per file (first N chars) to keep prompt size reasonable.
    aau_summary_parts = []
    for name, text in aau_files.items():
        snippet = text.strip()[:1000]  # limit per file
        aau_summary_parts.append(
            f"--- {name.replace('_', ' ').title()} ---\n{snippet}")

    aau_data_compact = "\n\n".join(aau_summary_parts)

    system_prompt = f"""
You are Savvy Chatbot — a helpful, concise assistant for Addis Ababa University (AAU) students.
When a question is about AAU, prefer the AAU knowledge below; otherwise use your general knowledge.

If the user asks about promotions, events, announcements, any person and anything not present in the AAU data, direct them to the official students bot {ADMIN_HANDLE}).
If they ask about course modules or study materials, direct them to the modules bot(@Savvysocietybot).
Be concise and avoid hallucinations; if you are uncertain, be transparent.

AAU Knowledge (compact):
{aau_data_compact}
"""

    # 1) Try OpenAI if configured
    if client_openai:
        try:
            bot_reply = call_model(
                client_openai, "gpt-4o-mini", system_prompt, user_message)
            full_reply = bot_reply + f"\n\n📢 @University_of_Addis_Ababa"
            save_to_results(user_message, bot_reply)
            return full_reply
        except Exception as e_openai:
            _log_error(user_message, "OpenAI call failed", e_openai)
    else:
        _log_error(user_message, "OpenAI not configured", None)

    # 2) Try Groq fallback if configured
    if client_groq:
        try:
            # Groq model names vary; use a conservative small/instant model if available.
            # If you have a specific Groq model, update this value via GROQ_KEY and config.
            bot_reply = call_model(
                client_groq, "llama-3.1-8b-instant", system_prompt, user_message)
            full_reply = bot_reply + f"\n\n📢 Subscribe: @University_of_Addis_Ababa"
            save_to_results(user_message, bot_reply)
            return full_reply
        except Exception as e_groq:
            _log_error(user_message, "Groq call failed", e_groq)
    else:
        _log_error(user_message, "Groq not configured", None)

    # 3) Try local keyword search (no API usage)
    try:
        local_result = local_search(user_message)
        if local_result:
            # local_result already includes a header (source). Add footer & save log.
            # Remove header before logging to keep logs shorter
            save_to_results(user_message, local_result)
            return local_result + f"\n\n📢 Subscribe: @University_of_Addis_Ababa"
    except Exception as e_local:
        _log_error(user_message, "Local search failed", e_local)

    # 4) Final escalation: ask user to contact admin
    _log_error(user_message, "All fallback layers failed", None)
    return f"⚠️ I couldn't find an accurate answer. Please contact the admins for help: {ADMIN_HANDLE}"
