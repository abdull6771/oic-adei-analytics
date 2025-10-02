"""
Pytest configuration file for OIC ADEI Analytics test suite
"""
import pytest
import sys
import os

# Add parent directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test configuration
pytest_plugins = []

# Test markers
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "visual: marks tests as visual parity tests"
    )

# Skip tests if dependencies are missing
def pytest_runtest_setup(item):
    """Setup function called before each test"""
    try:
        import streamlit
        import plotly
        import pandas
    except ImportError as e:
        pytest.skip(f"Skipping test due to missing dependency: {e}")

# Test collection customization
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names"""
    for item in items:
        # Mark slow tests
        if "rag" in item.name.lower() or "search" in item.name.lower():
            item.add_marker(pytest.mark.slow)
        
        # Mark integration tests
        if "database" in item.name.lower() or "connection" in item.name.lower():
            item.add_marker(pytest.mark.integration)
        
        # Mark visual tests
        if "visual" in item.name.lower() or "chart" in item.name.lower():
            item.add_marker(pytest.mark.visual)
        
        # Mark unit tests (default for others)
        if not any(marker.name in ["slow", "integration", "visual"] for marker in item.iter_markers()):
            item.add_marker(pytest.mark.unit)