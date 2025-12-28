"""
Test Topic Modeling Improvements - Verify Stopwords Filtering and Quality
"""
import sys
import io

# Fix Unicode encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 80)
print("TOPIC MODELING IMPROVEMENTS TEST")
print("=" * 80)

# Load the comprehensive test feedback
from pathlib import Path

feedback_file = Path("COMPREHENSIVE_TEST_FEEDBACK.md")
if feedback_file.exists():
    content = feedback_file.read_text(encoding='utf-8')
    # Extract feedback items (lines starting with numbers)
    test_feedback = []
    for line in content.split('\n'):
        if line.strip() and line[0].isdigit() and '. ' in line:
            # Extract text after "N. "
            feedback_text = line.split('. ', 1)[1].strip()
            test_feedback.append(feedback_text)
else:
    print("⚠️ COMPREHENSIVE_TEST_FEEDBACK.md not found, using inline feedback")
    test_feedback = [
        "The product quality is excellent and materials are top-notch.",
        "Great build quality but a bit expensive for what you get.",
        "Amazing product! Worth every penny. Highly recommended.",
        "Delivery took forever. Package arrived 2 weeks late!",
        "Shipping was incredibly slow. Very disappointed with delivery time.",
        "Fast delivery! Arrived in just 2 days, well packaged.",
        "Customer service was fantastic. They resolved my issue immediately.",
        "Support team is helpful and responsive. Great service!",
        "Terrible customer service. No one responded to my emails.",
        "The interface is confusing and hard to navigate.",
        "Very difficult to use. Not user-friendly at all.",
        "Performance is lightning fast. No lag whatsoever!"
    ]

print(f"\n📋 Testing with {len(test_feedback)} feedback items\n")

# Test the topic modeler directly
print("🔍 Step 1: Testing TopicModeler directly...")
from src.services.nlp_processors import get_topic_modeler

modeler = get_topic_modeler()

print(f"   ✓ TopicModeler initialized")
print(f"   ✓ Min topic size: {modeler.min_topic_size}")
print(f"   ✓ Max topics: {modeler.max_topics}")
print(f"   ✓ Stopwords filtering: {'english' if hasattr(modeler.vectorizer_model, 'stop_words') else 'NONE'}")
print(f"   ✓ UMAP n_neighbors: {modeler.umap_model.n_neighbors}")
print(f"   ✓ HDBSCAN min_cluster_size: {modeler.hdbscan_model.min_cluster_size}")

# Extract topics
topics_result = modeler.extract_topics(test_feedback, min_texts=3)

print(f"\n📊 Topic Modeling Results:")
print(f"   Total topics: {topics_result['num_topics']}")
print(f"   Total documents: {len(test_feedback)}")

if 'outlier_count' in topics_result:
    outlier_pct = (topics_result['outlier_count'] / len(test_feedback)) * 100
    print(f"   Outliers: {topics_result['outlier_count']} ({outlier_pct:.1f}%)")

print("\n🏷️ Topic Details:\n")

for i, topic in enumerate(topics_result['topics'], 1):
    print(f"Topic {i}: ID={topic['topic_id']}")
    print(f"   Documents: {topic['count']}")
    print(f"   Keywords: {', '.join(topic['keywords'][:5])}")

    if 'representative_docs' in topic:
        print(f"   Examples:")
        for doc in topic['representative_docs'][:2]:
            print(f"      - \"{doc[:60]}...\"")
    print()

# Check for stopwords in keywords
print("\n🔍 Quality Check:")
stopwords_found = []
common_stopwords = {'to', 'the', 'and', 'a', 'an', 'is', 'was', 'were', 'of', 'in', 'on', 'at', 'for'}

for topic in topics_result['topics']:
    for keyword in topic['keywords'][:5]:
        if keyword.lower() in common_stopwords:
            stopwords_found.append((topic['topic_id'], keyword))

if stopwords_found:
    print(f"   ⚠️ Found {len(stopwords_found)} stopwords in topic keywords:")
    for topic_id, word in stopwords_found[:5]:
        print(f"      Topic {topic_id}: '{word}'")
else:
    print("   ✅ No common stopwords found in topic keywords!")

# Check outlier rate
outlier_pct = 0
if 'outlier_count' in topics_result:
    outlier_pct = (topics_result['outlier_count'] / len(test_feedback)) * 100
    if outlier_pct > 30:
        print(f"   ⚠️ High outlier rate: {outlier_pct:.1f}% (target: <20%)")
    else:
        print(f"   ✅ Good outlier rate: {outlier_pct:.1f}%")
else:
    print(f"   ✅ No outliers detected (0.0%)")

print("\n" + "=" * 80)
print("EXPECTED vs ACTUAL")
print("=" * 80)

print("\n✅ Expected (4-5 topics):")
print("   1. Product Quality (quality, product, materials, build)")
print("   2. Delivery Issues (delivery, shipping, late, slow)")
print("   3. Customer Service (service, support, customer, help)")
print("   4. Usability (interface, difficult, confusing, user)")
print("   5. Performance (fast, performance, speed)")

print(f"\n📌 Actual ({topics_result['num_topics']} topics):")
for i, topic in enumerate(topics_result['topics'], 1):
    keywords = ', '.join(topic['keywords'][:5])
    print(f"   {i}. Topic {topic['topic_id']} ({topic['count']} docs): {keywords}")

print("\n" + "=" * 80)
if topics_result['num_topics'] >= 4 and not stopwords_found and outlier_pct < 30:
    print("✅ TOPIC MODELING QUALITY: GOOD")
    print("   - Multiple meaningful topics detected")
    print("   - No stopwords in keywords")
    print("   - Low outlier rate")
else:
    print("⚠️ TOPIC MODELING QUALITY: NEEDS IMPROVEMENT")
    if topics_result['num_topics'] < 4:
        print("   - Too few topics detected")
    if stopwords_found:
        print("   - Stopwords present in keywords")
    if outlier_pct >= 30:
        print("   - High outlier rate")

print("=" * 80)
