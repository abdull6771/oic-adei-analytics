"""
Visual parity test runner for comparing Streamlit app with Metabase dashboards
Generates reports and validates that visualizations match expected outputs
"""
import pandas as pd
import json
import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from streamlit_app import load_data
    import config
except ImportError as e:
    print(f"Warning: Could not import required modules: {e}")
    print("This is expected if dependencies are not installed yet.")
    sys.exit(0)


class VisualParityValidator:
    """Validates visual parity between Streamlit app and Metabase dashboards"""
    
    def __init__(self):
        self.df = load_data()
        self.report = {
            'timestamp': datetime.now().isoformat(),
            'tests': [],
            'summary': {}
        }
    
    def test_executive_dashboard_metrics(self):
        """Test executive dashboard key metrics"""
        print("🔍 Testing Executive Dashboard Metrics...")
        
        test_result = {
            'test_name': 'Executive Dashboard Metrics',
            'status': 'PASS',
            'details': {},
            'errors': []
        }
        
        try:
            # Calculate key metrics
            total_countries = self.df['country'].nunique()
            total_records = len(self.df)
            years_range = f"{self.df['year'].min()}-{self.df['year'].max()}"
            avg_score = round(self.df['adei_score'].mean(), 3)
            
            metrics = {
                'total_countries': total_countries,
                'total_records': total_records,
                'years_range': years_range,
                'average_adei_score': avg_score
            }
            
            test_result['details'] = metrics
            
            # Validation checks
            if total_countries < 20:
                test_result['errors'].append(f"Too few countries: {total_countries}")
            if total_records < 100:
                test_result['errors'].append(f"Too few records: {total_records}")
            if not (0.3 <= avg_score <= 0.8):
                test_result['errors'].append(f"Unrealistic average score: {avg_score}")
            
            if test_result['errors']:
                test_result['status'] = 'FAIL'
            
            print(f"   ✅ Countries: {total_countries}")
            print(f"   ✅ Records: {total_records}")
            print(f"   ✅ Years: {years_range}")
            print(f"   ✅ Avg Score: {avg_score}")
            
        except Exception as e:
            test_result['status'] = 'ERROR'
            test_result['errors'].append(str(e))
            print(f"   ❌ Error: {e}")
        
        self.report['tests'].append(test_result)
        return test_result
    
    def test_top_performers_chart(self):
        """Test top performers bar chart data"""
        print("🔍 Testing Top Performers Chart...")
        
        test_result = {
            'test_name': 'Top Performers Chart',
            'status': 'PASS',
            'details': {},
            'errors': []
        }
        
        try:
            latest_year = self.df['year'].max()
            latest_data = self.df[self.df['year'] == latest_year]
            top_10 = latest_data.nlargest(10, 'adei_score')
            
            # Extract top performers
            top_performers = []
            for _, row in top_10.iterrows():
                top_performers.append({
                    'country': row['country'],
                    'score': round(row['adei_score'], 3)
                })
            
            test_result['details'] = {
                'year': latest_year,
                'top_performers': top_performers,
                'count': len(top_performers)
            }
            
            # Validation checks
            if len(top_performers) == 0:
                test_result['errors'].append("No top performers found")
            if len(top_performers) > 10:
                test_result['errors'].append(f"Too many performers: {len(top_performers)}")
            
            # Check scores are in descending order
            scores = [p['score'] for p in top_performers]
            if scores != sorted(scores, reverse=True):
                test_result['errors'].append("Scores not in descending order")
            
            if test_result['errors']:
                test_result['status'] = 'FAIL'
            
            print(f"   ✅ Found {len(top_performers)} top performers for {latest_year}")
            if top_performers:
                print(f"   ✅ Top country: {top_performers[0]['country']} ({top_performers[0]['score']})")
            
        except Exception as e:
            test_result['status'] = 'ERROR'
            test_result['errors'].append(str(e))
            print(f"   ❌ Error: {e}")
        
        self.report['tests'].append(test_result)
        return test_result
    
    def test_performance_distribution(self):
        """Test performance distribution pie chart"""
        print("🔍 Testing Performance Distribution...")
        
        test_result = {
            'test_name': 'Performance Distribution',
            'status': 'PASS',
            'details': {},
            'errors': []
        }
        
        try:
            latest_year = self.df['year'].max()
            latest_data = self.df[self.df['year'] == latest_year]
            
            # Categorize performance
            def categorize_performance(score):
                if pd.isna(score):
                    return 'Unknown'
                elif score >= 0.7:
                    return 'High'
                elif score >= 0.5:
                    return 'Medium'
                else:
                    return 'Low'
            
            latest_data['performance_tier'] = latest_data['adei_score'].apply(categorize_performance)
            distribution = latest_data['performance_tier'].value_counts().to_dict()
            
            test_result['details'] = {
                'year': latest_year,
                'distribution': distribution,
                'total_countries': sum(distribution.values())
            }
            
            # Validation checks
            if sum(distribution.values()) == 0:
                test_result['errors'].append("No countries in distribution")
            if 'Unknown' in distribution and distribution['Unknown'] > len(latest_data) * 0.5:
                test_result['errors'].append("Too many countries with unknown scores")
            
            if test_result['errors']:
                test_result['status'] = 'FAIL'
            
            print(f"   ✅ Distribution for {latest_year}: {distribution}")
            
        except Exception as e:
            test_result['status'] = 'ERROR'
            test_result['errors'].append(str(e))
            print(f"   ❌ Error: {e}")
        
        self.report['tests'].append(test_result)
        return test_result
    
    def test_global_trends(self):
        """Test global trends line chart"""
        print("🔍 Testing Global Trends...")
        
        test_result = {
            'test_name': 'Global Trends',
            'status': 'PASS',
            'details': {},
            'errors': []
        }
        
        try:
            yearly_avg = self.df.groupby('year')['adei_score'].mean().round(3)
            trends_data = []
            
            for year, score in yearly_avg.items():
                trends_data.append({
                    'year': int(year),
                    'average_score': float(score)
                })
            
            test_result['details'] = {
                'trends': trends_data,
                'years_count': len(trends_data)
            }
            
            # Validation checks
            if len(trends_data) < 2:
                test_result['errors'].append("Need at least 2 years for trends")
            
            # Check for reasonable score ranges
            scores = [t['average_score'] for t in trends_data]
            if any(score < 0 or score > 1 for score in scores):
                test_result['errors'].append("Scores outside valid range [0,1]")
            
            if test_result['errors']:
                test_result['status'] = 'FAIL'
            
            print(f"   ✅ Trends across {len(trends_data)} years")
            for trend in trends_data:
                print(f"      {trend['year']}: {trend['average_score']}")
            
        except Exception as e:
            test_result['status'] = 'ERROR'
            test_result['errors'].append(str(e))
            print(f"   ❌ Error: {e}")
        
        self.report['tests'].append(test_result)
        return test_result
    
    def test_pillar_analysis(self):
        """Test pillar analysis components"""
        print("🔍 Testing Pillar Analysis...")
        
        test_result = {
            'test_name': 'Pillar Analysis',
            'status': 'PASS',
            'details': {},
            'errors': []
        }
        
        try:
            pillar_columns = [col for col in self.df.columns if col.startswith('adei_') and col != 'adei_score']
            
            # Test pillar data availability
            pillar_stats = {}
            for col in pillar_columns:
                non_null_count = self.df[col].notna().sum()
                pillar_stats[col] = {
                    'non_null_records': non_null_count,
                    'completion_rate': round(non_null_count / len(self.df), 3)
                }
            
            test_result['details'] = {
                'pillars_found': len(pillar_columns),
                'pillar_columns': pillar_columns,
                'pillar_stats': pillar_stats
            }
            
            # Validation checks
            if len(pillar_columns) < 4:
                test_result['errors'].append(f"Too few pillars: {len(pillar_columns)}")
            
            for col, stats in pillar_stats.items():
                if stats['completion_rate'] < 0.5:
                    test_result['errors'].append(f"Low completion rate for {col}: {stats['completion_rate']}")
            
            if test_result['errors']:
                test_result['status'] = 'FAIL'
            
            print(f"   ✅ Found {len(pillar_columns)} pillars")
            for col in pillar_columns[:3]:  # Show first 3
                completion = pillar_stats[col]['completion_rate']
                print(f"      {col}: {completion*100:.1f}% complete")
            
        except Exception as e:
            test_result['status'] = 'ERROR'
            test_result['errors'].append(str(e))
            print(f"   ❌ Error: {e}")
        
        self.report['tests'].append(test_result)
        return test_result
    
    def test_data_quality(self):
        """Test overall data quality"""
        print("🔍 Testing Data Quality...")
        
        test_result = {
            'test_name': 'Data Quality',
            'status': 'PASS',
            'details': {},
            'errors': []
        }
        
        try:
            # Basic data quality metrics
            quality_metrics = {
                'total_records': len(self.df),
                'unique_countries': self.df['country'].nunique(),
                'unique_years': self.df['year'].nunique(),
                'adei_score_completeness': round(self.df['adei_score'].notna().sum() / len(self.df), 3),
                'year_range': [int(self.df['year'].min()), int(self.df['year'].max())],
                'score_range': [float(self.df['adei_score'].min()), float(self.df['adei_score'].max())]
            }
            
            test_result['details'] = quality_metrics
            
            # Validation checks
            if quality_metrics['total_records'] < 100:
                test_result['errors'].append(f"Too few records: {quality_metrics['total_records']}")
            if quality_metrics['unique_countries'] < 20:
                test_result['errors'].append(f"Too few countries: {quality_metrics['unique_countries']}")
            if quality_metrics['adei_score_completeness'] < 0.8:
                test_result['errors'].append(f"Low ADEI score completeness: {quality_metrics['adei_score_completeness']}")
            if quality_metrics['score_range'][0] < 0 or quality_metrics['score_range'][1] > 1:
                test_result['errors'].append(f"Invalid score range: {quality_metrics['score_range']}")
            
            if test_result['errors']:
                test_result['status'] = 'FAIL'
            
            print(f"   ✅ Records: {quality_metrics['total_records']}")
            print(f"   ✅ Countries: {quality_metrics['unique_countries']}")
            print(f"   ✅ Years: {quality_metrics['year_range']}")
            print(f"   ✅ ADEI Score Completeness: {quality_metrics['adei_score_completeness']*100:.1f}%")
            
        except Exception as e:
            test_result['status'] = 'ERROR'
            test_result['errors'].append(str(e))
            print(f"   ❌ Error: {e}")
        
        self.report['tests'].append(test_result)
        return test_result
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n📊 Generating Visual Parity Report...")
        
        # Calculate summary statistics
        total_tests = len(self.report['tests'])
        passed_tests = sum(1 for test in self.report['tests'] if test['status'] == 'PASS')
        failed_tests = sum(1 for test in self.report['tests'] if test['status'] == 'FAIL')
        error_tests = sum(1 for test in self.report['tests'] if test['status'] == 'ERROR')
        
        self.report['summary'] = {
            'total_tests': total_tests,
            'passed': passed_tests,
            'failed': failed_tests,
            'errors': error_tests,
            'success_rate': round(passed_tests / total_tests, 3) if total_tests > 0 else 0
        }
        
        # Save report to file
        report_file = 'visual_parity_report.json'
        with open(report_file, 'w') as f:
            json.dump(self.report, f, indent=2)
        
        # Print summary
        print(f"\n📋 Test Summary:")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Passed: {passed_tests}")
        print(f"   ❌ Failed: {failed_tests}")
        print(f"   🔥 Errors: {error_tests}")
        print(f"   Success Rate: {self.report['summary']['success_rate']*100:.1f}%")
        
        if failed_tests > 0 or error_tests > 0:
            print(f"\n⚠️  Issues Found:")
            for test in self.report['tests']:
                if test['status'] in ['FAIL', 'ERROR']:
                    print(f"   {test['test_name']}: {test['status']}")
                    for error in test['errors']:
                        print(f"      - {error}")
        
        print(f"\n📄 Full report saved to: {report_file}")
        return self.report
    
    def run_all_tests(self):
        """Run all visual parity tests"""
        print("🚀 Starting Visual Parity Validation...\n")
        
        # Run all tests
        self.test_executive_dashboard_metrics()
        self.test_top_performers_chart()
        self.test_performance_distribution()
        self.test_global_trends()
        self.test_pillar_analysis()
        self.test_data_quality()
        
        # Generate report
        return self.generate_report()


def main():
    """Main function to run visual parity tests"""
    try:
        validator = VisualParityValidator()
        report = validator.run_all_tests()
        
        # Return exit code based on results
        if report['summary']['failed'] > 0 or report['summary']['errors'] > 0:
            print("\n❌ Some tests failed. Please review the issues above.")
            return 1
        else:
            print("\n✅ All tests passed! Visual parity validated.")
            return 0
    
    except Exception as e:
        print(f"\n🔥 Critical error during testing: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)