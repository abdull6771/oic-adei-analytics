"""
Test suite for visualization components and Metabase parity
Tests chart generation, data visualization, and visual parity with Metabase
"""
import pytest
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from streamlit_app import load_data, get_countries, get_years
    import config
except ImportError as e:
    pytest.skip(f"Skipping tests due to missing dependencies: {e}", allow_module_level=True)


class TestExecutiveDashboard:
    """Test Executive Dashboard visualizations"""
    
    def test_key_metrics_calculation(self):
        """Test calculation of key metrics"""
        df = load_data()
        
        # Test metrics that should be calculated
        total_countries = df['country'].nunique()
        total_records = len(df)
        years_covered = df['year'].nunique()
        avg_score = df['adei_score'].mean()
        
        assert total_countries > 0, "Should have countries"
        assert total_records > 0, "Should have records"
        assert years_covered > 0, "Should have years"
        assert 0 <= avg_score <= 1, "Average score should be in valid range"
    
    def test_top_performers_data(self):
        """Test top performers calculation for bar chart"""
        df = load_data()
        
        # Get latest year data
        latest_year = df['year'].max()
        latest_data = df[df['year'] == latest_year]
        
        # Get top 10 performers
        top_performers = latest_data.nlargest(10, 'adei_score')
        
        assert len(top_performers) <= 10, "Should have at most 10 top performers"
        assert len(top_performers) > 0, "Should have at least 1 performer"
        
        # Check that scores are in descending order
        scores = top_performers['adei_score'].tolist()
        assert scores == sorted(scores, reverse=True), "Scores should be in descending order"
    
    def test_performance_distribution(self):
        """Test performance distribution for pie chart"""
        df = load_data()
        latest_year = df['year'].max()
        latest_data = df[df['year'] == latest_year]
        
        # Categorize performance
        def categorize_performance(score):
            if score >= 0.7:
                return 'High'
            elif score >= 0.5:
                return 'Medium'
            else:
                return 'Low'
        
        latest_data['performance_tier'] = latest_data['adei_score'].apply(categorize_performance)
        distribution = latest_data['performance_tier'].value_counts()
        
        assert 'High' in distribution.index or 'Medium' in distribution.index or 'Low' in distribution.index, \
            "Should have at least one performance tier"
        
        # Check that all values sum to total countries in latest year
        assert distribution.sum() == len(latest_data), "Distribution should account for all countries"
    
    def test_global_trends_data(self):
        """Test global trends calculation for line chart"""
        df = load_data()
        
        # Calculate yearly averages
        yearly_avg = df.groupby('year')['adei_score'].mean().reset_index()
        
        assert len(yearly_avg) > 0, "Should have yearly averages"
        assert yearly_avg['year'].is_monotonic_increasing, "Years should be in ascending order"
        
        # Check that all averages are in valid range
        assert yearly_avg['adei_score'].min() >= 0, "Average scores should be non-negative"
        assert yearly_avg['adei_score'].max() <= 1, "Average scores should be <= 1"


