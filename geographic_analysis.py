# Geographic Analysis Module for OIC ADEI Analytics
# =================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from typing import Dict, List, Tuple
import json

# OIC Regional Groupings
OIC_REGIONS = {
    'Gulf Cooperation Council (GCC)': [
        'Bahrain', 'Kuwait', 'Oman', 'Qatar', 'Saudi Arabia', 'United Arab Emirates'
    ],
    'Non-GCC Middle East': [
        'Iran', 'Iraq', 'Jordan', 'Lebanon', 'Palestine', 'Syria', 'Yemen'
    ],
    'Southeast Asia (ASEAN)': [
        'Brunei Darussalam', 'Indonesia', 'Malaysia'
    ],
    'North Africa': [
        'Algeria', 'Egypt', 'Libya', 'Morocco', 'Sudan', 'Tunisia'
    ],
    'West Africa': [
        'Benin', 'Burkina Faso', 'Cameroon', 'Chad', 'Côte d\'Ivoire', 'The Gambia',
        'Guinea', 'Guinea-Bissau', 'Mali', 'Mauritania', 'Niger', 'Nigeria',
        'Senegal', 'Sierra Leone', 'Togo'
    ],
    'East Africa': [
        'Comoros', 'Djibouti', 'Somalia', 'Uganda'
    ],
    'Central Asia': [
        'Azerbaijan', 'Kazakhstan', 'Kyrgyzstan', 'Tajikistan', 'Turkmenistan'
    ],
    'South Asia': [
        'Afghanistan', 'Bangladesh', 'Maldives', 'Pakistan'
    ],
    'South America': [
        'Guyana', 'Suriname'
    ]
}

# Geographic neighbors mapping (simplified - can be enhanced with actual geographic data)
GEOGRAPHIC_NEIGHBORS = {
    'Turkey': ['Azerbaijan', 'Iran', 'Iraq', 'Syria', 'Armenia', 'Georgia', 'Bulgaria', 'Greece'],
    'Saudi Arabia': ['Iraq', 'Jordan', 'Kuwait', 'Oman', 'Qatar', 'United Arab Emirates', 'Yemen'],
    'Egypt': ['Libya', 'Sudan', 'Palestine', 'Israel'],
    'Iran': ['Afghanistan', 'Azerbaijan', 'Iraq', 'Pakistan', 'Turkey', 'Turkmenistan'],
    'Pakistan': ['Afghanistan', 'Iran', 'India', 'China'],
    'Indonesia': ['Malaysia', 'Brunei', 'Papua New Guinea', 'East Timor'],
    'Malaysia': ['Indonesia', 'Brunei', 'Thailand', 'Singapore'],
    'Morocco': ['Algeria', 'Spain'],
    'Algeria': ['Morocco', 'Tunisia', 'Libya', 'Niger', 'Mali'],
    'Nigeria': ['Niger', 'Chad', 'Cameroon', 'Benin'],
    'Kazakhstan': ['Kyrgyzstan', 'Uzbekistan', 'Turkmenistan', 'Russia', 'China'],
    'Bangladesh': ['India', 'Myanmar'],
    'Jordan': ['Iraq', 'Saudi Arabia', 'Syria', 'Palestine', 'Israel'],
    'Lebanon': ['Syria', 'Palestine', 'Israel'],
    'Iraq': ['Iran', 'Turkey', 'Syria', 'Jordan', 'Saudi Arabia', 'Kuwait'],
    'Syria': ['Turkey', 'Iraq', 'Jordan', 'Lebanon', 'Palestine', 'Israel'],
    'Afghanistan': ['Iran', 'Pakistan', 'Tajikistan', 'Uzbekistan', 'Turkmenistan', 'China'],
    'UAE': ['Saudi Arabia', 'Oman'],
    'Kuwait': ['Iraq', 'Saudi Arabia'],
    'Qatar': ['Saudi Arabia'],
    'Oman': ['UAE', 'Saudi Arabia', 'Yemen'],
    'Yemen': ['Saudi Arabia', 'Oman'],
    'Uzbekistan': ['Afghanistan', 'Kazakhstan', 'Kyrgyzstan', 'Tajikistan', 'Turkmenistan'],
    'Turkmenistan': ['Afghanistan', 'Iran', 'Kazakhstan', 'Uzbekistan'],
    'Tajikistan': ['Afghanistan', 'Kyrgyzstan', 'Uzbekistan', 'China'],
    'Kyrgyzstan': ['Kazakhstan', 'Tajikistan', 'Uzbekistan', 'China'],
    'Azerbaijan': ['Iran', 'Turkey', 'Armenia', 'Georgia', 'Russia'],
    'Albania': ['Montenegro', 'Kosovo', 'North Macedonia', 'Greece'],
    'Bosnia and Herzegovina': ['Croatia', 'Montenegro', 'Serbia'],
    'Kosovo': ['Albania', 'Montenegro', 'North Macedonia', 'Serbia']
}

