"""
Test ABSA End-to-End to identify the exact data structure issue
"""
import sys
import io
import json

# Fix Unicode encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 80)
print("ABSA END-TO-END STRUCTURE TEST")
print("=" * 80)

# Test 1: ABSA Processor output
print("\n📋 Step 1: Testing ABSA Processor directly...")
from src.services.absa_processor import get_absa_analyzer

analyzer = get_absa_analyzer()

test_feedback = [
    "The product quality is excellent but the price is too high.",
    "Delivery was slow and customer service was helpful."
]

absa_raw = analyzer.analyze_batch(test_feedback)

print(f"\n✓ ABSA Processor returned {absa_raw['total_aspects']} aspects")
print(f"  Structure keys: {list(absa_raw.keys())}")
print(f"  Aspects dict keys: {list(absa_raw['aspects'].keys())}")

# Test 2: Analysis Agent output
print("\n📋 Step 2: Testing Analysis Agent...")
from src.agents.analysis_agent import AnalysisAgent

agent = AnalysisAgent()
analysis_result = agent.analyze(test_feedback, include_topics=False, include_emotions=True, include_absa=True)

print(f"\n✓ Analysis Agent returned")
print(f"  Top-level keys: {list(analysis_result.keys())}")

if 'aspects' in analysis_result:
    aspects_data = analysis_result['aspects']
    print(f"  Type of 'aspects': {type(aspects_data)}")
    print(f"  'aspects' keys: {list(aspects_data.keys()) if isinstance(aspects_data, dict) else 'Not a dict!'}")

    if isinstance(aspects_data, dict) and 'aspects' in aspects_data:
        inner_aspects = aspects_data['aspects']
        print(f"  Type of nested 'aspects': {type(inner_aspects)}")
        if isinstance(inner_aspects, dict):
            print(f"  Nested aspect names: {list(inner_aspects.keys())[:5]}")

            # Show one example aspect structure
            if inner_aspects:
                first_aspect_name = list(inner_aspects.keys())[0]
                first_aspect_data = inner_aspects[first_aspect_name]
                print(f"\n  Example aspect '{first_aspect_name}':")
                print(f"    {json.dumps(first_aspect_data, indent=6)}")
else:
    print("  ❌ No 'aspects' key found!")

# Test 3: What format does the frontend expect?
print("\n" + "=" * 80)
print("EXPECTED vs ACTUAL FORMAT")
print("=" * 80)

print("\n📌 Frontend expects (from result_displays.py line 342-348):")
print("""
{
  'aspects': {
    'aspects': [                    <-- LIST of aspect dicts
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
      ...
    ],
    'recommendations': {...}
  }
}
""")

print("\n📌 Backend currently returns:")
if 'aspects' in analysis_result:
    aspects_data = analysis_result['aspects']
    if isinstance(aspects_data, dict) and 'aspects' in aspects_data:
        inner = aspects_data['aspects']
        print(f"\n{{'aspects': {{'aspects': {type(inner).__name__}, ...}}}}")

        if isinstance(inner, dict):
            print("\n❌ PROBLEM FOUND!")
            print(f"   Backend returns: dict with {len(inner)} aspect names as keys")
            print(f"   Frontend expects: list of aspect dicts")
            print(f"\n   Backend format:")
            print(f"   {{'product': {{'sentiment_breakdown': ..., 'mention_count': ...}}, 'price': {{...}}}}")
            print(f"\n   Frontend expects:")
            print(f"   [")
            print(f"     {{'aspect': 'product', 'sentiment_breakdown': ..., 'mention_count': ...}},")
            print(f"     {{'aspect': 'price', 'sentiment_breakdown': ..., 'mention_count': ...}}")
            print(f"   ]")

print("\n" + "=" * 80)
print("SOLUTION NEEDED")
print("=" * 80)
print("""
The ABSA processor returns aspects as a DICT (aspect_name: stats),
but the frontend expects a LIST of dicts with 'aspect' key.

Fix needed in: src/agents/analysis_agent.py
Transform the dict to a list before returning.
""")
