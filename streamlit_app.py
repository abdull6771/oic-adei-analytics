# OIC ADEI Analytics - Streamlit App
# ==================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import psycopg2
from sqlalchemy import create_engine
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="OIC ADEI Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem;
    }
    .metric-number {
        font-size: 2rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #666;
        margin-top: 0.5rem;
    }
    .sidebar-header {
        font-size: 1.2rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Database connection configuration
@st.cache_resource
def init_connection():
    """Initialize database connection"""
    try:
        # Neon PostgreSQL connection
        connection_string = "postgresql://neondb_owner:npg_mvnKs8P2Vrbd@ep-noisy-darkness-adflnyur-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require"
        engine = create_engine(connection_string)
        return engine
    except Exception as e:
        st.error(f"Database connection failed: {str(e)}")
        return None

# Load data functions
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_data():
    """Load all data from database"""
    engine = init_connection()
    if engine is None:
        return None
    
    try:
        # Main dataset
        query = """
        SELECT * FROM oic_adei_data 
        ORDER BY country, year
        """
        df = pd.read_sql(query, engine)
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

def get_countries():
    """Get list of unique countries from data"""
    df = load_data()
    if df is not None:
        return sorted(df['country'].unique().tolist())
    return []

def get_years():
    """Get list of unique years from data"""
    df = load_data()
    if df is not None:
        return sorted(df['year'].unique().tolist())
    return []

@st.cache_data(ttl=3600)
def load_country_summary():
    """Load country summary view"""
    engine = init_connection()
    if engine is None:
        return None
    
    try:
        query = "SELECT * FROM oic_adei_data_country_summary ORDER BY avg_adei_score DESC"
        df = pd.read_sql(query, engine)
        return df
    except Exception as e:
        st.error(f"Error loading country summary: {str(e)}")
        return None

@st.cache_data(ttl=3600)
def load_latest_data():
    """Load latest year data"""
    engine = init_connection()
    if engine is None:
        return None
    
    try:
        query = "SELECT * FROM oic_adei_data_latest"
        df = pd.read_sql(query, engine)
        return df
    except Exception as e:
        st.error(f"Error loading latest data: {str(e)}")
        return None

@st.cache_data(ttl=3600)
def load_trends_data():
    """Load year-over-year trends"""
    engine = init_connection()
    if engine is None:
        return None
    
    try:
        query = "SELECT * FROM oic_adei_data_yoy_trends ORDER BY year"
        df = pd.read_sql(query, engine)
        return df
    except Exception as e:
        st.error(f"Error loading trends data: {str(e)}")
        return None

# Utility functions
def create_metric_card(value, label, delta=None):
    """Create a metric display card"""
    if delta:
        delta_color = "normal" if delta >= 0 else "inverse"
        st.metric(label=label, value=value, delta=delta, delta_color=delta_color)
    else:
        st.metric(label=label, value=value)

def get_color_palette():
    """Get consistent color palette for charts"""
    return px.colors.qualitative.Set3

# Main dashboard functions
def show_executive_dashboard():
    """Executive Overview Dashboard"""
    st.markdown('<div class="main-header">📊 Executive Overview</div>', unsafe_allow_html=True)
    
    # Load data
    df = load_data()
    latest_df = load_latest_data()
    trends_df = load_trends_data()
    
    if df is None or latest_df is None:
        st.error("Unable to load data. Please check database connection.")
        return
    
    # Key metrics row
    st.markdown("### 📈 Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_countries = df['country'].nunique()
        create_metric_card(total_countries, "Total Countries")
    
    with col2:
        total_records = len(df)
        create_metric_card(total_records, "Total Records")
    
    with col3:
        year_range = f"{df['year'].min()}-{df['year'].max()}"
        st.metric("Time Period", year_range)
    
    with col4:
        avg_score_2025 = latest_df['adei_score'].mean()
        create_metric_card(f"{avg_score_2025:.1f}", "Avg ADEI Score 2025")
    
    st.divider()
    
    # Main visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏆 Top 10 Performers (2025)")
        top_10 = latest_df.nlargest(10, 'adei_score')
        
        fig = px.bar(
            top_10, 
            x='adei_score', 
            y='country',
            orientation='h',
            title="Top 10 Countries by ADEI Score",
            color='adei_score',
            color_continuous_scale='Blues'
        )
        fig.update_layout(height=400, yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 📊 Performance Distribution (2025)")
        
        # Performance tier distribution
        tier_counts = latest_df['performance_tier'].value_counts()
        
        fig = px.pie(
            values=tier_counts.values,
            names=tier_counts.index,
            title="Countries by Performance Tier",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Global trends
    st.markdown("### 📈 Global ADEI Trends (2021-2025)")
    
    if trends_df is not None and not trends_df.empty:
        fig = px.line(
            trends_df,
            x='year',
            y='avg_adei_score',
            title="Average ADEI Score Evolution",
            markers=True
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    # Additional insights
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎯 Top Improvers")
        
        # Calculate improvement for countries with data in both 2021 and 2025
        improvement_data = df[df['year'].isin([2021, 2025])].groupby('country').agg({
            'adei_score': ['first', 'last'],
            'year': 'count'
        }).reset_index()
        
        improvement_data.columns = ['country', 'score_2021', 'score_2025', 'data_points']
        improvement_data = improvement_data[improvement_data['data_points'] == 2]
        improvement_data['improvement'] = improvement_data['score_2025'] - improvement_data['score_2021']
        
        top_improvers = improvement_data.nlargest(5, 'improvement')
        
        if not top_improvers.empty:
            fig = px.bar(
                top_improvers,
                x='improvement',
                y='country',
                orientation='h',
                title="Biggest Improvers (2021-2025)",
                color='improvement',
                color_continuous_scale='Greens'
            )
            fig.update_layout(height=300, yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 🎲 Performance Variability")
        
        # Countries with most/least consistent performance
        country_summary = load_country_summary()
        if country_summary is not None:
            variability_data = country_summary.nsmallest(10, 'adei_volatility')
            
            fig = px.scatter(
                variability_data,
                x='avg_adei_score',
                y='adei_volatility',
                size='max_adei_score',
                hover_data=['country'],
                title="Performance vs Consistency",
                labels={
                    'avg_adei_score': 'Average ADEI Score',
                    'adei_volatility': 'Score Volatility'
                }
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)

def show_pillar_analysis():
    """Pillar Performance Analysis Dashboard"""
    st.markdown('<div class="main-header">🏛️ Pillar Performance Analysis</div>', unsafe_allow_html=True)
    
    df = load_data()
    latest_df = load_latest_data()
    
    if df is None:
        st.error("Unable to load data.")
        return
    
    # Pillar comparison for top countries
    st.markdown("### 🏆 Top 5 Countries - Pillar Comparison")
    
    # Get top 5 countries
    top_5_countries = latest_df.nlargest(5, 'adei_score')['country'].tolist()
    
    # Select pillar scores for comparison
    pillar_columns = [
        'governance_score', 'technology_infrastructure_score', 'education_score',
        'digital_government_score', 'innovation_score', 'emerging_tech_score',
        'economic_infrastructure_score', 'financial_inclusion_score'
    ]
    
    pillar_labels = [
        'Governance', 'Technology Infrastructure', 'Education',
        'Digital Government', 'Innovation', 'Emerging Tech',
        'Economic Infrastructure', 'Financial Inclusion'
    ]
    
    # Create comparison data
    comparison_data = []
    for country in top_5_countries:
        country_data = latest_df[latest_df['country'] == country].iloc[0]
        for col, label in zip(pillar_columns, pillar_labels):
            if pd.notna(country_data[col]):
                comparison_data.append({
                    'Country': country,
                    'Pillar': label,
                    'Score': country_data[col]
                })
    
    comparison_df = pd.DataFrame(comparison_data)
    
    if not comparison_df.empty:
        fig = px.bar(
            comparison_df,
            x='Pillar',
            y='Score',
            color='Country',
            title="Pillar Performance Comparison - Top 5 Countries",
            barmode='group',
            height=500
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    # Individual pillar analysis
    st.markdown("### 📊 Individual Pillar Analysis")
    
    selected_pillar = st.selectbox(
        "Select a pillar for detailed analysis:",
        options=list(zip(pillar_columns, pillar_labels)),
        format_func=lambda x: x[1]
    )
    
    pillar_col, pillar_name = selected_pillar
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top performers in selected pillar
        pillar_data = latest_df[['country', pillar_col]].dropna()
        top_pillar = pillar_data.nlargest(10, pillar_col)
        
        fig = px.bar(
            top_pillar,
            x=pillar_col,
            y='country',
            orientation='h',
            title=f"Top 10 in {pillar_name}",
            color=pillar_col,
            color_continuous_scale='Viridis'
        )
        fig.update_layout(height=400, yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Pillar score distribution
        fig = px.histogram(
            pillar_data,
            x=pillar_col,
            nbins=20,
            title=f"{pillar_name} Score Distribution",
            labels={pillar_col: f"{pillar_name} Score"}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Correlation analysis
    st.markdown("### 🔗 Pillar Correlation Analysis")
    
    # Calculate correlation matrix
    correlation_data = latest_df[pillar_columns].corr()
    
    fig = px.imshow(
        correlation_data,
        labels=dict(x="Pillar", y="Pillar", color="Correlation"),
        x=pillar_labels,
        y=pillar_labels,
        title="Pillar Correlation Matrix",
        color_continuous_scale='RdBu',
        aspect="auto"
    )
    fig.update_layout(height=600)
    st.plotly_chart(fig, use_container_width=True)

# Navigation
def main():
    """Main application"""
    st.sidebar.markdown('<div class="sidebar-header">🌍 OIC ADEI Analytics</div>', unsafe_allow_html=True)
    
    # Navigation
    page = st.sidebar.radio(
        "Navigate to:",
        ["📊 Executive Dashboard", "🏛️ Pillar Analysis", "🌍 Country Comparison", "�️ Geographic Analysis", "�🔍 RAG Search", "📈 Trends Analysis"]
    )
    
    # Database connection status
    engine = init_connection()
    if engine:
        st.sidebar.success("✅ Database Connected")
    else:
        st.sidebar.error("❌ Database Connection Failed")
    
    # Page routing
    if page == "📊 Executive Dashboard":
        show_executive_dashboard()
    elif page == "🏛️ Pillar Analysis":
        show_pillar_analysis()
    elif page == "🌍 Country Comparison":
        # Import and show country comparison
        try:
            from country_comparison import show_country_comparison
            df = load_data()
            show_country_comparison(df)
        except ImportError:
            st.error("Country comparison module not available. Please ensure all files are present.")
    elif page == "�️ Geographic Analysis":
        # Import and show geographic analysis
        try:
            from geographic_analysis import show_geographic_analysis
            df = load_data()
            show_geographic_analysis(df)
        except ImportError:
            st.error("Geographic analysis module not available. Please ensure all files are present.")
    elif page == "�🔍 RAG Search":
        # Import and show RAG search
        try:
            from rag_search import show_rag_search
            df = load_data()
            show_rag_search(df)
        except ImportError:
            st.error("RAG search module not available. Please install LangChain dependencies.")
    elif page == "📈 Trends Analysis":
        show_trends_analysis()
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Data Source:** OIC ADEI 2021-2025")
    st.sidebar.markdown(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")

def show_trends_analysis():
    """Comprehensive Trends Analysis Dashboard"""
    st.markdown('<div class="main-header">📈 Trends Analysis</div>', unsafe_allow_html=True)
    
    df = load_data()
    if df is None:
        st.error("Unable to load data.")
        return
    
    # Year-over-year analysis
    st.markdown("### 📊 Year-over-Year Global Trends")
    
    # Global average trends
    yearly_trends = df.groupby('year').agg({
        'adei_score': ['mean', 'median', 'std'],
        'governance_score': 'mean',
        'technology_infrastructure_score': 'mean',
        'innovation_score': 'mean',
        'country': 'count'
    }).round(2)
    
    yearly_trends.columns = ['Avg_ADEI', 'Median_ADEI', 'Std_ADEI', 'Avg_Governance', 'Avg_Technology', 'Avg_Innovation', 'Countries']
    yearly_trends = yearly_trends.reset_index()
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.line(
            yearly_trends,
            x='year',
            y=['Avg_ADEI', 'Avg_Governance', 'Avg_Technology', 'Avg_Innovation'],
            title="Average Scores Evolution",
            markers=True
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(
            yearly_trends,
            x='year',
            y='Std_ADEI',
            title="ADEI Score Variability by Year",
            color='Std_ADEI',
            color_continuous_scale='Reds'
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Individual country trends
    st.markdown("### 🌍 Individual Country Trends")
    
    # Country selection for trend analysis
    selected_countries = st.multiselect(
        "Select countries for trend analysis:",
        options=sorted(df['country'].unique()),
        default=['United Arab Emirates', 'Qatar', 'Saudi Arabia', 'Malaysia'][:3],
        max_selections=8
    )
    
    if selected_countries:
        country_trends = df[df['country'].isin(selected_countries)]
        
        # ADEI trends
        fig = px.line(
            country_trends,
            x='year',
            y='adei_score',
            color='country',
            title="ADEI Score Trends by Country",
            markers=True
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        # Performance improvement analysis
        st.markdown("### 📈 Performance Improvement Analysis")
        
        improvement_data = []
        for country in selected_countries:
            country_data = df[df['country'] == country].sort_values('year')
            if len(country_data) > 1:
                first_score = country_data['adei_score'].iloc[0]
                last_score = country_data['adei_score'].iloc[-1]
                improvement = last_score - first_score
                improvement_pct = (improvement / first_score) * 100 if first_score > 0 else 0
                
                improvement_data.append({
                    'Country': country,
                    'Initial Score': first_score,
                    'Final Score': last_score,
                    'Total Improvement': improvement,
                    'Improvement %': improvement_pct
                })
        
        if improvement_data:
            improvement_df = pd.DataFrame(improvement_data)
            improvement_df = improvement_df.sort_values('Improvement %', ascending=False)
            
            fig = px.bar(
                improvement_df,
                x='Improvement %',
                y='Country',
                orientation='h',
                title="Country Improvement Rankings",
                color='Improvement %',
                color_continuous_scale='RdYlGn'
            )
            fig.update_layout(height=400, yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
            
            st.dataframe(improvement_df.round(2), use_container_width=True)

if __name__ == "__main__":
    main()