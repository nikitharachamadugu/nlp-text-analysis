# TextPulse NLP - Text & Sentiment Analysis App

A modern, production-grade Natural Language Processing (NLP) web application built with **Python Flask** and **Vanilla CSS/JavaScript**, specifically optimized for lightweight, high-performance deployment on **Render.com**.

---

## 🌟 Key Features

- **🎭 Sentiment & Tone Analysis:**
  - Polarity scoring (-1.0 to +1.0) and Subjectivity percentage.
  - Emotion / Mood classifications (Joyful, Optimistic, Critical, Neutral).
  - Sentence-by-sentence sentiment timeline highlighting emotional shifts.

- **📊 Readability & Lexical Metrics:**
  - Flesch Reading Ease score with visual difficulty meter.
  - Flesch-Kincaid Grade Level, Coleman-Liau Index, and Automated Readability Index (ARI).
  - Estimated reading and speaking times.

- **🏷️ Keywords & Part-of-Speech (POS):**
  - Meaningful keyword extraction with stopword removal.
  - Interactive Doughnut Chart for POS distribution (Nouns, Verbs, Adjectives, Adverbs).

- **💡 Extractive Summarization & Entity Extraction:**
  - Significance-based extractive summary.
  - Automatic detection of URLs, emails, phone numbers, hashtags, and named entities.

- **🚀 Render Free Tier Optimized:**
  - Low memory footprint (< 150MB RAM, well within Render's 512MB free tier limit).
  - Self-contained NLP algorithms with graceful fallbacks to guarantee 100% uptime without crashes.

---

## 🚀 Deploying on Render (Step-by-Step)

In your Render Dashboard (**New Web Service**), configure the fields exactly as follows:

| Setting | Value to Enter |
| :--- | :--- |
| **Language** | `Python 3` |
| **Branch** | `main` |
| **Region** | `Singapore` *(or your preferred region)* |
| **Root Directory** | *(Leave blank)* |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app:app` |
| **Instance Type** | `Free` ($0/month, 512 MB RAM) |

Then click **Deploy Web Service**. Render will automatically build the dependencies and launch your web app.

---

## 💻 Local Development

1. **Clone the repository:**
   ```bash
   git clone https://github.com/nikitharachamadugu/nlp-text-analysis.git
   cd nlp-text-analysis
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the development server:**
   ```bash
   python app.py
   ```
   Open [http://localhost:5000](http://localhost:5000) in your browser.

---

## 🔌 REST API Usage

You can also use this app as a headless API service:

```bash
curl -X POST https://your-app-name.onrender.com/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "The deployment went smoothly and the performance was fantastic!"}'
```