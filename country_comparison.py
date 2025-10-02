# Country Comparison Module for Streamlit App
# ==========================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

def show_country_comparison(df=None):
    """Advanced Country Comparison Interface"""
    st.markdown('<div class="main-header">🌍 Country Comparison Analysis</div>', unsafe_allow_html=True)
    
    # Use provided data or show error if not available
    if df is None:
        st.error("Data not provided to country comparison module.")
        return
    
    # Sidebar controls
    st.sidebar.markdown("### 🎛️ Comparison Controls")
    
    # Year selection
    available_years = sorted(df['year'].unique())
    selected_years = st.sidebar.multiselect(
        "Select Years for Comparison:",
        options=available_years,
        default=[2025],  # Default to latest year
        help="Choose one or more years to compare"
    )
    
    # Country selection
    available_countries = sorted(df['country'].unique())
    default_countries = ['United Arab Emirates', 'Qatar', 'Saudi Arabia', 'Malaysia', 'Türkiye']
    
    selected_countries = st.sidebar.multiselect(
        "Select Countries for Comparison:",
        options=available_countries,
        default=[country for country in default_countries if country in available_countries][:3],
        help="Choose 2-10 countries to compare"
    )
    
    # Validation
    if not selected_years:
        st.warning("Please select at least one year.")
        return
    
    if len(selected_countries) < 2:
        st.warning("Please select at least 2 countries for comparison.")
        return
    
    if len(selected_countries) > 10:
        st.warning("Please select no more than 10 countries for better visualization.")
        selected_countries = selected_countries[:10]
    
    # Filter data
    filtered_df = df[
        (df['year'].isin(selected_years)) & 
        (df['country'].isin(selected_countries))
    ].copy()
    
    if filtered_df.empty:
        st.error("No data available for selected countries and years.")
        return
    
    # Comparison type selection
    comparison_type = st.radio(
        "Select Comparison Type:",
        ["Overall Performance", "Pillar Analysis", "Time Series", "Detailed Metrics"],
        horizontal=True
    )
    
    st.divider()
    
    if comparison_type == "Overall Performance":
        show_overall_performance_comparison(filtered_df, selected_countries, selected_years)
    elif comparison_type == "Pillar Analysis":
        show_pillar_comparison(filtered_df, selected_countries, selected_years)
    elif comparison_type == "Time Series":
        show_time_series_comparison(filtered_df, selected_countries, selected_years)
    elif comparison_type == "Detailed Metrics":
        show_detailed_metrics_comparison(filtered_df, selected_countries, selected_years)

