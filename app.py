import streamlit as st
from app.utils import load_dotenv_safe
load_dotenv_safe()
from app.crew_wrapper import CultureCrew
from app.agents import continue_text
import io
import re
from datetime import datetime

# Optional PDF support
try:
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.pagesizes import letter

    PDF_SUPPORTED = True

    def make_pdf_bytes(title: str, text: str) -> bytes:
        """Return nicely formatted PDF bytes using reportlab.platypus."""
        bio = io.BytesIO()
        doc = SimpleDocTemplate(bio, pagesize=letter, title=title)
        styles = getSampleStyleSheet()
        story = []

        # Title
        story.append(Paragraph(title, styles["Title"]))
        story.append(Spacer(1, 12))

        # If the text contains markdown-style headings, keep them as headings.
        for line in text.splitlines():
            s = line.strip()
            if not s:
                story.append(Spacer(1, 6))
                continue
            # heading-like line
            if s.endswith(":") or s.isupper() or s.startswith("# ") or s.startswith("## "):
                heading = s.replace("#", "").strip()
                story.append(Paragraph(heading, styles["Heading3"]))
            else:
                # simple body text
                # escape ampersands
                safe = s.replace("&", "&amp;")
                story.append(Paragraph(safe, styles["BodyText"]))
            story.append(Spacer(1, 6))

        doc.build(story)
        bio.seek(0)
        return bio.read()
except Exception:
    PDF_SUPPORTED = False


def sanitize_filename(name: str) -> str:
    """Sanitize a filename: allow letters, numbers, dot, underscore and hyphen; replace others with underscore."""
    return re.sub(r"[^A-Za-z0-9._-]", "_", name)


def _html_escape(text: str) -> str:
    if not text:
        return ""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _looks_cutoff(text: str) -> bool:
    if not text:
        return False
    s = text.strip()
    if s.endswith("..."):
        return True
    if s[-1] not in ".!?\"'”’":
        return len(s) > 80
    return False


def merge_texts(original: str, continuation: str) -> str:
    """Merge original + continuation while removing overlapping repeated fragments.

    Strategy:
    - try to find a character-level overlap between the end of `original` and start of `continuation` (up to 200 chars)
    - if none, try to find word-level overlap (up to 20 words)
    - if still none, just append with a space
    """
    if not continuation:
        return original or ""
    if not original:
        return continuation.strip()

    a = original.rstrip()
    b = continuation.lstrip()

    # normalize for matching (lowercase, collapse spaces)
    def norm(s: str) -> str:
        return re.sub(r"\s+", " ", s.strip().lower())

    na = norm(a)
    nb = norm(b)

    # try char-level overlap
    max_chars = min(200, len(na), len(nb))
    for k in range(max_chars, 20, -1):
        if na.endswith(nb[:k]):
            # remove overlap from b
            return (a + b[k:]).strip()

    # try word-level overlap
    a_words = na.split()
    b_words = nb.split()
    max_words = min(20, len(a_words), len(b_words))
    for k in range(max_words, 0, -1):
        if a_words[-k:] == b_words[:k]:
            # compute char index in b where overlap ends
            # find the substring corresponding to first k words of original b (before normalization use)
            # fallback: remove the matched prefix from b by word
            b_word_list = b.split()
            # remove first k words from b
            new_b = " ".join(b_word_list[k:])
            return (a + " " + new_b).strip()

    # nothing matched — just append with a single space
    return (a + " " + b).strip()

crew = CultureCrew()

st.set_page_config(page_title="AI Culture Companion", layout="wide")



