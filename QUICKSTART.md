# Quick Start Guide

Get started with Auto-Report in 5 minutes!

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Set Up API Keys

Choose one of these methods:

### Option A: Environment Variables (Recommended)

```bash
# For OpenAI
export OPENAI_API_KEY="your-openai-api-key-here"

# For Google Gemini
export GOOGLE_API_KEY="your-google-api-key-here"

# For DeepSeek
export DEEPSEEK_API_KEY="your-deepseek-api-key-here"
```

### Option B: .env File

Create a `.env` file in the project root:

```
OPENAI_API_KEY=your-openai-api-key-here
GOOGLE_API_KEY=your-google-api-key-here
DEEPSEEK_API_KEY=your-deepseek-api-key-here
```

### Option C: Enter in UI

You can also enter API keys directly in the application UI (Stage 4).

## Step 3: Launch the Application

```bash
streamlit run app.py
```

The application will open automatically in your browser at `http://localhost:8501`

## Step 4: Try with Example Data

The repository includes example data files in the `examples/` directory. Use these to test the application:

### Stage 1: Market Landscape
1. Click "Browse files" under "Amazon Sales Data"
2. Select `examples/amazon_sales_example.csv`
3. Click "Browse files" under "TikTok Shop Sales Data"
4. Select `examples/tiktok_sales_example.csv`
5. Click "🔬 Compute Market Statistics"

### Stage 2: Comments Analysis
1. The sidebar will show Stage 2 is now active
2. Click "Browse files" under "TikTok Comments"
3. Select `examples/tiktok_comments_example.csv`
4. Click "Next: Product Reviews"

### Stage 3: Reviews Analysis
1. Click "Browse files" under "Amazon Reviews"
2. Select `examples/amazon_reviews_example.csv`
3. Click "🔬 Compute VOC Statistics"

### Stage 4: Generate Report
1. Select two different LLM providers (e.g., OpenAI and Gemini)
2. Enter your API keys (if not set in environment)
3. Click "🚀 Run Multi-Model Debate"
4. Wait 2-3 minutes for the analysis
5. View the final report and download results

## Step 5: Use Your Own Data

Replace the example files with your own data:

1. **Sales Data**: Export from your Amazon Seller Central or TikTok Shop Seller Center
2. **Comments**: Scrape TikTok video comments or use Reddit API
3. **Reviews**: Export product reviews from Amazon or TikTok Shop

Make sure your files include the required columns (see README.md for details).

## Common Issues

### "API key not provided" Error
- Make sure you've set the environment variable correctly
- Or enter the key in the UI
- Check for typos in the key

### "Column not found" Error
- Your data file is missing required columns
- Check the example files for the correct structure
- The app will auto-detect common column name variations

### Streamlit Won't Start
- Make sure port 8501 is not in use
- Try: `streamlit run app.py --server.port=8502`

### Slow Performance
- Reduce the `max_tokens` parameter in Stage 4
- Use a faster LLM model (e.g., gpt-3.5-turbo instead of gpt-4)
- Process smaller data files

## Tips for Best Results

1. **Clean Data First**: Remove duplicates and invalid entries before uploading
2. **Use Recent Data**: More recent data provides more relevant insights
3. **Include Multiple Data Sources**: Combining Amazon and TikTok gives better cross-platform insights
4. **Choose Diverse LLMs**: Using different providers (e.g., OpenAI + Gemini) provides more balanced analysis
5. **Review Intermediate Results**: Check the data preview after each upload to ensure correct parsing

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore the code to understand the analysis methodology
- Customize the heuristics in `data_pipeline/` for your specific niche
- Add your own LLM providers in `ai/llm_clients.py`

## Need Help?

- Check the [README.md](README.md) for detailed documentation
- Open an issue on GitHub for bugs or feature requests
- Review the example data files to understand expected formats

---

**Happy Analyzing! 🚀**