def show_overall_performance_comparison(df, countries, years):
    """Overall ADEI Performance Comparison"""
    st.markdown("### 🏆 Overall ADEI Performance Comparison")
    
    # Latest year comparison
    if len(years) == 1:
        year = years[0]
        year_data = df[df['year'] == year]
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Bar chart comparison
            fig = px.bar(
                year_data.sort_values('adei_score', ascending=True),
                x='adei_score',
                y='country',
                orientation='h',
                title=f"ADEI Scores Comparison ({year})",
                color='adei_score',
                color_continuous_scale='Viridis',
                text='adei_score'
            )
            fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Performance tier distribution
            tier_counts = year_data['performance_tier'].value_counts()
            
            fig = px.pie(
                values=tier_counts.values,
                names=tier_counts.index,
                title=f"Performance Distribution ({year})"
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    else:
        # Multi-year comparison
        fig = px.line(
            df,
            x='year',
            y='adei_score',
            color='country',
            title="ADEI Score Evolution",
            markers=True,
            line_shape='linear'
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
    
    # Summary statistics table
    st.markdown("### 📊 Summary Statistics")
    
    summary_stats = df.groupby('country').agg({
        'adei_score': ['mean', 'min', 'max', 'std'],
        'year': 'count'
    }).round(2)
    
    summary_stats.columns = ['Avg Score', 'Min Score', 'Max Score', 'Std Dev', 'Data Points']
    summary_stats = summary_stats.sort_values('Avg Score', ascending=False)
    
    st.dataframe(summary_stats, use_container_width=True)

def show_pillar_comparison(df, countries, years):
    """Detailed Pillar Performance Comparison"""
    st.markdown("### 🏛️ Pillar Performance Analysis")
    
    # Pillar columns
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
    
    # Year selection for pillar analysis
    if len(years) > 1:
        selected_year = st.selectbox(
            "Select year for pillar analysis:",
            options=years,
            index=len(years)-1  # Default to latest year
        )
    else:
        selected_year = years[0]
    
    year_data = df[df['year'] == selected_year]
    
    # Radar chart comparison
    st.markdown(f"#### 🎯 Radar Chart Comparison ({selected_year})")
    
    fig = go.Figure()
    
    for country in countries:
        country_data = year_data[year_data['country'] == country]
        if not country_data.empty:
            values = []
            for col in pillar_columns:
                val = country_data[col].iloc[0]
                values.append(val if pd.notna(val) else 0)
            
            # Close the radar chart
            values.append(values[0])
            labels_with_close = pillar_labels + [pillar_labels[0]]
            
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=labels_with_close,
                fill='toself',
                name=country,
                line_color=px.colors.qualitative.Set1[countries.index(country) % len(px.colors.qualitative.Set1)]
            ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=True,
        title="Pillar Performance Radar Chart",
        height=600
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Grouped bar chart for pillars
    st.markdown(f"#### 📊 Pillar Scores Bar Chart ({selected_year})")
    
    # Prepare data for grouped bar chart
    comparison_data = []
    for country in countries:
        country_data = year_data[year_data['country'] == country]
        if not country_data.empty:
            for col, label in zip(pillar_columns, pillar_labels):
                val = country_data[col].iloc[0]
                if pd.notna(val):
                    comparison_data.append({
                        'Country': country,
                        'Pillar': label,
                        'Score': val
                    })
    
    if comparison_data:
        comparison_df = pd.DataFrame(comparison_data)
        
        fig = px.bar(
            comparison_df,
            x='Pillar',
            y='Score',
            color='Country',
            title="Pillar Performance Comparison",
            barmode='group',
            height=500
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    # Pillar comparison table
    st.markdown(f"#### 📋 Detailed Pillar Scores ({selected_year})")
    
    pillar_table_data = year_data[['country'] + pillar_columns].set_index('country')
    pillar_table_data.columns = pillar_labels
    pillar_table_data = pillar_table_data.round(1)
    
    # Color coding based on performance
    styled_table = pillar_table_data.style.background_gradient(
        cmap='RdYlGn', 
        subset=pillar_labels,
        vmin=0, 
        vmax=100
    ).format(precision=1)
    
    st.dataframe(styled_table, use_container_width=True)

def show_time_series_comparison(df, countries, years):
    """Time Series Analysis and Trends"""
    st.markdown("### 📈 Time Series Analysis")
    
    if len(years) < 2:
        st.warning("Please select at least 2 years for time series analysis.")
        return
    
    # Overall ADEI trend
    st.markdown("#### 🏆 ADEI Score Evolution")
    
    fig = px.line(
        df,
        x='year',
        y='adei_score',
        color='country',
        title="ADEI Score Trends",
        markers=True,
        line_shape='linear'
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Growth rate analysis
    st.markdown("#### 📊 Growth Rate Analysis")
    
    growth_data = []
    for country in countries:
        country_df = df[df['country'] == country].sort_values('year')
        if len(country_df) > 1:
            initial_score = country_df['adei_score'].iloc[0]
            final_score = country_df['adei_score'].iloc[-1]
            
            if initial_score > 0:
                growth_rate = ((final_score - initial_score) / initial_score) * 100
                total_improvement = final_score - initial_score
                
                growth_data.append({
                    'Country': country,
                    'Initial Score': initial_score,
                    'Final Score': final_score,
                    'Total Improvement': total_improvement,
                    'Growth Rate (%)': growth_rate
                })
    
    if growth_data:
        growth_df = pd.DataFrame(growth_data)
        growth_df = growth_df.sort_values('Growth Rate (%)', ascending=False)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(
                growth_df,
                x='Growth Rate (%)',
                y='Country',
                orientation='h',
                title="Growth Rate Comparison",
                color='Growth Rate (%)',
                color_continuous_scale='RdYlGn'
            )
            fig.update_layout(height=400, yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.scatter(
                growth_df,
                x='Initial Score',
                y='Final Score',
                size='Total Improvement',
                hover_data=['Country'],
                title="Initial vs Final Score",
                color='Growth Rate (%)',
                color_continuous_scale='RdYlGn'
            )
            fig.add_shape(
                type="line", line=dict(dash="dash"),
                x0=growth_df['Initial Score'].min(), y0=growth_df['Initial Score'].min(),
                x1=growth_df['Initial Score'].max(), y1=growth_df['Initial Score'].max()
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(growth_df.round(2), use_container_width=True)

def show_detailed_metrics_comparison(df, countries, years):
    """Detailed Metrics and Statistical Comparison"""
    st.markdown("### 📋 Detailed Metrics Comparison")
    
    # Latest year for detailed comparison
    latest_year = max(years)
    latest_data = df[df['year'] == latest_year]
    
    # All metrics comparison
    st.markdown(f"#### 🔍 Complete Metrics Overview ({latest_year})")
    
    # Select metrics categories
    metric_categories = {
        "Governance Indicators": [
            'political_stability', 'government_effectiveness', 'voice_accountability',
            'regulatory_quality', 'rule_of_law', 'control_corruption'
        ],
        "Technology & Digital": [
            'secure_internet_servers', 'e_security', 'online_shopping',
            'ict_regulatory_environment', 'access_to_ict', 'use_of_ict'
        ],
        "Innovation & R&D": [
            'university_industry_collaboration', 'knowledge_impact',
            'emerging_tech_adoption', 'emerging_tech_investment'
        ],
        "SDG Indicators": [
            'sdg_1_no_poverty', 'sdg_2_zero_hunger', 'sdg_3_health_wellbeing',
            'sdg_4_quality_education', 'sdg_8_economic_growth', 'sdg_9_innovation_infrastructure'
        ]
    }
    
    selected_category = st.selectbox(
        "Select Metric Category:",
        options=list(metric_categories.keys())
    )
    
    selected_metrics = metric_categories[selected_category]
    
    # Filter available metrics (those that exist in the data)
    available_metrics = [col for col in selected_metrics if col in latest_data.columns]
    
    if available_metrics:
        # Heatmap comparison
        heatmap_data = latest_data[latest_data['country'].isin(countries)][['country'] + available_metrics]
        heatmap_data = heatmap_data.set_index('country')
        
        fig = px.imshow(
            heatmap_data.T,
            labels=dict(x="Country", y="Metric", color="Score"),
            title=f"{selected_category} Heatmap",
            color_continuous_scale='RdYlGn',
            aspect="auto"
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        # Statistical summary
        st.markdown("#### 📊 Statistical Summary")
        
        stats_summary = heatmap_data.describe().T
        stats_summary = stats_summary.round(2)
        
        st.dataframe(stats_summary, use_container_width=True)
        
        # Ranking table
        st.markdown("#### 🏅 Rankings by Metric")
        
        ranking_data = []
        for metric in available_metrics:
            metric_data = heatmap_data[metric].dropna().sort_values(ascending=False)
            for rank, (country, score) in enumerate(metric_data.items(), 1):
                ranking_data.append({
                    'Metric': metric.replace('_', ' ').title(),
                    'Rank': rank,
                    'Country': country,
                    'Score': score
                })
        
        ranking_df = pd.DataFrame(ranking_data)
        
        # Display rankings for top metrics
        for metric in available_metrics[:3]:  # Show top 3 metrics
            metric_rankings = ranking_df[ranking_df['Metric'] == metric.replace('_', ' ').title()]
            
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown(f"**{metric.replace('_', ' ').title()} Rankings:**")
                st.dataframe(
                    metric_rankings[['Rank', 'Country', 'Score']].head(len(countries)),
                    hide_index=True,
                    use_container_width=True
                )
    
    else:
        st.warning(f"No data available for {selected_category} metrics.")
    
    # Export functionality
    st.markdown("#### 💾 Export Data")
    
    if st.button("Export Comparison Data to CSV"):
        export_data = df[df['country'].isin(countries) & df['year'].isin(years)]
        csv = export_data.to_csv(index=False)
        
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"oic_adei_comparison_{'-'.join(map(str, years))}.csv",
            mime="text/csv"
        )