# ISO country codes for choropleth mapping
ISO_COUNTRY_CODES = {
    'Afghanistan': 'AFG', 'Albania': 'ALB', 'Algeria': 'DZA', 'Azerbaijan': 'AZE',
    'Bahrain': 'BHR', 'Bangladesh': 'BGD', 'Benin': 'BEN', 'Bosnia and Herzegovina': 'BIH',
    'Brunei': 'BRN', 'Burkina Faso': 'BFA', 'Cameroon': 'CMR', 'Chad': 'TCD',
    'Comoros': 'COM', 'Ivory Coast': 'CIV', 'Djibouti': 'DJI', 'Egypt': 'EGY',
    'Gabon': 'GAB', 'Gambia': 'GMB', 'Guinea': 'GIN', 'Guinea-Bissau': 'GNB',
    'Guyana': 'GUY', 'Indonesia': 'IDN', 'Iran': 'IRN', 'Iraq': 'IRQ',
    'Jordan': 'JOR', 'Kazakhstan': 'KAZ', 'Kosovo': 'XKX', 'Kuwait': 'KWT',
    'Kyrgyzstan': 'KGZ', 'Lebanon': 'LBN', 'Libya': 'LBY', 'Malaysia': 'MYS',
    'Maldives': 'MDV', 'Mali': 'MLI', 'Morocco': 'MAR', 'Mozambique': 'MOZ',
    'Niger': 'NER', 'Nigeria': 'NGA', 'Oman': 'OMN', 'Pakistan': 'PAK',
    'Palestine': 'PSE', 'Qatar': 'QAT', 'Saudi Arabia': 'SAU', 'Senegal': 'SEN',
    'Sierra Leone': 'SLE', 'Somalia': 'SOM', 'Sudan': 'SDN', 'Suriname': 'SUR',
    'Syria': 'SYR', 'Tajikistan': 'TJK', 'Togo': 'TGO', 'Tunisia': 'TUN',
    'Turkey': 'TUR', 'Turkmenistan': 'TKM', 'Uganda': 'UGA', 'United Arab Emirates': 'ARE',
    'Uzbekistan': 'UZB', 'Yemen': 'YEM'
}

# Sample World Bank GDP data (in practice, this would be loaded from an API or database)
# REMOVED - GDP functionality has been removed per user request

def get_country_region(country: str) -> str:
    """Get the OIC region for a given country"""
    for region, countries in OIC_REGIONS.items():
        if country in countries:
            return region
    return None

def show_geographic_analysis(df=None):
    """Main Geographic Analysis Interface"""
    st.markdown('<div class="main-header">🌍 Geographic Analysis</div>', unsafe_allow_html=True)
    
    if df is None:
        st.error("Data not provided to geographic analysis module.")
        return
    
    # Add region column to dataframe
    df['region'] = df['country'].apply(get_country_region)
    
    # Filter out countries that are not part of the defined OIC regions
    df = df[df['region'].notna()].copy()
    
    # Sidebar controls
    st.sidebar.markdown("### 🗺️ Geographic Controls")
    
    # Analysis type selection
    analysis_type = st.sidebar.selectbox(
        "Select Analysis Type:",
        ["🌍 World Map", "🏢 Regional Analysis", "🤝 Neighboring Countries"]
    )
    
    # Year selection
    available_years = sorted(df['year'].unique())
    selected_year = st.sidebar.selectbox(
        "Select Year:",
        available_years,
        index=len(available_years)-1  # Default to latest year
    )
    
    # Filter data for selected year
    year_data = df[df['year'] == selected_year].copy()
    
    if analysis_type == "🌍 World Map":
        show_world_map(year_data, selected_year)
    elif analysis_type == "🏢 Regional Analysis":
        show_regional_analysis(df, year_data, selected_year)
    elif analysis_type == "🤝 Neighboring Countries":
        show_neighboring_countries_analysis(year_data, selected_year)

