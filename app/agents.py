from crewai import Agent, Crew

# Define CrewAI agents for each function
summary_agent = Agent(
    role="Summary Agent",
    goal="Generate a practical, actionable cultural summary for a given culture.",
    backstory="Expert in cross-cultural communication and travel guidance.",
    tools=[],
    verbose=True
)

etiquette_agent = Agent(
    role="Etiquette Agent",
    goal="Provide etiquette rules and tips for interacting with people from a given culture.",
    backstory="Specialist in global etiquette and social norms.",
    tools=[],
    verbose=True
)

comm_agent = Agent(
    role="Communication Agent",
    goal="Describe communication preferences and styles for a given culture.",
    backstory="Expert in international communication styles.",
    tools=[],
    verbose=True
)

recommendation_agent = Agent(
    role="Recommendation Agent",
    goal="Generate must-know tips and common mistakes for visitors to a given culture.",
    backstory="Travel advisor focused on practical advice.",
    tools=[],
    verbose=True
)

# CrewAI orchestration (preserves previous logic)
def crewai_generate_culture_summary(culture: str, verbosity: str = "medium", sections=None):
    # Define tasks for each agent
    summary_task = Task(
        description=f"Generate a cultural summary for {culture} with verbosity {verbosity}.",
        agent=summary_agent
    )
    etiquette_task = Task(
        description=f"Provide etiquette rules for {culture}.",
        agent=etiquette_agent
    )
    comm_task = Task(
        description=f"Describe communication style for {culture}.",
        agent=comm_agent
    )
    recommendation_task = Task(
        description=f"List must-know tips and common mistakes for {culture}.",
        agent=recommendation_agent
    )

    crew = Crew(
        agents=[summary_agent, etiquette_agent, comm_agent, recommendation_agent],
        tasks=[summary_task, etiquette_task, comm_task, recommendation_task],
        verbose=True
    )
    results = crew.kickoff()
    # Map CrewAI results to previous output format
    return {
        "summary": results[0],
        "etiquette": results[1],
        "communication_style": results[2],
        "recommendations": results[3],
        "sections": sections
    }

# Preserve previous API: allow switching between CrewAI and legacy logic
def generate_culture_summary(culture: str, verbosity: str = "medium", sections=None, use_crew=False) -> dict:
    if use_crew:
        return crewai_generate_culture_summary(culture, verbosity=verbosity, sections=sections)
    else:
        return _wrap_generate_culture_summary(culture, verbosity=verbosity, sections=sections)
import os
import json
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini API directly
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize API and model
import google.generativeai as genai
genai.configure(api_key=GEMINI_API_KEY)

# Try models in order of preference
model = None
models_to_try = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-pro", "gemini-1.5-pro"]

for model_name in models_to_try:
    try:
        model = genai.GenerativeModel(model_name)
        print(f"Using model: {model_name}")
        break
    except Exception as e:
        print(f"Model {model_name} not available: {e}")
        continue

if model is None:
    raise Exception("No available models found. Check your API key.")


def cultural_summary_prompt(culture: str) -> str:
    return f"""Produce a practical, actionable cultural briefing for {culture} aimed at travelers and professionals.
Output exactly 6–10 short sections, each with a clear heading (one line) followed by 1–3 short sentences or 2 short bullets. Use plain, direct language and avoid long paragraphs.

Suggested section headings (use those or equally clear equivalents):
- Quick Snapshot
- How to Greet
- Politeness & Titles
- Gestures & Body Language
- Common Taboos / What to Avoid
- Communication Tone
- Workplace Tips
- Social & Travel Tips

Total length: aim for 350–600 words. For each section give specific, actionable guidance (what to do, what to avoid, and why). Prefer examples and short phrases the user can follow. No long historical essays — focus on practical behavior and short explanations."""


def persona_chat_prompt(culture: str, persona: str, text: str) -> str:
    return f"""You are {persona} from {culture}. Respond succinctly to this message: "{text}"

Reply in character using cultural phrasing, but keep your reply to 1–3 short sentences (or 2–3 short bullet points).
Be friendly and clear; avoid long paragraphs."""


