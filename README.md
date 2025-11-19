## AI Culture Companion

### Overview
AI Culture Companion is a Streamlit web app that provides instant, actionable cultural briefings for any country or culture. It helps users learn etiquette, communication styles, social norms, and must-know tips—ideal for travelers, professionals, and anyone working cross-culturally.

---

### Features
- Generate cultural summaries using AI (Google Gemini API)
- Custom verbosity and section selection (Summary, Etiquette, Communication Style)
- Dynamic, place-specific resource links (Google Custom Search API)
- Personalized recommendations and common mistakes
- Persona chat for interactive Q&A
- Save notes and export content as PDF or text
- Clean, modern, and aesthetic UI

---

### Technical Stack
- **Frontend/UI:** Streamlit, custom CSS
- **Backend/Logic:** Google Gemini API, Google Custom Search API
- **Python Modules:**
	- `app.py` (main UI and logic)
	- `crew_wrapper.py` (agent orchestration, resource fetching)
	- `agents.py` (summary, chat, recommendations logic)
	- `utils.py` (environment loading, API helpers)
- **Export:** ReportLab for PDF generation
- **Environment:** `.env` file for API keys and configuration

---

### Setup & Installation
1. Clone the repository and navigate to the project folder.
2. Install dependencies:
	 ```
	 pip install -r requirements.txt
	 ```
3. Add your API keys to a `.env` file:
	 - `GOOGLE_GEMINI_API_KEY=...`
	 - `GOOGLE_CSE_ID=...`
	 - `GOOGLE_API_KEY=...`
4. Start the app:
	 ```
	 streamlit run app.py
	 ```

---

### Usage
1. Use the sidebar to enter a culture/country and select verbosity.
2. Click "Generate Summary" to view cultural briefings.
3. Explore etiquette, communication style, recommendations, and resources.
4. Chat with a local persona in the Persona Chat tab.
5. Save and download notes in the Your Notes tab.
6. Export summaries and chats as PDF or text files.

---

### Architecture & Flow
- **Summary Generation:**
	- User input triggers Gemini API via `agents.py`.
	- Prompt built based on verbosity and sections.
	- Response parsed and displayed in UI.
- **Resource Links:**
	- Google Custom Search API fetches relevant resources.
- **Recommendations:**
	- AI generates tips and common mistakes.
- **Persona Chat:**
	- Simulates local expert responses.
- **Export:**
	- PDF (ReportLab) and TXT downloads.

---

### Extensibility
- Modular codebase for easy feature addition and maintenance.

---

### Demo Scenario
1. Enter "Japan" in the sidebar.
2. Select "custom" verbosity and choose "Summary" and "Etiquette".
3. Click "Generate Summary".
4. Review the summary, etiquette tips, recommendations, and resources.
5. Chat with a "Japanese local" in the Persona Chat tab.
6. Save and download notes.

---

### License
MIT License
