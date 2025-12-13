# Auto-Report

**Cross-Border E-Commerce Market Analysis Workflow**

Automated market analysis application that processes sales data, user feedback, and product reviews through a 4-stage workflow, culminating in a comprehensive market report generated via multi-LLM debate.

## 🌟 Key Features

- **4-Stage Analysis Workflow**: Market landscape → Comments → Reviews → AI Report
- **Python-Based Data Processing**: All statistics computed deterministically
- **Multi-LLM Debate System**: Two models analyze independently, judge synthesizes
- **Multi-Platform Support**: Amazon & TikTok Shop data analysis
- **Voice of Customer (VOC)**: Extract insights from comments and reviews
- **Interactive Visualizations**: Comprehensive charts and graphs
- **Chinese Report Output**: Final reports in Chinese for cross-border markets

## 📋 Prerequisites

- Python 3.10 or higher
- Streamlit
- API keys for at least one LLM provider (OpenAI, Google Gemini, or DeepSeek)
- (Optional) Reddit API credentials for social media analysis

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/magendary/Auto-Report.git
cd Auto-Report
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Environment Variables

Create a `.env` file or export environment variables:

```bash
# Required: At least one LLM provider
export OPENAI_API_KEY="your-openai-api-key"
export GOOGLE_API_KEY="your-google-api-key"
export DEEPSEEK_API_KEY="your-deepseek-api-key"

# Optional: For Reddit comment fetching
export REDDIT_CLIENT_ID="your-reddit-client-id"
export REDDIT_CLIENT_SECRET="your-reddit-client-secret"
export REDDIT_USER_AGENT="AutoReport/1.0"
```

### 4. Run the Application

```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`

## 📊 Workflow Overview

### Stage 1: Market Landscape (Sales Data)

**Input:**
- Amazon sales data (CSV/XLSX)
- TikTok Shop sales data (CSV/XLSX)

**Expected Columns:**

**Amazon:**
- `asin` or `product_id`: Product identifier
- `title` or `product_title`: Product name
- `price`: Product price
- `sales` or `units_sold`: Number of units sold
- `rating` or `avg_rating`: Average rating (1-5)
- `reviews` or `review_count`: Number of reviews
- `launch_date` (optional): Product launch date
- `category` (optional): Product category
- `seller` (optional): Seller name

**TikTok Shop:**
- `product_id` or `sku`: Product identifier
- `title` or `product_name`: Product name
- `price` or `selling_price`: Product price
- `sales` or `sold`: Number of units sold
- `rating` or `score`: Average rating (1-5)
- `reviews` or `review_count`: Number of reviews
- `shop` or `store_name` (optional): Shop name

**Output:**
- Market overview statistics
- Competition metrics (market concentration, long-tail index)
- Price band analysis
- Feature performance analysis
- Cross-platform comparison

### Stage 2: User Comments Analysis

**Input:**
- TikTok video comments (CSV/XLSX)
- Reddit threads/comments (fetched via API or uploaded)

**Expected Columns:**

**TikTok:**
- `text` or `comment`: Comment text
- `likes` or `like_count`: Number of likes
- `created_at` or `timestamp` (optional): Comment date

**Reddit:**
- `text` or `body`: Comment text
- `upvotes` or `score`: Number of upvotes
- `created_at` (optional): Comment date

**Output:**
- Potential reasons to buy (Top 5)
- Potential reasons not to buy (Top 5)
- Usage scenarios (Top 5)
- User segments (Top 5)

### Stage 3: Product Reviews Analysis

**Input:**
- Amazon product reviews (CSV/XLSX)
- TikTok Shop product reviews (CSV/XLSX)

**Expected Columns:**

**Amazon:**
- `asin` or `product_id`: Product identifier
- `text` or `review_text`: Review text
- `rating` or `star_rating`: Rating (1-5)
- `helpful` or `helpful_votes` (optional): Helpfulness votes
- `date` or `review_date` (optional): Review date
- `verified` or `verified_purchase` (optional): Verified purchase flag

**TikTok:**
- `product_id`: Product identifier
- `text` or `content`: Review text
- `rating` or `score`: Rating (1-5)
- `helpful` or `likes` (optional): Helpfulness count
- `date` or `created_at` (optional): Review date

**Output:**
- Must-have factors (from 4-5 star reviews)
- Critical pitfalls (from 1-2 star reviews)
- Usage scenarios (real usage descriptions)
- Unmet needs (feature requests, complaints)
- Platform comparison

### Stage 4: Multi-Model Debate & Report

**Input:**
- Structured JSON from Stages 1-3

**Process:**
1. Two LLM models independently analyze the data
2. Each produces a comprehensive analysis report in Chinese
3. A judge model reads both reports and synthesizes a final report
4. Final report explicitly mentions agreements, disagreements, and reasoning

**Output:**
- Individual reports from both analyst models
- Final synthesized report in Chinese
- Downloadable markdown and JSON files

## 🏗️ Project Structure

