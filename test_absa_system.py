"""Test ABSA system end-to-end."""

import sys
import io

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from src.services.absa_processor import get_absa_analyzer

# Test feedback samples
test_feedbacks = [
    "Great product quality but terrible delivery service. The item itself is amazing but shipping took forever.",
    "Love the design and performance. Fast and responsive. However, the price is a bit high.",
    "Customer support was unhelpful. Product quality is good though.",
    "Excellent value for money! Fast delivery and great features.",
    "The interface is confusing and not user-friendly. Performance is slow too."
]

print("=" * 80)
print("ABSA SYSTEM END-TO-END TEST")
print("=" * 80)

print(f"\n📝 Testing with {len(test_feedbacks)} feedback samples\n")

try:
    # Initialize ABSA analyzer
    print("Initializing ABSA analyzer...")
    absa_analyzer = get_absa_analyzer()
    print("✓ ABSA analyzer ready\n")

    # Analyze batch
    print("Running batch analysis...")
    results = absa_analyzer.analyze_batch(test_feedbacks)
    print("✓ Analysis complete\n")

    # Display results
    print("=" * 80)
    print("ABSA ANALYSIS RESULTS")
    print("=" * 80)

    aspects = results.get("aspects", {})
    summary = results.get("summary", {})

    print(f"\n📊 Total Aspects Found: {results.get('total_aspects', 0)}")
    print(f"📍 Total Mentions: {results.get('total_mentions', 0)}")

    print("\n" + "="*80)
    print("ASPECT SENTIMENT BREAKDOWN")
    print("=" * 80)

    for aspect, stats in aspects.items():
        breakdown = stats.get("sentiment_breakdown", {})
        mention_count = stats.get("mention_count", 0)
        priority = stats.get("priority", "")

        total = sum(breakdown.values())
        if total == 0:
            continue

        # Calculate percentages
        pos_pct = (breakdown.get("positive", 0) / total) * 100
        neu_pct = (breakdown.get("neutral", 0) / total) * 100
        neg_pct = (breakdown.get("negative", 0) / total) * 100

        # Priority indicator
        priority_icon = "🚨" if priority == "high" else "⚠️" if priority == "medium" else "✅"

        print(f"\n{priority_icon} {aspect.upper()} ({mention_count} mentions) - Priority: {priority.upper()}")
        print(f"   Positive: {breakdown.get('positive', 0):2d} ({pos_pct:5.1f}%) {'█' * int(pos_pct/5)}")
        print(f"   Neutral:  {breakdown.get('neutral', 0):2d} ({neu_pct:5.1f}%) {'█' * int(neu_pct/5)}")
        print(f"   Negative: {breakdown.get('negative', 0):2d} ({neg_pct:5.1f}%) {'█' * int(neg_pct/5)}")

        # Show example mentions
        examples = stats.get("example_mentions", [])[:2]
        if examples:
            print(f"   Examples:")
            for ex in examples:
                sentiment_emoji = "👍" if ex["sentiment"] == "positive" else "👎" if ex["sentiment"] == "negative" else "➡️"
                print(f"      {sentiment_emoji} \"{ex['text'][:60]}...\"")

    print("\n" + "="*80)
    print("SUMMARY INSIGHTS")
    print("=" * 80)

    # Top positive aspects
    top_positive = summary.get("top_positive_aspects", [])
    if top_positive:
        print(f"\n✅ Top Strengths: {', '.join(top_positive[:3])}")

    # Top negative aspects
    top_negative = summary.get("top_negative_aspects", [])
    if top_negative:
        print(f"❌ Areas Needing Attention: {', '.join(top_negative[:3])}")

    # Recommendations
    recommendations = summary.get("priority_recommendations", [])
    if recommendations:
        print("\n" + "="*80)
        print("PRIORITY RECOMMENDATIONS")
        print("=" * 80)

        for i, rec in enumerate(recommendations[:5], 1):
            priority_icon = "🚨" if rec["priority"] == "HIGH" else "⚠️"
            print(f"\n{i}. {priority_icon} {rec['priority']} PRIORITY: {rec['aspect']}")
            print(f"   Action: {rec['action']}")
            print(f"   Impact: {rec['impact']}")

    print("\n" + "="*80)
    print("✅ ABSA TEST COMPLETED SUCCESSFULLY!")
    print("=" * 80)

except Exception as e:
    print(f"\n❌ TEST FAILED: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
