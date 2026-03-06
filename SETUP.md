# Setup Guide - Gemini Math Mentor

## Quick Start

### 1. Get Your Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
2. Click "Get API Key" or "Create API Key"
3. Copy your API key

### 2. Configure the Project

Edit the `.env` file and add your API key:

```bash
GEMINI_API_KEY=your-actual-api-key-here
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Test the API Connection

```bash
python test_gemini.py
```

You should see:
- ✓ API key loaded
- List of available models
- ✓ Test response
- ✅ Gemini API is working correctly!

### 5. Build the RAG Index (Optional but Recommended)

Run the app and click "Build RAG Index" in the sidebar:

```bash
streamlit run app.py
```

Or build it from command line:

```bash
python rag.py YOUR_API_KEY
```

### 6. Start Using the App

```bash
streamlit run app.py
```

Open http://localhost:8501 in your browser.

## Troubleshooting

### "GEMINI_API_KEY not found"
- Make sure you created the `.env` file from `.env.example`
- Make sure you added your actual API key (not the placeholder text)
- The `.env` file should be in the same directory as `app.py`

### "Model not found" errors
- The code uses `gemini-2.5-flash` which is the latest model
- If this model is not available, you can change it to `gemini-2.0-flash-exp`, `gemini-1.5-flash` or `gemini-1.5-pro`
- Edit the model name in `agents.py` in the `call_gemini()` function

### Import errors
- Make sure you installed the new `google-genai` package (not the deprecated `google-generativeai`)
- Run: `pip install google-genai`

## Features

- ✅ Text input - Type math problems directly
- ✅ Image input - Upload photos of math problems (Gemini Vision)
- ✅ Audio input - Upload audio recordings (uses Whisper fallback)
- ✅ 5-Agent Pipeline - Parser → Router → Solver → Verifier → Explainer
- ✅ RAG - FAISS vector search with Gemini embeddings
- ✅ Memory - SQLite database tracks all problems and feedback
- ✅ HITL - Human-in-the-loop for low confidence answers

## Next Steps

1. Try solving a simple problem: "Solve: 2x² - 5x + 3 = 0"
2. Upload an image of a math problem
3. Check the agent trace to see how it works
4. Provide feedback to improve the memory system
