"""
Configuration settings for OIC ADEI Analytics Streamlit App
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Try to import streamlit for secrets (only available when running in Streamlit)
try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False

# Helper function to get config value from Streamlit secrets or environment
def get_config_value(streamlit_section, streamlit_key, env_key, default_value):
    """Get configuration value from Streamlit secrets first, then env vars, then default"""
    if HAS_STREAMLIT:
        try:
            if hasattr(st, 'secrets') and streamlit_section in st.secrets:
                return st.secrets[streamlit_section].get(streamlit_key, default_value)
        except:
            pass
    return os.getenv(env_key, default_value)

# Database Configuration
# Prioritizes Streamlit Cloud secrets, falls back to .env, then hardcoded defaults
DATABASE_CONFIG = {
    'host': get_config_value('database', 'host', 'DB_HOST', 
                            'ep-noisy-darkness-adflnyur-pooler.c-2.us-east-1.aws.neon.tech'),
    'port': int(get_config_value('database', 'port', 'DB_PORT', 5432)),
    'database': get_config_value('database', 'database', 'DB_NAME', 'neondb'),
    'username': get_config_value('database', 'user', 'DB_USER', 'neondb_owner'),
    'password': get_config_value('database', 'password', 'DB_PASSWORD', 'npg_mvnKs8P2Vrbd'),
    'sslmode': get_config_value('database', 'sslmode', 'DB_SSL_MODE', 'require')
}

# Application Settings
APP_CONFIG = {
    'cache_ttl': int(os.getenv('CACHE_TTL', 3600)),  # 1 hour default
    'max_countries_comparison': int(os.getenv('MAX_COUNTRIES_COMPARISON', 10)),
    'rag_search_depth': int(os.getenv('RAG_SEARCH_DEPTH', 5)),
    'chart_height': int(os.getenv('CHART_HEIGHT', 400)),
    'page_title': 'OIC ADEI Analytics',
    'page_icon': '📊'
}

# RAG Configuration
RAG_CONFIG = {
    'openai_api_key': get_config_value('openai', 'api_key', 'OPENAI_API_KEY', None),
    'embedding_model': 'sentence-transformers/all-MiniLM-L6-v2',
    'chunk_size': 1000,
    'chunk_overlap': 200,
    'vector_store_type': 'faiss'
}

# Streamlit Configuration
STREAMLIT_CONFIG = {
    'page_title': APP_CONFIG['page_title'],
    'page_icon': APP_CONFIG['page_icon'],
    'layout': 'wide',
    'initial_sidebar_state': 'expanded'
}

# Chart Configuration
CHART_CONFIG = {
    'height': APP_CONFIG['chart_height'],
    'color_palette': [
        '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
        '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
    ],
    'background_color': 'white',
    'grid_color': '#E5E5E5'
}

# Performance Tiers (for categorization)
PERFORMANCE_TIERS = {
    'High': (0.7, 1.0),
    'Medium': (0.5, 0.7), 
    'Low': (0.0, 0.5)
}

# Pillar Names and Descriptions
PILLARS = {
    'adei_economic_opportunities': 'Economic Opportunities',
    'adei_educational_attainment': 'Educational Attainment',
    'adei_health_survival': 'Health & Survival',
    'adei_political_empowerment': 'Political Empowerment',
    'adei_access_land_non_land_assets': 'Access to Assets',
    'adei_access_justice': 'Access to Justice',
    'adei_agency_voice_participation': 'Agency & Participation',
    'adei_time_use_unpaid_care_work': 'Time Use & Care Work'
}

# Countries mapping (if needed for display names)
COUNTRY_DISPLAY_NAMES = {
    # Add any country name mappings here if needed
    # 'country_code': 'Display Name'
}

# Default query examples for RAG search
DEFAULT_RAG_QUERIES = [
    "Which countries have the highest ADEI scores?",
    "What are the trends in educational attainment across OIC countries?", 
    "How does economic opportunities pillar correlate with overall ADEI scores?",
    "Which countries showed the most improvement from 2021 to 2023?",
    "What are the main challenges in political empowerment pillar?",
    "Compare the performance of Turkey, Indonesia, and Malaysia",
    "What factors contribute to high health and survival scores?",
    "Which regions perform best in access to justice?"
]