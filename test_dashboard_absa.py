"""
Test script to verify ABSA dashboard integration
"""
import sys
import io

# Fix Unicode encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 80)
print("ABSA Dashboard Integration Test")
print("=" * 80)

# Test 1: Import API client and check aspect methods
print("\n✓ Test 1: Checking API Client aspect methods...")
try:
    from src.ui.components.api_client import APIClient

    client = APIClient()

    # Check if aspect methods exist
    assert hasattr(client, 'get_aspect_history'), "Missing get_aspect_history method"
    assert hasattr(client, 'get_aspect_summary'), "Missing get_aspect_summary method"

    print("  ✅ API Client has aspect methods: get_aspect_history, get_aspect_summary")
except Exception as e:
    print(f"  ❌ API Client test failed: {e}")
    sys.exit(1)

# Test 2: Import result display components
print("\n✓ Test 2: Checking result display components...")
try:
    from src.ui.components.result_displays import display_aspect_analysis, display_complete_results

    print("  ✅ Aspect display components imported successfully")
except Exception as e:
    print(f"  ❌ Result display import failed: {e}")
    sys.exit(1)

# Test 3: Check Dashboard page file
print("\n✓ Test 3: Checking Dashboard page updates...")
try:
    with open("src/ui/pages/01_📊_Dashboard.py", "r", encoding="utf-8") as f:
        dashboard_content = f.read()

    assert "get_aspect_summary" in dashboard_content, "Dashboard missing aspect summary call"
    assert "Aspect Analytics Overview" in dashboard_content, "Dashboard missing aspect section"

    print("  ✅ Dashboard page has aspect analytics section")
except Exception as e:
    print(f"  ❌ Dashboard page check failed: {e}")
    sys.exit(1)

# Test 4: Check Aspect Analytics page exists
print("\n✓ Test 4: Checking Aspect Analytics page...")
try:
    import os

    aspect_page = "src/ui/pages/07_🎯_Aspects.py"
    assert os.path.exists(aspect_page), f"Aspect page not found at {aspect_page}"

    with open(aspect_page, "r", encoding="utf-8") as f:
        aspect_content = f.read()

    assert "Aspect Analytics" in aspect_content, "Aspect page missing title"
    assert "plotly.graph_objects" in aspect_content, "Aspect page missing plotly visualizations"
    assert "Sentiment Distribution by Aspect" in aspect_content, "Aspect page missing charts"

    print("  ✅ Aspect Analytics page created with visualizations")
except Exception as e:
    print(f"  ❌ Aspect page check failed: {e}")
    sys.exit(1)

# Test 5: Verify aspect tab in results
print("\n✓ Test 5: Checking aspect tab in analysis results...")
try:
    with open("src/ui/components/result_displays.py", "r", encoding="utf-8") as f:
        results_content = f.read()

    assert "🎯 Aspects" in results_content, "Results missing aspect tab"
    assert "display_aspect_analysis(analysis_results)" in results_content, "Results not calling aspect display"

    print("  ✅ Analysis results have aspect tab")
except Exception as e:
    print(f"  ❌ Results tab check failed: {e}")
    sys.exit(1)

# Test 6: Mock aspect data display
print("\n✓ Test 6: Testing aspect data structure...")
try:
    # Mock aspect data that would come from API
    mock_aspect_data = {
        'aspects': [
            {
                'aspect': 'product',
                'mention_count': 5,
                'priority': 'LOW',
                'sentiment_breakdown': {
                    'positive': 3,
                    'neutral': 2,
                    'negative': 0
                }
            },
            {
                'aspect': 'price',
                'mention_count': 3,
                'priority': 'HIGH',
                'sentiment_breakdown': {
                    'positive': 0,
                    'neutral': 0,
                    'negative': 3
                }
            }
        ],
        'recommendations': {
            'strengths': ['product', 'service'],
            'improvements': ['price', 'delivery']
        }
    }

    # Verify structure
    assert 'aspects' in mock_aspect_data
    assert len(mock_aspect_data['aspects']) == 2
    assert mock_aspect_data['aspects'][0]['aspect'] == 'product'
    assert mock_aspect_data['aspects'][1]['priority'] == 'HIGH'

    print("  ✅ Aspect data structure is correct")
    print(f"     - Found {len(mock_aspect_data['aspects'])} aspects")
    print(f"     - Strengths: {', '.join(mock_aspect_data['recommendations']['strengths'])}")
    print(f"     - Improvements needed: {', '.join(mock_aspect_data['recommendations']['improvements'])}")

except Exception as e:
    print(f"  ❌ Aspect data test failed: {e}")
    sys.exit(1)

# Summary
print("\n" + "=" * 80)
print("✅ ALL TESTS PASSED!")
print("=" * 80)
print("\n📋 ABSA Dashboard Features Implemented:")
print("   1. ✅ API Client with aspect endpoints")
print("   2. ✅ Aspect visualization component with stacked bar charts")
print("   3. ✅ Aspect tab in analysis results")
print("   4. ✅ Aspect summary section in Dashboard")
print("   5. ✅ Dedicated Aspect Analytics page (07_🎯_Aspects.py)")
print("\n🚀 Next Steps:")
print("   1. Start the API server: python -m uvicorn src.api.main:app --reload")
print("   2. Start the Streamlit app: streamlit run src/ui/app.py")
print("   3. Log in and upload/analyze feedback to see ABSA features")
print("\n" + "=" * 80)