# Aesthetic, professional, and visually pleasing CSS overhaul
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif !important;
        background: linear-gradient(120deg, #f6f8fc 0%, #e3eaf7 100%) !important;
    }
    .block-container {
        max-width: 950px;
        margin: 48px auto 0 auto;
        padding: 0 0 36px 0;
    }
    /* Sidebar aesthetic */
    section[data-testid="stSidebar"] {
        background: linear-gradient(120deg, #e8f0fe 0%, #f6f8fc 100%);
        border-right: 1.5px solid #e0e7ef;
        min-width: 320px;
        box-shadow: 2px 0 16px 0 rgba(30,41,59,0.06);
    }
    .pro-title {
        font-size:2.1rem; font-weight:700; color:#1e293b; letter-spacing:-1px; margin-bottom:0.1em;
        display:flex; align-items:center; gap:12px;
        text-shadow:0 2px 8px rgba(30,41,59,0.04);
    }
    .pro-title .icon {font-size:2.1rem;}
    .pro-subtitle {
        color:#4b5563; font-size:1.08rem; margin-bottom:1.7em; margin-top:-0.5em;
        font-weight:500; letter-spacing:0.01em;
        line-height:1.5;
    }
    .pro-card {
        background: linear-gradient(120deg, #fff 80%, #f3f6fa 100%);
        border-radius: 16px; box-shadow: 0 4px 24px rgba(30,41,59,0.08);
        padding: 2em 2em 1.3em 2em; margin-bottom:2em;
        border: 1.5px solid #e2e8f0;
        transition: box-shadow 0.18s;
    }
    .pro-card:hover {
        box-shadow: 0 8px 32px rgba(30,41,59,0.13);
    }
    .pro-section-title {
        font-size:1.18rem; font-weight:600; color:#2563eb; margin-bottom:0.6em; margin-top:0.2em;
        display:flex; align-items:center; gap:8px;
    }
    .pro-section-title .icon {font-size:1.2em;}
    .pro-label {
        font-weight:600; color:#334155; margin-bottom:0.2em; display:block; font-size:1.04em;
    }
    .pro-input, .pro-select, textarea, input, select {
        border-radius:8px; border:1.5px solid #cbd5e1; padding:0.7em 1em; font-size:1em; margin-bottom:1.1em;
        background:#f8fafc; color:#1e293b; font-family:'Inter',sans-serif;
        box-shadow:0 1px 4px rgba(30,41,59,0.04);
        transition: border 0.15s, box-shadow 0.15s;
    }
    .pro-input:focus, .pro-select:focus, textarea:focus, input:focus, select:focus {
        border:1.5px solid #2563eb; box-shadow:0 2px 8px #2563eb22;
    }
    .pro-btn, button[kind="primary"] {
        background:linear-gradient(90deg,#3b82f6,#2563eb); color:#fff; border:none; border-radius:8px;
        font-weight:600; font-size:1em; padding:0.65em 1.4em; cursor:pointer; transition:all 0.13s;
        box-shadow:0 2px 8px rgba(30,41,59,0.09);
        margin-bottom: 0.2em;
    }
    .pro-btn:hover, button[kind="primary"]:hover {
        background:linear-gradient(90deg,#2563eb,#3b82f6); transform:translateY(-2px) scale(1.03);
        box-shadow:0 4px 16px rgba(30,41,59,0.13);
    }
    .pro-followup-btn {
        background:#e0e7ef; color:#2563eb; border:none; border-radius:7px; padding:0.5em 1em; margin-right:0.5em; margin-bottom:0.5em;
        font-weight:500; font-size:0.98em; cursor:pointer; transition:background 0.13s;
    }
    .pro-followup-btn:hover {background:#c7d2fe; color:#1e293b;}
    .pro-caption {color:#64748b; font-size:0.98em; margin-bottom:1.2em;}
    .small {font-size:13px; color:#6b7280}
    .muted {color:#6b7280}
    /* Expander tweaks */
    .streamlit-expanderHeader {
        font-size:1.08em; font-weight:600; color:#2563eb;
    }
    /* Download button tweaks */
    .stDownloadButton > button {
        background:linear-gradient(90deg,#3b82f6,#2563eb)!important; color:#fff!important; border-radius:8px!important;
        font-weight:600; font-size:1em; padding:0.65em 1.4em; margin-bottom:0.2em;
        box-shadow:0 2px 8px rgba(30,41,59,0.09);
        border:none;
    }
    .stDownloadButton > button:hover {
        background:linear-gradient(90deg,#2563eb,#3b82f6)!important; color:#fff!important;
        box-shadow:0 4px 16px rgba(30,41,59,0.13);
    }
    /* Text input tweaks */
    .stTextInput > div > input, .stTextArea > div > textarea {
        border-radius:8px!important; border:1.5px solid #cbd5e1!important; background:#f8fafc!important;
        font-size:1em!important; color:#1e293b!important; font-family:'Inter',sans-serif!important;
        box-shadow:0 1px 4px rgba(30,41,59,0.04)!important;
        transition: border 0.15s, box-shadow 0.15s;
    }
    .stTextInput > div > input:focus, .stTextArea > div > textarea:focus {
        border:1.5px solid #2563eb!important; box-shadow:0 2px 8px #2563eb22!important;
    }
    /* Tabs aesthetic */
    .stTabs [data-baseweb="tab-list"] {
        background: #f3f6fa;
        border-radius: 10px 10px 0 0;
        box-shadow: 0 2px 8px rgba(30,41,59,0.04);
        padding: 0.2em 0.5em 0 0.5em;
    }
    .stTabs [data-baseweb="tab"] {
        font-size:1.08em; font-weight:600; color:#2563eb;
        border-radius: 8px 8px 0 0;
        margin-right: 0.5em;
    }
    .stTabs [aria-selected="true"] {
        background: #e0e7ef;
        color: #1e293b;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# Move title and subtitle to sidebar for a stable left-side display
with st.sidebar:
    st.markdown(
        '''<div style="position:sticky;top:0;z-index:10;background:inherit;padding-bottom:1.2em;">
        <div class="pro-title"><span class="icon">🌍</span>AI Culture Companion</div><br>
        <div class="pro-subtitle">Learn etiquette, communication styles, social norms, and cultural do’s & don’ts - in seconds.<br><span style="color:#2563eb;font-weight:600;">Professional, actionable, exportable.</span></div>
        </div>''',
        unsafe_allow_html=True
    )

# main content container to center and constrain width
st.markdown('<div class="block-container">', unsafe_allow_html=True)

if not PDF_SUPPORTED:
    st.info("PDF downloads require the `reportlab` package. Install it in your virtualenv to enable PDF exports:\n`pip install reportlab`")

# Sidebar: keep defaults but remove visible settings controls
sidebar_user = "user123"
sidebar_verbosity = "medium"

tab1, tab2, tab3 = st.tabs(["Cultural Summary", "Persona Chat", "Your Notes"])

with tab1:
    st.header("Cultural Summary")
    # Main output column (full width in content area) — summary is not scrollable
    # Removed misplaced outer card; only wrap actual content sections in cards

    # Controls moved into the sidebar to keep them separate from the scrolling summary
    with st.sidebar.expander("Cultural Summary Controls", expanded=True):
        st.markdown('<div class="card">', unsafe_allow_html=True)
        # Group label, input, select, and caption for better alignment
        st.markdown('<div class="pro-label">✨ Choose Detail Level</div>', unsafe_allow_html=True)
        col1, col2 = st.columns([2,1])
        with col1:
            culture = st.text_input("Enter a culture/country:", "", key="input_culture_sidebar")
        with col2:
            verbosity = st.selectbox("Verbosity", ["concise", "medium", "detailed", "custom"], index=["concise","medium","detailed","custom"].index(sidebar_verbosity) if sidebar_verbosity in ["concise","medium","detailed","custom"] else 1, key="input_verbosity_sidebar")
        st.caption("How detailed should the cultural summary be?")
        username = sidebar_user

        # Custom section selection
        custom_sections = {"Summary": True, "Etiquette": True, "Communication Style": True}
        selected_sections = []
        if verbosity == "custom":
            st.markdown('<div class="pro-label">Select Sections to Include</div>', unsafe_allow_html=True)
            cols = st.columns(len(custom_sections))
            for i, section in enumerate(custom_sections.keys()):
                checked = st.session_state.get(f"custom_section_{section}", custom_sections[section])
                val = cols[i].checkbox(section, value=checked, key=f"custom_section_{section}")
                if val:
                    selected_sections.append(section)
        else:
            selected_sections = []

        if st.button("Generate Summary", key="gen_summary_btn_sidebar"):
            if not culture.strip():
                st.error("Please enter a culture.")
            else:
                with st.spinner("Generating summary..."):
                    if verbosity == "custom":
                        result = crew.generate_summary_with_verbosity(culture, username, verbosity=verbosity, sections=selected_sections)
                    else:
                        result = crew.generate_summary_with_verbosity(culture, username, verbosity=verbosity)
                    st.session_state["last_summary"] = result
                    st.session_state["last_summary_culture"] = culture
                    st.session_state["last_summary_verbosity"] = verbosity
                    st.session_state["last_summary_sections"] = selected_sections

        st.markdown("---")

    # Suggested follow-ups in their own expander
    with st.sidebar.expander("Suggested Follow-up Questions", expanded=False):
        st.markdown('<div class="small muted">Suggested follow-ups</div>', unsafe_allow_html=True)
        if culture:
            s1 = f"What gestures are considered rude in {culture}?"
            s2 = f"How do I greet someone older in {culture}?"
            s3 = f"What dress considerations should I know when visiting {culture}?"
        else:
            s1 = "What gestures are considered rude in this culture?"
            s2 = "How do I greet someone older in this culture?"
            s3 = "What dress considerations should I know when visiting?"

        if st.button(s1, key="sugg1_sidebar"):
            st.session_state["followup_question"] = s1
        if st.button(s2, key="sugg2_sidebar"):
            st.session_state["followup_question"] = s2
        if st.button(s3, key="sugg3_sidebar"):
            st.session_state["followup_question"] = s3

        followup = st.text_area("Follow-up question", value=st.session_state.get("followup_question", ""), key="followup_area_sidebar")
        if st.button("Ask Follow-up (Persona)", key="ask_followup_sidebar"):
            if not (culture.strip() and followup.strip()):
                st.error("Provide a culture and a follow-up question first.")
            else:
                with st.spinner("Asking local persona..."):
                    resp = crew.chat_as_culture_with_verbosity(culture, "local expert", followup, username, verbosity=st.session_state.get("last_summary_verbosity","medium"))
                    st.session_state["last_followup"] = resp


    # Main output column (full width in content area) — summary is not scrollable
    st.markdown('<div class="card">', unsafe_allow_html=True)
    # output area: either placeholder or the last generated summary
    if st.session_state.get("last_summary") and st.session_state.get("last_summary_culture"):
        last = st.session_state["last_summary"]
        last_culture = st.session_state["last_summary_culture"]

        # Reading time and summary grouped visually
        if last.get("summary"):
            word_count = len(last.get("summary","").split())
            minutes = max(1, int(word_count / 220)) if word_count else 0
            if minutes:
                st.caption(f"⏱ Approx. reading time: {minutes} min")
            st.subheader("📝 Summary")
            st.write(last.get("summary", ""))
            st.markdown('<hr style="border:none;border-top:2px solid #e0e7ef;margin:32px 0 24px 0;">', unsafe_allow_html=True)

        # Section display logic
        sections = st.session_state.get("last_summary_sections", [])
        if st.session_state.get("last_summary_verbosity") == "custom" and sections:
            if "Etiquette" in sections and last.get("etiquette"):
                st.subheader("🤝 Etiquette")
                st.write(last.get("etiquette", ""))
                st.markdown('<hr style="border:none;border-top:2px solid #e0e7ef;margin:32px 0 24px 0;">', unsafe_allow_html=True)
            if "Communication Style" in sections and last.get("communication_style"):
                st.subheader("💬 Communication Style")
                st.write(last.get("communication_style", ""))
                st.markdown('<hr style="border:none;border-top:2px solid #e0e7ef;margin:32px 0 24px 0;">', unsafe_allow_html=True)
        else:
            if last.get("etiquette"):
                st.subheader("🤝 Etiquette")
                st.write(last.get("etiquette", ""))
                st.markdown('<hr style="border:none;border-top:2px solid #e0e7ef;margin:32px 0 24px 0;">', unsafe_allow_html=True)
            if last.get("communication_style"):
                st.subheader("💬 Communication Style")
                st.write(last.get("communication_style", ""))
                st.markdown('<hr style="border:none;border-top:2px solid #e0e7ef;margin:32px 0 24px 0;">', unsafe_allow_html=True)

        # Show personalized recommendations if present
        if last.get("recommendations"):
            st.subheader("⭐ Personalized Recommendations")
            st.markdown(last.get("recommendations"))
            st.markdown('<hr style="border:none;border-top:2px solid #e0e7ef;margin:32px 0 24px 0;">', unsafe_allow_html=True)

        # Collapsible examples (if present)
        if last.get("examples"):
            with st.expander("Show Example(s)"):
                st.write(last.get("examples"))
            st.markdown('<hr style="border:none;border-top:2px solid #e0e7ef;margin:32px 0 24px 0;">', unsafe_allow_html=True)

        # Dynamic Related Resources using an agent
        if last.get("summary") or last.get("etiquette") or last.get("communication_style"):
            st.subheader("🔗 Related Resources")
            country = st.session_state.get("last_summary_culture", "")
            if country:
                with st.spinner("Finding relevant resources..."):
                    try:
                        resources = crew.get_related_resources(country)
                    except Exception:
                        resources = []
                if resources:
                    for r in resources:
                        st.markdown(f"- [{r.get('title', r.get('url','Resource'))}]({r.get('url','')})")
                else:
                    st.info("No specific resources found. Try another country or check back later.")
            else:
                st.info("Generate a summary to see related resources.")
            st.markdown('<hr style="border:none;border-top:2px solid #e0e7ef;margin:32px 0 24px 0;">', unsafe_allow_html=True)

        # Continuation controls inline
        if _looks_cutoff(last.get("summary", "")):
            if st.button("Continue Summary", key=f"cont_summary_{last_culture}"):
                cont = continue_text(last.get("summary", ""))
                if cont:
                    last["summary"] = merge_texts(last.get("summary", ""), cont)
                    st.session_state["last_summary"] = last

        # Export/Copy/Share actions
        st.write("**Actions**")
        st.write(f"**Culture:** {last_culture}")
        st.write(f"**Verbosity:** {st.session_state.get('last_summary_verbosity','')}")

        summary_text = (
            f"Culture: {last_culture}\n\n"
            f"Summary:\n{last.get('summary', '')}\n\n"
            f"Etiquette:\n{last.get('etiquette', '')}\n\n"
            f"Communication Style:\n{last.get('communication_style', '')}\n"
        )

        if PDF_SUPPORTED:
            pdf_bytes = make_pdf_bytes(f"Cultural Summary - {last_culture}", summary_text)
            st.download_button("Download PDF", pdf_bytes, file_name=sanitize_filename(f"{last_culture}_summary.pdf"), mime="application/pdf", key=f"dl_pdf_card_{last_culture}")

        # Share link (placeholder)
        st.button("Share Link (Coming Soon)", key="share_link_btn", disabled=True)
        st.markdown('<hr style="border:none;border-top:2px solid #e0e7ef;margin:32px 0 24px 0;">', unsafe_allow_html=True)

        # show follow-up response if available
        if st.session_state.get("last_followup"):
            st.subheader("💡 Follow-up Response")
            fu = st.session_state.get("last_followup")
            st.write(fu.get("response", fu))
            st.markdown('<hr style="border:none;border-top:2px solid #e0e7ef;margin:32px 0 24px 0;">', unsafe_allow_html=True)

    else:
        st.subheader("No summary yet")
        st.write("Generate a cultural summary on the left. Suggested follow-ups will appear after generation.")

with tab2:
    st.header("Chat with Cultural Persona")

    culture = st.text_input("Culture (for persona):")
    persona = st.text_input("Persona (e.g., Japanese local, Italian chef):")
    user_text = st.text_area("Your message:")
    chat_verbosity = st.selectbox("Reply verbosity", ["concise", "medium", "detailed"], index=1)
    username = "user123"

    if st.button("Chat"):
        if not (culture.strip() and persona.strip() and user_text.strip()):
            st.error("Fill all fields.")
        else:
            with st.spinner("Generating response..."):
                result = crew.chat_as_culture_with_verbosity(culture, persona, user_text, username, verbosity=chat_verbosity)
                # save result to session so UI stays stable on download
                st.session_state["last_chat"] = result
                st.session_state["last_chat_meta"] = {"culture": culture, "persona": persona, "user_text": user_text}
                crew.save_note(username, culture, user_text, result)
                st.success("Note saved!")

    # display last chat and provide download buttons without regenerating
    if st.session_state.get("last_chat") and st.session_state.get("last_chat_meta"):
        last = st.session_state["last_chat"]
        meta = st.session_state["last_chat_meta"]
        st.subheader("Persona Response")
        st.write(last.get("response", ""))

        if _looks_cutoff(last.get("response", "")):
            if st.button("Continue Response", key=f"cont_resp_{meta['culture']}_{meta['persona']}"):
                cont = continue_text(last.get("response", ""))
                if cont:
                    last["response"] = merge_texts(last.get("response", ""), cont)
                    st.session_state["last_chat"] = last

        st.subheader("Etiquette Feedback")
        st.write(last.get("feedback", ""))

        if _looks_cutoff(last.get("feedback", "")):
            if st.button("Continue Feedback", key=f"cont_feed_{meta['culture']}_{meta['persona']}"):
                cont = continue_text(last.get("feedback", ""))
                if cont:
                    last["feedback"] = merge_texts(last.get("feedback", ""), cont)
                    st.session_state["last_chat"] = last

        transcript_text = (
            f"Culture: {meta['culture']}\nPersona: {meta['persona']}\n\nUser:\n{meta['user_text']}\n\nResponse:\n{last.get('response','')}\n\nFeedback:\n{last.get('feedback','')}\n"
        )
        if PDF_SUPPORTED:
            pdf_bytes = make_pdf_bytes(f"Chat - {meta['culture']} - {meta['persona']}", transcript_text)
            st.download_button("Download Chat (PDF)", pdf_bytes, file_name=sanitize_filename(f"{meta['culture']}_{meta['persona']}_chat.pdf"), mime="application/pdf", key=f"dl_chat_pdf_{meta['culture']}_{meta['persona']}")

with tab3:
    st.header("Saved Notes")

    username = "user123"
    notes = crew.get_notes(username)

    if not notes:
        st.info("No notes saved yet.")
    else:
        # button to download all notes as a single text file
        all_text = []
        for n in notes:
            all_text.append(f"Title: {n['title']}\nCulture: {n['culture']}\nSaved: {n['created_at']}\n\n{n['content']}\n\n---\n\n")
        combined = "".join(all_text)
        for n in notes:
            st.subheader(n["title"])
            st.write(f"**Culture:** {n['culture']}")
            st.write(n["content"])
            st.caption(f"Saved on: {n['created_at']}")
            # per-note download
            note_text = f"Title: {n['title']}\nCulture: {n['culture']}\nSaved: {n['created_at']}\n\n{n['content']}"
            st.download_button("Download Note", note_text, file_name=sanitize_filename(f"note_{n['created_at']}.txt"), mime="text/plain")
        # download all notes button (placed after notes to avoid streamlit re-run ordering issues)
        st.download_button("Download All Notes (TXT)", combined, file_name=sanitize_filename("saved_notes.txt"), mime="text/plain", key="dl_all_notes")

    # close main content container
    st.markdown('</div>', unsafe_allow_html=True)