def etiquette_feedback_prompt(culture: str, text: str) -> str:
    return f"""Analyze the following message for cross-cultural etiquette when interacting with people from {culture}:
    
Message: "{text}"

Provide constructive feedback on:
1. Any potential cultural sensitivities or faux pas
2. Recommended adjustments for better cultural alignment
3. Positive aspects of the communication
4. Tips for more respectful interaction

Be constructive and helpful, not judgmental. Keep feedback to 3 short points or under ~150 words."""


def generate_culture_summary(culture: str, verbosity: str = "medium", sections=None) -> dict:
    """Generate a cultural summary using Gemini API.

    Accepts an optional `verbosity` argument (concise|medium|detailed) and `sections`.
    """
    return _wrap_generate_culture_summary(culture, verbosity=verbosity, sections=sections)

def _wrap_generate_culture_summary(culture: str, verbosity: str = "medium", sections=None):
    # This function wraps the raw summary and formats the output.
    # The sections argument is accepted for future use (custom summaries).
    raw_summary, raw_etique, raw_comm = _raw_generate_culture_summary(culture.strip().lower(), verbosity)

    # Generate personalized recommendations (must-know tips and common mistakes)
    try:
        tips_prompt = (
            f"List 2–3 must-know tips for visitors to {culture}. Use short, actionable bullet points."
        )
        mistakes_prompt = (
            f"List 2 common mistakes to avoid when interacting with locals in {culture}. Use short, actionable bullet points."
        )
        tips_response = model.generate_content(tips_prompt)
        mistakes_response = model.generate_content(mistakes_prompt)
        recommendations = "\n**Personalized Recommendations**\n" + \
            "\nMust-Know Tips:\n" + tips_response.text.strip() + \
            "\nCommon Mistakes to Avoid:\n" + mistakes_response.text.strip()
    except Exception:
        recommendations = ""

    return {
        "summary": raw_summary,
        "etiquette": raw_etique,
        "communication_style": raw_comm,
        "recommendations": recommendations,
        "sections": sections  # Pass through for future use
    }

from functools import lru_cache


@lru_cache(maxsize=128)
def _raw_generate_culture_summary(culture: str, verbosity: str = "medium"):
    """Internal cached call that returns raw strings (not truncated)."""
    # Build distinctly different prompts per verbosity so outputs are noticeably different.
    if verbosity == "concise":
        # Very short, skimmable briefing
        prompt = (
            f"Provide a VERY BRIEF practical cultural briefing for {culture}."
            " Output 4 short sections with clear one-line headings and 1 short sentence or 1 bullet each."
            " Emphasize only the most essential do's and don'ts. Use plain short phrases and examples."
        )
        etiquette_prompt = (
            f"List 2 immediate etiquette rules for interacting with people from {culture}. Use 1 short sentence or bullet each."
        )
        comm_prompt = (
            f"List 2 quick communication tips for {culture} (tone, directness, formality). Use 1 short sentence each."
        )

    elif verbosity == "detailed":
        # Rich, example-driven briefing
        prompt = (
            cultural_summary_prompt(culture)
            + "\n\nFor each section include 1 brief example or short scenario (1-2 sentences) illustrating the tip."
        )
        etiquette_prompt = (
            f"Provide 5 detailed etiquette points for {culture}. For each point give a one-line explanation and a short example or consequence of ignoring it."
        )
        comm_prompt = (
            f"Describe communication preferences in {culture} in detail: include tone, indirect vs direct, typical formality, common phrasing to use/avoid, and 2 short examples."
        )

    else:
        # medium (default): practical, actionable, moderate length
        prompt = (
            f"Produce a practical cultural briefing for {culture} with 6 short sections (headings + 1–2 short sentences)."
            " Focus on actionable guidance and 1 brief example per 2–3 sections."
        )
        etiquette_prompt = (
            f"Provide 3 concise etiquette points for {culture}. For each, give a 1-line why and 1 brief example."
        )
        comm_prompt = (
            f"Describe communication preferences in {culture} with 3 short points (tone, directness, formality) and one short example each."
        )

    response = model.generate_content(prompt)
    etiquette_response = model.generate_content(etiquette_prompt)
    comm_response = model.generate_content(comm_prompt)

    raw_et = etiquette_response.text


    def _count_points(text: str) -> int:
        # Count lines that look like list items or numbered points
        if not text:
            return 0
        count = 0
        lines = text.splitlines()
        for l in lines:
            l = l.strip()
            if not l:
                continue
            if l[0].isdigit() and (l[1:2] == '.' or l[1:2] == ')'):
                count += 1
            elif l.startswith(('-', '*', '•')):
                count += 1
        # fallback: if there are multiple short sentences, approximate
        if count == 0:
            # count sentences as proxy
            count = max(0, min(10, text.count('.') + text.count('!') + text.count('?')))
        return count

    # If detailed verbosity requested, ensure etiquette has at least 5 points
    if verbosity == "detailed":
        try:
            need = 5 - _count_points(raw_et)
            if need > 0:
                add_prompt = (
                    f"You previously listed some etiquette points for {culture}."
                    f" Please provide {need} additional, distinct etiquette points (one per line), numbered,"
                    " and do not repeat the earlier points. Keep each point to one sentence."
                )
                add_resp = model.generate_content(add_prompt)
                # append the new points
                raw_et = (raw_et.rstrip() + "\n" + add_resp.text).strip()
        except Exception:
            # best-effort, ignore failures
            pass

    return (response.text, raw_et, comm_response.text)