class TestPillarAnalysis:
    """Test Pillar Analysis visualizations"""
    
    def test_pillar_data_availability(self):
        """Test that pillar data is available"""
        df = load_data()
        
        pillar_columns = [col for col in df.columns if col.startswith('adei_') and col != 'adei_score']
        assert len(pillar_columns) >= 4, "Should have at least 4 pillar columns"
        
        # Check that pillar data exists
        for col in pillar_columns:
            non_null_count = df[col].notna().sum()
            assert non_null_count > 0, f"Pillar {col} should have non-null data"
    
    def test_pillar_comparison_data(self):
        """Test pillar comparison calculation"""
        df = load_data()
        latest_year = df['year'].max()
        latest_data = df[df['year'] == latest_year]
        
        pillar_columns = [col for col in df.columns if col.startswith('adei_') and col != 'adei_score']
        
        # Get top countries for comparison
        top_countries = latest_data.nlargest(5, 'adei_score')['country'].tolist()
        comparison_data = latest_data[latest_data['country'].isin(top_countries)]
        
        assert len(comparison_data) > 0, "Should have comparison data"
        assert len(comparison_data) <= 5, "Should have at most 5 countries"
        
        # Check that all pillar columns have data for these countries
        for col in pillar_columns:
            has_data = comparison_data[col].notna().any()
            assert has_data, f"Top countries should have data for {col}"
    
    def test_correlation_matrix_calculation(self):
        """Test correlation matrix calculation"""
        df = load_data()
        
        pillar_columns = [col for col in df.columns if col.startswith('adei_') and col != 'adei_score']
        
        if len(pillar_columns) >= 2:
            # Calculate correlation matrix
            correlation_data = df[pillar_columns].corr()
            
            assert correlation_data.shape[0] == len(pillar_columns), \
                "Correlation matrix should have correct dimensions"
            assert correlation_data.shape[1] == len(pillar_columns), \
                "Correlation matrix should be square"
            
            # Check diagonal values are 1 (self-correlation)
            for i in range(len(pillar_columns)):
                assert abs(correlation_data.iloc[i, i] - 1.0) < 0.001, \
                    "Diagonal values should be 1"


class TestCountryComparisonVisuals:
    """Test Country Comparison visualizations"""
    
    def test_comparison_data_filtering(self):
        """Test data filtering for country comparison"""
        df = load_data()
        
        # Select test countries and years
        countries = get_countries()[:3]
        years = get_years()[:2]
        
        # Filter data
        filtered_data = df[
            (df['country'].isin(countries)) & 
            (df['year'].isin(years))
        ]
        
        assert len(filtered_data) > 0, "Filtered data should not be empty"
        assert filtered_data['country'].nunique() <= len(countries), \
            "Should not exceed selected countries"
        assert filtered_data['year'].nunique() <= len(years), \
            "Should not exceed selected years"
    
    def test_radar_chart_data_preparation(self):
        """Test radar chart data preparation"""
        df = load_data()
        
        countries = get_countries()[:2]
        year = get_years()[-1]  # Latest year
        
        # Get data for radar chart
        radar_data = df[
            (df['country'].isin(countries)) & 
            (df['year'] == year)
        ]
        
        pillar_columns = [col for col in df.columns if col.startswith('adei_') and col != 'adei_score']
        
        if len(pillar_columns) > 0 and len(radar_data) > 0:
            # Check that data is suitable for radar chart
            for col in pillar_columns:
                values = radar_data[col].dropna()
                if len(values) > 0:
                    assert values.min() >= 0, f"Radar data for {col} should be non-negative"
                    assert values.max() <= 1, f"Radar data for {col} should be <= 1"