def show_world_map(df, year):
    """Display interactive world map with ADEI scores"""
    st.markdown(f"### 🌍 Global ADEI Scores - {year}")
    
    # Add ISO codes for mapping
    df['iso_code'] = df['country'].map(ISO_COUNTRY_CODES)
    
    # Create choropleth map
    fig = px.choropleth(
        df,
        locations='iso_code',
        color='adei_score',
        hover_name='country',
        hover_data={
            'adei_score': ':.3f',
            'region': True,
            'iso_code': False
        },
        color_continuous_scale='RdYlGn',
        range_color=[df['adei_score'].min(), df['adei_score'].max()],
        title=f'ADEI Scores by Country - {year}',
        labels={'adei_score': 'ADEI Score'}
    )
    
    fig.update_layout(
        height=600,
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type='equirectangular'
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Summary statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Countries Mapped", len(df))
    with col2:
        st.metric("Highest Score", f"{df['adei_score'].max():.3f}")
    with col3:
        st.metric("Lowest Score", f"{df['adei_score'].min():.3f}")
    with col4:
        st.metric("Global Average", f"{df['adei_score'].mean():.3f}")
    
    # Top and bottom performers
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🏆 Top 10 Performers")
        top_10 = df.nlargest(10, 'adei_score')[['country', 'adei_score', 'region']]
        top_10['rank'] = range(1, len(top_10) + 1)
        st.dataframe(top_10[['rank', 'country', 'region', 'adei_score']], hide_index=True)
    
    with col2:
        st.markdown("#### 📉 Bottom 10 Performers")
        bottom_10 = df.nsmallest(10, 'adei_score')[['country', 'adei_score', 'region']]
        bottom_10['rank'] = range(len(df), len(df) - len(bottom_10), -1)
        st.dataframe(bottom_10[['rank', 'country', 'region', 'adei_score']], hide_index=True)

def show_regional_analysis(full_df, year_data, year):
    """Display regional comparison analysis"""
    st.markdown(f"### 🏢 Regional Analysis - {year}")
    
    # Regional statistics
    regional_stats = year_data.groupby('region').agg({
        'adei_score': ['mean', 'std', 'min', 'max', 'count']
    }).round(3)
    
    regional_stats.columns = ['Average', 'Std Dev', 'Min', 'Max', 'Countries']
    regional_stats = regional_stats.sort_values('Average', ascending=False)
    
    # Display regional statistics table
    st.markdown("#### 📊 Regional Performance Summary")
    st.dataframe(regional_stats, use_container_width=True)
    
    # Regional comparison chart
    fig = px.box(
        year_data,
        x='region',
        y='adei_score',
        title=f'ADEI Score Distribution by Region - {year}',
        color='region'
    )
    
    fig.update_layout(height=500, xaxis_title='Region', yaxis_title='ADEI Score')
    st.plotly_chart(fig, use_container_width=True)
    
    # Regional trends over time
    st.markdown("#### 📈 Regional Trends Over Time")
    
    regional_trends = full_df.groupby(['year', 'region'])['adei_score'].mean().reset_index()
    
    fig = px.line(
        regional_trends,
        x='year',
        y='adei_score',
        color='region',
        title='Regional ADEI Score Trends',
        markers=True
    )
    
    fig.update_layout(height=500, xaxis_title='Year', yaxis_title='Average ADEI Score')
    st.plotly_chart(fig, use_container_width=True)
    
    # Individual region analysis
    st.markdown("#### 🔍 Individual Region Deep Dive")
    selected_region = st.selectbox("Select Region for Detailed Analysis:", 
                                 sorted(year_data['region'].unique()))
    
    if selected_region:
        region_data = year_data[year_data['region'] == selected_region]
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Top performers in region
            st.markdown(f"**Top Performers in {selected_region}**")
            top_in_region = region_data.nlargest(5, 'adei_score')[['country', 'adei_score']]
            st.dataframe(top_in_region, hide_index=True)
        
        with col2:
            # Regional pillar analysis
            pillar_cols = [col for col in region_data.columns if col.startswith('adei_') and col != 'adei_score']
            if pillar_cols:
                st.markdown(f"**Average Pillar Scores - {selected_region}**")
                pillar_means = region_data[pillar_cols].mean().sort_values(ascending=False)
                pillar_chart = px.bar(
                    x=pillar_means.values,
                    y=[col.replace('adei_', '').replace('_', ' ').title() for col in pillar_means.index],
                    orientation='h',
                    title=f'Pillar Performance - {selected_region}'
                )
                pillar_chart.update_layout(height=300)
                st.plotly_chart(pillar_chart, use_container_width=True)

def show_neighboring_countries_analysis(df, year):
    """Display neighboring countries comparison"""
    st.markdown(f"### 🤝 Neighboring Countries Analysis - {year}")
    
    # Country selection
    available_countries = sorted([country for country in df['country'].unique() 
                                if country in GEOGRAPHIC_NEIGHBORS.keys()])
    
    if not available_countries:
        st.warning("No countries with defined neighbors found in the current dataset.")
        return
    
    selected_country = st.selectbox("Select Country to Analyze:", available_countries)
    
    if selected_country:
        # Get neighbors data
        neighbors = GEOGRAPHIC_NEIGHBORS.get(selected_country, [])
        neighbors_in_data = [n for n in neighbors if n in df['country'].values]
        
        if not neighbors_in_data:
            st.warning(f"No neighboring countries found in dataset for {selected_country}")
            return
        
        # Get country and neighbors data
        country_data = df[df['country'] == selected_country]
        neighbors_data = df[df['country'].isin(neighbors_in_data)]
        
        # Comparison metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            country_score = country_data['adei_score'].iloc[0] if len(country_data) > 0 else 0
            st.metric(f"{selected_country} Score", f"{country_score:.3f}")
        
        with col2:
            neighbors_avg = neighbors_data['adei_score'].mean()
            st.metric("Neighbors Average", f"{neighbors_avg:.3f}")
        
        with col3:
            difference = country_score - neighbors_avg
            st.metric("Difference", f"{difference:.3f}", 
                     delta=f"{'Above' if difference > 0 else 'Below'} average")
        
        # Detailed comparison
        comparison_data = pd.concat([country_data, neighbors_data])
        comparison_data['is_selected'] = comparison_data['country'] == selected_country
        comparison_data = comparison_data.sort_values('adei_score', ascending=False)
        
        # Bar chart comparison
        fig = px.bar(
            comparison_data,
            x='country',
            y='adei_score',
            color='is_selected',
            title=f'{selected_country} vs Neighboring Countries - ADEI Scores',
            color_discrete_map={True: '#ff7f0e', False: '#1f77b4'}
        )
        
        fig.update_layout(
            height=500,
            xaxis_title='Country',
            yaxis_title='ADEI Score',
            showlegend=False
        )
        
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
        
        # Detailed table
        st.markdown("#### 📋 Detailed Comparison")
        display_data = comparison_data[['country', 'adei_score', 'region']].copy()
        display_data['rank'] = range(1, len(display_data) + 1)
        st.dataframe(display_data[['rank', 'country', 'region', 'adei_score']], hide_index=True)
        
        # Pillar comparison if available
        pillar_cols = [col for col in df.columns if col.startswith('adei_') and col != 'adei_score']
        if pillar_cols:
            st.markdown("#### 🏛️ Pillar Performance Comparison")
            
            pillar_comparison = comparison_data[['country'] + pillar_cols].set_index('country')
            
            # Create radar chart for selected country vs neighbors average
            neighbors_pillar_avg = neighbors_data[pillar_cols].mean()
            country_pillar_scores = country_data[pillar_cols].iloc[0] if len(country_data) > 0 else pd.Series()
            
            radar_data = pd.DataFrame({
                selected_country: country_pillar_scores,
                'Neighbors Average': neighbors_pillar_avg
            })
            
            # Create radar chart
            fig = go.Figure()
            
            for col in radar_data.columns:
                fig.add_trace(go.Scatterpolar(
                    r=radar_data[col].values,
                    theta=[c.replace('adei_', '').replace('_', ' ').title() for c in radar_data.index],
                    fill='toself',
                    name=col
                ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 1]
                    )),
                showlegend=True,
                title=f'Pillar Comparison: {selected_country} vs Neighbors',
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)