def chat_with_persona(culture: str, persona: str, message: str, verbosity: str = "medium") -> dict:
    """Chat as a cultural persona using Gemini API."""
    try:
        # adjust prompt slightly based on verbosity
        if verbosity == "concise":
            prompt = persona_chat_prompt(culture, persona, message) + "\n\nReply in 1 short sentence."
            resp_limit = 300
        elif verbosity == "detailed":
            prompt = persona_chat_prompt(culture, persona, message) + "\n\nYou may answer with 3-5 short sentences if helpful."
            resp_limit = 1200
        else:
            prompt = persona_chat_prompt(culture, persona, message)
            resp_limit = 800

        response = model.generate_content(prompt)

        feedback_prompt = etiquette_feedback_prompt(culture, message)
        feedback_response = model.generate_content(feedback_prompt)

        return {
            "response": truncate_text(response.text, max_chars=resp_limit),
            "feedback": truncate_text(feedback_response.text, max_chars=800)
        }
    except Exception as e:
        raise Exception(f"Error generating response: {str(e)}")


def continue_text(existing_text: str) -> str:
    """Ask the model to continue the provided text. Returns continuation text (best-effort)."""
    try:
        if not existing_text:
            return ""
        # Provide a stronger instruction to avoid repetition and to only return new text.
        # Include a short context window (last 400 chars) to keep prompt concise.
        context = existing_text.strip()[-400:]
        prompt = (
            "Finish the last incomplete sentence from the text below and then add 1-2 concise sentences to complete the thought. "
            "Do NOT repeat any of the existing words or sentences — return ONLY the new continuation text (no quotes, no extra commentary). "
            "Keep the continuation short and directly connected to the previous content.\n\n"
            f"TEXT CONTEXT:\n{context}"
        )
        cont = model.generate_content(prompt)
        return cont.text
    except Exception:
        return ""


def normalize_agent_output(result):
    if isinstance(result, dict):
        return result
    return {"text": str(result)}


def truncate_text(text: str, max_chars: int = 1000) -> str:
    """Trim text to at most `max_chars` without cutting mid-word; append ellipsis if truncated."""

    if text is None:
        return ""
    s = str(text).strip()
    if len(s) <= max_chars:
        return s
    # cut and avoid breaking a word
    cut = s[:max_chars]
    if " " in cut:
        cut = cut.rsplit(" ", 1)[0]
    return cut + "..."

# Utility to filter resource results (for use in resource display logic)
def filter_resource_links(links):
    """
    Remove inaccurate or non-web URLs from resource results.
    Only keep links that start with http(s) and exclude local file paths or irrelevant sources.
    """
    filtered = []
    for link in links:
        if isinstance(link, str) and link.strip().lower().startswith(('http://', 'https://')):
            filtered.append(link)
    return filtered
