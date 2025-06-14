
# 🌐 Multilingual Text Converter AI using Google GenAI & Streamlit

This Streamlit app allows users to input English text (4–10 lines or more) and automatically generates:

1. **English in Devanagari script** – Phonetic transliteration (e.g., "How are you?" → "हाउ आर यू?")
2. **Hindi in Devanagari script** – Accurate Hindi translation (e.g., "How are you?" → "आप कैसे हैं?")
3. **Hindi in Roman script** – Romanized version of Hindi (e.g., "Aap kaise hain?")

## 🚀 Live App

👉 [Click here to open the app on Streamlit Cloud](https://your-streamlit-app-url)

## 🛠️ Tech Stack

- **Streamlit** – For interactive web UI
- **Google Generative AI (Gemini)** – For multilingual text generation
- **LangChain** – For managing prompts and LLM interactions

## 📦 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/multilingual-text-converter.git
   cd multilingual-text-converter
````

2. Create a `.env` file and add your Google API key:

   ```
   GOOGLE_API_KEY=your_key_here
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Run the app:

   ```bash
   streamlit run app.py
   ```

## ✨ Features

* Clean UI for input and output display
* Supports long paragraphs
* Uses LLM to understand context and provide high-quality translations
* Fast and easy deployment via Streamlit Cloud

## 📄 License

MIT License

---

### 🔗 Connect

Feel free to fork or contribute. For issues or suggestions, open a GitHub issue.

```
