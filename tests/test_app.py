"""
Test suite for OIC ADEI Analytics Streamlit App
Tests database connectivity, data loading, and core functionality
"""
import pytest
import pandas as pd
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from streamlit_app import init_connection, load_data, get_countries, get_years
    from country_comparison import CountryComparison
    from rag_search import OICDataRAG
    import config
except ImportError as e:
    pytest.skip(f"Skipping tests due to missing dependencies: {e}", allow_module_level=True)


class TestDatabaseConnection:
    """Test database connectivity and data access"""
    
    def test_database_connection(self):
        """Test that database connection can be established"""
        engine = init_connection()
        assert engine is not None, "Database connection should be established"
        
        # Test connection is usable
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            assert result.fetchone()[0] == 1, "Database should respond to simple query"
    
    def test_data_loading(self):
        """Test that data can be loaded from database"""
        df = load_data()
        assert df is not None, "Data should be loaded successfully"
        assert len(df) > 0, "Data should contain records"
        assert 'country' in df.columns, "Data should have country column"
        assert 'year' in df.columns, "Data should have year column"
        assert 'adei_score' in df.columns, "Data should have ADEI score column"
    
    def test_data_quality(self):
        """Test data quality and structure"""
        df = load_data()
        
        # Check for required columns
        required_columns = [
            'country', 'year', 'adei_score',
            'adei_economic_opportunities', 'adei_educational_attainment',
            'adei_health_survival', 'adei_political_empowerment'
        ]
        
        for col in required_columns:
            assert col in df.columns, f"Required column {col} should be present"
        
        # Check data types
        assert df['year'].dtype in ['int64', 'Int64'], "Year should be integer"
        assert pd.api.types.is_numeric_dtype(df['adei_score']), "ADEI score should be numeric"
        
        # Check for reasonable data ranges
        assert df['adei_score'].min() >= 0, "ADEI scores should be non-negative"
        assert df['adei_score'].max() <= 1, "ADEI scores should be <= 1"
    
    def test_get_countries(self):
        """Test country listing functionality"""
        countries = get_countries()
        assert len(countries) > 0, "Should have countries in database"
        assert isinstance(countries, list), "Countries should be returned as list"
        assert all(isinstance(c, str) for c in countries), "All countries should be strings"
    
    def test_get_years(self):
        """Test year listing functionality"""
        years = get_years()
        assert len(years) > 0, "Should have years in database"
        assert isinstance(years, list), "Years should be returned as list"
        assert all(isinstance(y, int) for y in years), "All years should be integers"
        assert min(years) >= 2021, "Years should start from 2021"
        assert max(years) <= 2025, "Years should not exceed 2025"


class TestCountryComparison:
    """Test country comparison functionality"""
    
    def test_country_comparison_init(self):
        """Test CountryComparison initialization"""
        df = load_data()
        cc = CountryComparison(df)
        assert cc.df is not None, "CountryComparison should initialize with data"
    
    def test_overall_performance_comparison(self):
        """Test overall performance comparison"""
        df = load_data()
        cc = CountryComparison(df)
        
        # Get sample countries and years
        countries = get_countries()[:3]  # First 3 countries
        years = get_years()[:2]  # First 2 years
        
        # This should not raise an exception
        try:
            cc.show_overall_performance_comparison(countries, years)
        except Exception as e:
            pytest.fail(f"Overall performance comparison failed: {e}")
    
    def test_pillar_comparison(self):
        """Test pillar comparison functionality"""
        df = load_data()
        cc = CountryComparison(df)
        
        countries = get_countries()[:3]
        years = get_years()[:1]
        
        try:
            cc.show_pillar_comparison(countries, years)
        except Exception as e:
            pytest.fail(f"Pillar comparison failed: {e}")


class TestRAGSearch:
    """Test RAG search functionality"""
    
    def test_rag_initialization(self):
        """Test RAG system initialization"""
        df = load_data()
        
        try:
            rag = OICDataRAG(df)
            assert rag is not None, "RAG system should initialize"
        except Exception as e:
            # RAG initialization might fail due to missing models/internet
            pytest.skip(f"RAG initialization failed (expected): {e}")
    
    def test_rag_search(self):
        """Test RAG search functionality"""
        df = load_data()
        
        try:
            rag = OICDataRAG(df)
            
            # Test simple query
            response = rag.search("Which countries have high ADEI scores?")
            assert response is not None, "RAG should return response"
            assert len(response) > 0, "Response should not be empty"
            
        except Exception as e:
            pytest.skip(f"RAG search test skipped: {e}")


class TestConfiguration:
    """Test configuration and settings"""
    
    def test_config_loading(self):
        """Test configuration loading"""
        assert hasattr(config, 'DATABASE_CONFIG'), "Should have database config"
        assert hasattr(config, 'APP_CONFIG'), "Should have app config"
        assert hasattr(config, 'PILLARS'), "Should have pillar definitions"
    
    def test_database_config(self):
        """Test database configuration"""
        db_config = config.DATABASE_CONFIG
        required_keys = ['host', 'port', 'database', 'username', 'password']
        
        for key in required_keys:
            assert key in db_config, f"Database config should have {key}"
            assert db_config[key] is not None, f"Database config {key} should not be None"
    
    def test_pillar_config(self):
        """Test pillar configuration"""
        pillars = config.PILLARS
        assert len(pillars) >= 8, "Should have at least 8 pillars defined"
        
        # Check for key pillars
        key_pillars = [
            'adei_economic_opportunities',
            'adei_educational_attainment',
            'adei_health_survival',
            'adei_political_empowerment'
        ]
        
        for pillar in key_pillars:
            assert pillar in pillars, f"Should have {pillar} pillar defined"


class TestDataIntegrity:
    """Test data integrity and consistency"""
    
    def test_data_completeness(self):
        """Test data completeness across years and countries"""
        df = load_data()
        
        # Check for reasonable number of records
        assert len(df) >= 100, "Should have reasonable number of records"
        
        # Check for multiple years
        unique_years = df['year'].nunique()
        assert unique_years >= 2, "Should have data for multiple years"
        
        # Check for multiple countries
        unique_countries = df['country'].nunique()
        assert unique_countries >= 20, "Should have data for multiple countries"
    
    def test_score_consistency(self):
        """Test score consistency and relationships"""
        df = load_data()
        
        # ADEI score should be reasonable aggregate of pillars
        pillar_cols = [col for col in df.columns if col.startswith('adei_') and col != 'adei_score']
        
        if len(pillar_cols) > 0:
            # Check that pillar scores are in reasonable range
            for col in pillar_cols:
                pillar_scores = df[col].dropna()
                if len(pillar_scores) > 0:
                    assert pillar_scores.min() >= 0, f"{col} should have non-negative scores"
                    assert pillar_scores.max() <= 1, f"{col} should have scores <= 1"
    
    def test_temporal_consistency(self):
        """Test temporal consistency of data"""
        df = load_data()
        
        # Group by country and check for temporal consistency
        country_groups = df.groupby('country')
        
        for country, group in country_groups:
            if len(group) > 1:
                # Check that years are in sequence
                years = sorted(group['year'].tolist())
                assert years == list(range(min(years), max(years) + 1)), \
                    f"Country {country} should have consecutive years"


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"])