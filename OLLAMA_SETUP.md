# Local LLM Setup with Ollama

This guide shows you how to run the Pitch Deck Analyzer completely offline using Ollama.

## Why Use Local LLM?

✅ **Privacy**: Your data never leaves your machine  
✅ **Cost**: No API fees  
✅ **Speed**: No network latency  
✅ **Offline**: Works without internet  

## Installation

### Step 1: Install Ollama

**Windows:**
1. Download from https://ollama.com/download/windows
2. Run the installer
3. Ollama will start automatically

**Mac:**
```bash
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Step 2: Download a Model

Open terminal and run:

```bash
# Recommended: Llama 3.1 8B (Best balance of speed and quality)
ollama pull llama3.1:8b

# Alternative options:
ollama pull llama3.1:70b    # Better quality, slower
ollama pull mistral:7b      # Faster, good quality
ollama pull qwen2.5:14b     # Excellent for structured output
```

### Step 3: Verify Installation

```bash
ollama list
```

You should see your downloaded models.

### Step 4: Configure the Application

Edit your `.env` file:

```env
# Change from gemini to ollama
LLM_PROVIDER=ollama

# Ollama settings
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
```

### Step 5: Restart the Backend

```bash
python -m uvicorn app.main:app --reload
```

## Recommended Models

| Model | Size | Speed | Quality | Use Case |
|-------|------|-------|---------|----------|
| llama3.1:8b | 4.7GB | Fast | Good | Recommended for most users |
| llama3.1:70b | 40GB | Slow | Excellent | Best quality, needs powerful GPU |
| mistral:7b | 4.1GB | Very Fast | Good | Quick processing |
| qwen2.5:14b | 9GB | Medium | Excellent | Best for structured extraction |

## Performance Tips

1. **GPU Acceleration**: Ollama automatically uses your GPU if available
2. **RAM**: Ensure you have enough RAM (8GB minimum, 16GB+ recommended)
3. **Model Size**: Start with 8B models, upgrade to 70B if you have the hardware

## Switching Back to Gemini

Edit `.env`:
```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_api_key_here
```

## Troubleshooting

**Ollama not responding:**
```bash
# Check if Ollama is running
ollama list

# Restart Ollama service
# Windows: Restart from system tray
# Mac/Linux: 
ollama serve
```

**Model not found:**
```bash
ollama pull llama3.1:8b
```

**Slow processing:**
- Use a smaller model (mistral:7b)
- Ensure GPU drivers are updated
- Close other applications

## Hybrid Mode (Coming Soon)

Use Ollama for classification and Gemini for extraction to balance cost and quality.