```
Auto-Report/
├── app.py                          # Main Streamlit application
├── data_pipeline/                  # Data processing modules
│   ├── __init__.py
│   ├── clean_amazon_sales.py       # Amazon sales normalization
│   ├── clean_tiktok_sales.py       # TikTok Shop sales normalization
│   ├── comments_tiktok.py          # TikTok comments processing
│   ├── comments_reddit.py          # Reddit comments fetching
│   ├── reviews_amazon.py           # Amazon reviews processing
│   ├── reviews_tiktok.py           # TikTok reviews processing
│   ├── market_statistics.py        # Market landscape statistics
│   └── voc_statistics.py           # VOC statistics computation
├── ai/                             # AI/LLM integration
│   ├── __init__.py
│   ├── llm_clients.py              # LLM provider wrappers
│   ├── debate_orchestrator.py      # Multi-model debate logic
│   └── prompts.py                  # Prompt templates (Chinese)
├── visualization/                  # Visualization utilities
│   ├── __init__.py
│   └── charts.py                   # Chart generation
├── requirements.txt                # Python dependencies
├── .gitignore                      # Git ignore rules
└── README.md                       # This file
```

## 🔧 Configuration

### LLM Providers

The application supports three LLM providers:

1. **OpenAI** (GPT-4, GPT-3.5)
   - Set `OPENAI_API_KEY` environment variable
   - Default model: `gpt-4o-mini`

2. **Google Gemini**
   - Set `GOOGLE_API_KEY` environment variable
   - Default model: `gemini-pro`

3. **DeepSeek**
   - Set `DEEPSEEK_API_KEY` environment variable
   - Default model: `deepseek-chat`

You can choose different providers for each role (Analyst 1, Analyst 2, Judge) in the UI.

### Reddit API (Optional)

To fetch Reddit comments automatically:

1. Create a Reddit app at https://www.reddit.com/prefs/apps
2. Note your client ID, client secret, and choose a user agent
3. Set environment variables as shown in Quick Start

## 📝 Example Workflow

1. **Prepare Your Data**
   - Export Amazon sales data from your analytics dashboard
   - Export TikTok Shop sales data
   - Collect TikTok video comments
   - (Optional) Prepare Reddit keywords for fetching

2. **Run Analysis**
   - Start the Streamlit app
   - Upload Amazon sales data in Stage 1
   - Upload TikTok sales data in Stage 1
   - Click "Compute Market Statistics"
   - Upload TikTok comments in Stage 2
   - (Optional) Fetch or upload Reddit comments
   - Proceed to Stage 3
   - Upload Amazon reviews in Stage 3
   - Upload TikTok reviews in Stage 3
   - Click "Compute VOC Statistics"
   - Proceed to Stage 4

3. **Generate Report**
   - Choose two different LLM providers for analysts
   - Choose a judge provider (can be same as one analyst)
   - Enter API keys if not set in environment
   - Click "Run Multi-Model Debate"
   - Wait for analysis (may take 2-3 minutes)
   - Review individual reports and final synthesized report

4. **Export Results**
   - Download final report as Markdown
   - Download complete analysis as JSON
   - Share visualizations and insights with team

## 🎯 Design Principles

1. **Python for Processing, LLMs for Interpretation**
   - All numeric computations done in Python
   - LLMs only receive structured JSON
   - Minimizes hallucinations and API costs

2. **Deterministic Data Pipeline**
   - Reproducible results
   - Clear data transformations
   - Easy to audit and improve

3. **Multi-Model Debate**
   - Reduces single-model bias
   - Provides multiple perspectives
   - Judge synthesizes best insights

4. **Modular Architecture**
   - Easy to add new data sources
   - Easy to plug in new LLM providers
   - Easy to extend analysis capabilities

## 🛠️ Development

### Adding a New LLM Provider

1. Create a new client class in `ai/llm_clients.py` inheriting from `BaseLLMClient`
2. Implement `generate()` and `get_provider_name()` methods
3. Add provider to `get_llm_client()` factory function
4. Update UI dropdown in `app.py`

### Adding New Analysis Metrics

1. Add computation logic to `data_pipeline/market_statistics.py` or `voc_statistics.py`
2. Update JSON structure returned by computation functions
3. (Optional) Add visualization in `visualization/charts.py`
4. Update UI to display new metrics

### Improving Clustering Algorithms

Comment and review categorization uses heuristic keyword matching. To improve:

1. Implement ML-based clustering in relevant modules
2. Add embedding-based similarity search
3. Use topic modeling (LDA, NMF) for better categorization

## 🐛 Troubleshooting

**Issue: "API key not provided" error**
- Solution: Set environment variables or enter keys in the UI

**Issue: Reddit comments not fetching**
- Solution: Verify Reddit API credentials are correct
- Check that subreddits are not private

**Issue: File upload fails**
- Solution: Ensure file is CSV or XLSX format
- Check that required columns exist in the file

**Issue: LLM generation timeout**
- Solution: Reduce max_tokens parameter
- Try a different LLM provider
- Check your API rate limits

## 📄 License

This project is provided as-is for educational and commercial use.

## 🤝 Contributing

Contributions are welcome! Please feel free to:
- Report bugs
- Suggest new features
- Improve documentation
- Add new data sources or LLM providers

## 📧 Support

For issues and questions, please open a GitHub issue.

---

**Built with ❤️ for cross-border e-commerce entrepreneurs**