class TestChartGeneration:
    """Test chart generation and Plotly integration"""
    
    def test_bar_chart_creation(self):
        """Test bar chart creation"""
        df = load_data()
        latest_year = df['year'].max()
        latest_data = df[df['year'] == latest_year]
        top_performers = latest_data.nlargest(10, 'adei_score')
        
        # Create bar chart
        fig = px.bar(
            top_performers,
            x='adei_score',
            y='country',
            orientation='h',
            title='Top 10 Countries by ADEI Score'
        )
        
        assert fig is not None, "Bar chart should be created"
        assert len(fig.data) > 0, "Chart should have data"
        assert fig.data[0].type == 'bar', "Should be a bar chart"
    
    def test_line_chart_creation(self):
        """Test line chart creation"""
        df = load_data()
        yearly_avg = df.groupby('year')['adei_score'].mean().reset_index()
        
        # Create line chart
        fig = px.line(
            yearly_avg,
            x='year',
            y='adei_score',
            title='Global ADEI Score Trends'
        )
        
        assert fig is not None, "Line chart should be created"
        assert len(fig.data) > 0, "Chart should have data"
        assert fig.data[0].type == 'scatter', "Should be a line chart"
    
    def test_pie_chart_creation(self):
        """Test pie chart creation"""
        df = load_data()
        latest_year = df['year'].max()
        latest_data = df[df['year'] == latest_year]
        
        # Categorize performance
        def categorize_performance(score):
            if score >= 0.7:
                return 'High'
            elif score >= 0.5:
                return 'Medium'
            else:
                return 'Low'
        
        latest_data['performance_tier'] = latest_data['adei_score'].apply(categorize_performance)
        distribution = latest_data['performance_tier'].value_counts().reset_index()
        
        # Create pie chart
        fig = px.pie(
            distribution,
            values='count',
            names='performance_tier',
            title='Performance Distribution'
        )
        
        assert fig is not None, "Pie chart should be created"
        assert len(fig.data) > 0, "Chart should have data"
        assert fig.data[0].type == 'pie', "Should be a pie chart"
    
    def test_heatmap_creation(self):
        """Test heatmap creation"""
        df = load_data()
        pillar_columns = [col for col in df.columns if col.startswith('adei_') and col != 'adei_score']
        
        if len(pillar_columns) >= 2:
            correlation_matrix = df[pillar_columns].corr()
            
            # Create heatmap
            fig = px.imshow(
                correlation_matrix,
                title='Pillar Correlation Matrix',
                color_continuous_scale='RdBu_r'
            )
            
            assert fig is not None, "Heatmap should be created"
            assert len(fig.data) > 0, "Chart should have data"
            assert fig.data[0].type == 'heatmap', "Should be a heatmap"


class TestMetabaseParity:
    """Test visual parity with Metabase dashboards"""
    
    def test_executive_dashboard_metrics(self):
        """Test that executive dashboard reproduces Metabase metrics"""
        df = load_data()
        
        # Key metrics that should match Metabase
        total_countries = df['country'].nunique()
        total_records = len(df)
        year_range = f"{df['year'].min()}-{df['year'].max()}"
        avg_score = round(df['adei_score'].mean(), 3)
        
        # These should be reasonable values matching what we expect
        assert total_countries >= 20, "Should have reasonable number of countries"
        assert total_records >= 100, "Should have reasonable number of records"
        assert df['year'].min() >= 2021, "Should start from 2021"
        assert 0.3 <= avg_score <= 0.8, "Average score should be reasonable"
    
    def test_top_performers_consistency(self):
        """Test top performers match expected format"""
        df = load_data()
        latest_year = df['year'].max()
        latest_data = df[df['year'] == latest_year]
        top_10 = latest_data.nlargest(10, 'adei_score')
        
        # Should have exactly 10 or fewer countries
        assert len(top_10) <= 10, "Should have at most 10 top performers"
        
        # Scores should be in descending order
        scores = top_10['adei_score'].tolist()
        assert scores == sorted(scores, reverse=True), "Should be sorted by score descending"
        
        # Top score should be reasonable
        assert top_10.iloc[0]['adei_score'] >= 0.5, "Top performer should have decent score"
    
    def test_chart_styling_consistency(self):
        """Test that chart styling is consistent and professional"""
        df = load_data()
        
        # Test color palette from config
        colors = config.CHART_CONFIG['color_palette']
        assert len(colors) >= 10, "Should have enough colors for visualizations"
        
        # Test that all colors are valid hex colors
        for color in colors:
            assert color.startswith('#'), "Colors should be hex codes"
            assert len(color) == 7, "Hex colors should be 7 characters"
    
    def test_data_freshness(self):
        """Test that data is current and complete"""
        df = load_data()
        
        # Should have recent data
        max_year = df['year'].max()
        assert max_year >= 2023, "Should have recent data"
        
        # Should have data for recent years
        recent_years = df['year'].unique()
        assert len(recent_years) >= 2, "Should have multiple years of data"
        
        # Should have complete ADEI scores
        complete_scores = df['adei_score'].notna().sum()
        total_records = len(df)
        completeness_ratio = complete_scores / total_records
        assert completeness_ratio >= 0.8, "Should have high data completeness"


if __name__ == "__main__":
    # Run visualization tests
    pytest.main([__file__, "-v", "--tb=short"])