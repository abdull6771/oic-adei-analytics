# 🌍 OIC ADEI Analytics Dashboard

A comprehensive Streamlit web application for analyzing the Organization of Islamic Cooperation (OIC) Artificial Intelligence for Development and Emerging Indexes (ADEI) dataset from 2021-2025.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-url.streamlit.app)

## 🎯 Features

### 📊 **Executive Dashboard**

- Key metrics and performance indicators
- Top performers visualization
- Performance distribution analysis
- Global trends tracking
- Year-over-year improvements

### 📈 **Pillar Analysis**

- 8 Development Pillars:
  - Governance & Regulatory Framework
  - Technology Infrastructure & Digital Access
  - Education & Human Capital
  - Digital Government Services
  - Innovation & R&D
  - Emerging Technology Adoption
  - Economic & Financial Infrastructure
  - SDG Achievement
- Radar charts, correlation heatmaps, and comparative analysis

### 🔄 **Country Comparison**

- Multi-country, multi-year comparisons
- Side-by-side performance analysis
- Trend visualization
- Export functionality

### 🗺️ **Geographic Analysis**

- Interactive world choropleth maps
- Regional analysis (Middle East, Africa, Asia, Europe)
- Geographic neighbor comparisons
- Regional performance trends

### 🔍 **RAG Search**

- Natural language question answering
- Contextual search with intelligent ranking
- Query type detection (top/bottom performers, comparisons, trends)
- Interactive data exploration

### 📉 **Trends Analysis**

- Historical performance tracking
- Improvement analysis
- Variability metrics
- Time series visualization

## 🚀 Quick Start

### Local Development

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/oic-adei-analytics.git
cd oic-adei-analytics
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Set up environment variables**

```bash
cp .env.example .env
# Edit .env with your database credentials
```

4. **Run the app**

```bash
streamlit run streamlit_app.py
```

The app will open in your browser at `http://localhost:8501`

## ☁️ Deploy to Streamlit Cloud

### Prerequisites

- GitHub account
- Streamlit Cloud account (free at [share.streamlit.io](https://share.streamlit.io))
- PostgreSQL database with OIC ADEI data

### Deployment Steps

1. **Push code to GitHub**

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/oic-adei-analytics.git
git push -u origin main
```

2. **Deploy on Streamlit Cloud**

   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Select your repository: `yourusername/oic-adei-analytics`
   - Set main file path: `streamlit_app.py`
   - Click "Advanced settings" to add secrets

3. **Configure Secrets**

In Streamlit Cloud, add these secrets (Settings → Secrets):

```toml
# Database Configuration
[database]
host = "your-database-host.neon.tech"
port = 5432
database = "neondb"
user = "your_username"
password = "your_password"
sslmode = "require"

# Optional: OpenAI for enhanced RAG
[openai]
api_key = "your-openai-api-key"
```

4. **Deploy!**
   - Click "Deploy"
   - Wait 2-3 minutes for deployment
   - Your app will be live at `https://your-app-name.streamlit.app`

## 🗄️ Database Setup

This app requires a PostgreSQL database with the OIC ADEI dataset.

### Using Neon (Free PostgreSQL)

1. Sign up at [neon.tech](https://neon.tech)
2. Create a new project
3. Import your data:

```bash
psql "postgresql://user:password@host/database?sslmode=require" < oic_adei_data.sql
```

### Database Schema

Required table: `oic_adei_data`

Key columns:

- `country` (varchar)
- `year` (integer)
- `adei_score` (decimal)
- Pillar scores and indicators

## 📦 Dependencies

Main technologies:

- **Streamlit** - Web framework
- **Plotly** - Interactive visualizations
- **PostgreSQL** - Database
- **Pandas** - Data manipulation
- **LangChain** - RAG functionality (optional)
- **FAISS** - Vector search (optional)

Full list in [`requirements.txt`](requirements.txt)

## 🔧 Configuration

### Environment Variables

Create a `.env` file (see `.env.example`):

```env
# Database
DB_HOST=your-host.neon.tech
DB_PORT=5432
DB_NAME=neondb
DB_USER=username
DB_PASSWORD=password
DB_SSL_MODE=require

# Optional
OPENAI_API_KEY=sk-...
```

### App Configuration

Edit `config.py` to customize:

- Cache duration
- Chart dimensions
- RAG search parameters
- Performance settings

## 🧪 Testing

Run tests locally:

```bash
# All tests
pytest tests/ -v

# Specific test
pytest tests/test_app.py::test_database_connection -v
```

## 📊 Data Sources

- **Dataset**: OIC ADEI Data 2021-2025
- **Countries**: 57 OIC member states
- **Time Period**: 2021-2025
- **Indicators**: 8 major pillars with multiple sub-indicators

## 🎨 Screenshots

### Executive Dashboard

![Executive Dashboard](docs/screenshots/dashboard.png)

### Geographic Analysis

![Geographic Map](docs/screenshots/geographic.png)

### Country Comparison

![Country Comparison](docs/screenshots/comparison.png)

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OIC** - Organization of Islamic Cooperation
- **Neon** - Free PostgreSQL hosting
- **Streamlit** - Open-source app framework

## 📧 Contact

For questions or support:

- Open an issue on GitHub
- Email: your.email@example.com

## 🔗 Links

- [Live Demo](https://your-app.streamlit.app)
- [Documentation](docs/)
- [Issues](https://github.com/yourusername/oic-adei-analytics/issues)
- [Streamlit Docs](https://docs.streamlit.io)

---

Made with ❤️ using [Streamlit](https://streamlit.io)
