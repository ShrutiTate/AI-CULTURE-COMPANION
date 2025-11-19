# 🌍 AI Culture Companion

An AI-powered Streamlit application that delivers **instant, actionable cultural briefings** for any country or region. Learn etiquette, communication styles, social norms, and cultural do’s & don’ts—perfect for **travelers, professionals, students, and global teams.**

---

## 🚀 Features

✨ **AI-Powered Cultural Insights**  
Generate cultural summaries using Google Gemini API with personalized depth and verbosity.

🗂️ **Customizable Section Selection**  
Choose what to view — Summary, Etiquette, Communication Style, Recommendations, and more.

🔍 **Dynamic Resource Links**  
Fetch real and recent articles, guides, and travel content using Google Custom Search API.

🤖 **Persona Chat**  
Chat interactively with an AI that behaves like a local expert from that culture.

📝 **Save Notes & Export**  
Save generated summaries, chat responses, and export as **PDF or text**.

🎨 **Modern, Aesthetic UI**  
Clean, minimal, and user-friendly interface built with Streamlit and custom CSS.

---

## 🏗️ Tech Stack

| Category | Technologies |
|----------|--------------|
| Frontend/UI | Streamlit, Custom CSS |
| AI & NLP | Google Gemini API |
| Search & Resources | Google Custom Search API |
| PDF Export | ReportLab |
| Language | Python |
| Environment Management | `.env` file, dotenv |
| Architecture | Modular (Agents, UI, Utils, Orchestration) |

---

## 📁 Project Structure

ai-culture-companion/    
│── app.py # Main UI and Streamlit logic    
│── agents.py # AI response generation logic       
│── crew_wrapper.py # Agent orchestration & API communication       
│── utils.py # Helpers: API loading, formatting    
│── requirements.txt # Dependencies    
│── .env # API keys (ignored in Git)    
│── .gitignore # Ignored environments & sensitive files    
│── README.md # Project documentation    

---

## ⚙️ Setup & Installation

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/<username>/AI-CULTURE-COMPANION.git
cd AI-CULTURE-COMPANION
```
2️⃣ Install Dependencies
```
pip install -r requirements.txt
```
3️⃣ Create .env file
Add your API keys:
GOOGLE_GEMINI_API_KEY=your_gemini_key_here    
GOOGLE_CSE_ID=your_custom_search_engine_id    
GOOGLE_API_KEY=your_google_api_key    

4️⃣ Start the App
```
streamlit run app.py
```

💡 How It Works    
flowchart TD    
    A[User Input Country] --> B[Prompt Builder]    
    B --> C[Google Gemini API]    
    C --> D[Generate Cultural Summary]    
    D --> E[Streamlit UI Display]    
    G[Google Custom Search API] --> E    
    E --> F[PDF / Text Export]    
    E --> H[Persona Chat Module]    
        


🧭 Usage Guide    
✔ Enter any country or culture    
✔ Choose verbosity (Short, Medium, Detailed, Custom)    
✔ Select sections (Summary, Etiquette, Communication Style, Tips, Resources…)    
✔ Click Generate Summary    
✔ Explore local insights, mistakes, recommendations    
✔ Start a chat with a local persona    
✔ Save, export, or share as PDF/TXT    

🎯 Demo Scenario Example    

🗾 Enter Japan
Select Custom -> Summary + Etiquette
Click Generate    
✨ View greeting customs, bowing etiquette, communication style, gift-giving traditions, links, and chat with a Japanese persona.


🔧 Extensibility Ideas    
🔹 Voice-based input using Speech-to-Text    
🔹 Live translation using Google Translate API    
🔹 Cultural comparisons (e.g., India vs Japan)    
🔹 Travel itinerary assistance    
🔹 Multilingual interface support    

🤝 Contributing
Contributions are welcome!
fork → clone → branch → commit → push → pull request


📜 License
Licensed under the MIT License — feel free to use and modify.

⭐ Support
If you like this project, please consider giving it a ⭐ star on GitHub!


---

Let me know if you want:

🎨 A GitHub banner/header image  
🚀 Deployment to Streamlit Cloud / HuggingFace  
📄 Add badges (API used, license, built with)  
🛠️ Add CONTRIBUTING.md or LICENSE file  

🚀 Ready to paste!
