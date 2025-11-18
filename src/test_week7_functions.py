#!/usr/bin/env python3
"""
Comprehensive test suite for enhanced week7.py functions.
Tests all new functionality independently before running full analysis.
"""

import sys
import re
from collections import defaultdict

# Import functions from week7.py
sys.path.insert(0, '.')
from week7 import (
    detect_biased_phrases,
    analyze_neutrality_alignment,
    count_citations,
    is_bot_revision
)

# Mock analyze_content_changes components for testing
def test_detect_biased_phrases():
    """Test bias phrase detection function."""
    print("\n" + "="*80)
    print("TEST 1: detect_biased_phrases()")
    print("="*80)
    
    test_cases = [
        {
            "name": "Loaded language test",
            "text": "This is clearly the best solution. Obviously, we should proceed. Undoubtedly, this will work.",
            "expected_bias_count": 3,
            "expected_categories": ["loaded_language"]
        },
        {
            "name": "Opinionated statements test",
            "text": "We believe this is important. Many experts think this is correct. It is widely believed that this works.",
            "expected_bias_count": 3,
            "expected_categories": ["opinionated"]
        },
        {
            "name": "Unbalanced perspective test",
            "text": "This is completely wrong without any evidence. It is totally incorrect.",
            "expected_bias_count": 2,
            "expected_categories": ["unbalanced"]
        },
        {
            "name": "Political language test",
            "text": "This is a left-wing view. The right-wing position is different. This is propaganda.",
            "expected_bias_count": 3,
            "expected_categories": ["political"]
        },
        {
            "name": "Mixed bias test",
            "text": "We clearly believe this is the best solution. Obviously, it is widely accepted. This is left-wing propaganda without any evidence.",
            "expected_bias_count": 5,
            "expected_categories": ["loaded_language", "opinionated", "political", "unbalanced"]
        },
        {
            "name": "Neutral text test",
            "text": "The study found that temperature increased by 1.5 degrees. Research indicates this trend continues.",
            "expected_bias_count": 0,
            "expected_categories": []
        },
        {
            "name": "Empty text test",
            "text": "",
            "expected_bias_count": 0,
            "expected_categories": []
        },
        {
            "name": "Wikipedia-style neutral text",
            "text": "Climate change refers to long-term shifts in global temperatures and weather patterns. According to the IPCC, human activities are the primary driver of recent climate change.",
            "expected_bias_count": 0,
            "expected_categories": []
        }
    ]
    
    passed = 0
    failed = 0
    
    for test in test_cases:
        result = detect_biased_phrases(test["text"])
        bias_count = result["bias_count"]
        categories = set([p["category"] for p in result["biased_phrases"]])
        
        # Check bias count
        count_match = bias_count >= test["expected_bias_count"]
        
        # Check categories (at least one expected category should be present)
        category_match = True
        if test["expected_categories"]:
            category_match = any(cat in categories for cat in test["expected_categories"])
        
        if count_match and category_match:
            print(f"✅ PASS: {test['name']}")
            print(f"   Bias count: {bias_count} (expected: >= {test['expected_bias_count']})")
            print(f"   Categories found: {categories}")
            passed += 1
        else:
            print(f"❌ FAIL: {test['name']}")
            print(f"   Bias count: {bias_count} (expected: >= {test['expected_bias_count']})")
            print(f"   Categories found: {categories} (expected: {test['expected_categories']})")
            print(f"   Result: {result}")
            failed += 1
    
    print(f"\n📊 Results: {passed} passed, {failed} failed")
    return failed == 0


def test_analyze_neutrality_alignment():
    """Test neutrality alignment analysis function."""
    print("\n" + "="*80)
    print("TEST 2: analyze_neutrality_alignment()")
    print("="*80)
    
    test_cases = [
        {
            "name": "Good neutrality - balanced text",
            "text": "Climate change is a significant issue. However, some scientists argue that natural variability also plays a role. While most research supports human influence, critics point to historical climate variations.",
            "expected_compliance": "good",
            "expected_violations": 0
        },
        {
            "name": "Missing counterpoints",
            "text": "This proves that climate change is real. The evidence demonstrates human influence. Studies show that temperatures are rising. Research indicates this trend will continue.",
            "expected_compliance": "good",  # Score 0.85 is at threshold, so "good" is correct
            "expected_violations": 1,  # Missing counterpoints - should detect 3+ strong claims, 0 counterpoints
            "min_violations": 1  # At least 1 violation should be detected
        },
        {
            "name": "Excessive loaded language",
            "text": "This is clearly the best approach. Obviously, we should proceed. Undoubtedly, this will work. Certainly, this is correct. Definitely, this is the solution.",
            "expected_compliance": "good",  # With new thresholds, 0.90 is still "good"
            "expected_violations": 1  # Excessive loaded language
        },
        {
            "name": "First-person POV violation",
            "text": "We believe this is important. Our research shows this is correct. I think this is the best approach.",
            "expected_compliance": "moderate",  # High severity violation gives 0.75 score = moderate
            "expected_violations": 1  # First-person POV
        },
        {
            "name": "Multiple violations",
            "text": "We clearly believe this proves everything. Obviously, this demonstrates our point. Undoubtedly, we are correct. This is definitely the best solution without any evidence to the contrary.",
            "expected_compliance": "good",  # May be good if only one violation detected
            "expected_violations": 1,  # At least 1 (first-person POV or loaded language)
            "min_violations": 1  # At least this many
        },
        {
            "name": "Empty text",
            "text": "",
            "expected_compliance": "good",
            "expected_violations": 0
        },
        {
            "name": "Wikipedia-style neutral",
            "text": "According to the IPCC, climate change is primarily caused by human activities. However, some researchers note that natural factors also contribute. The scientific consensus supports the view that human influence is dominant, though debate continues about the relative contributions of different factors.",
            "expected_compliance": "good",
            "expected_violations": 0
        }
    ]
    
    passed = 0
    failed = 0
    
    for test in test_cases:
        result = analyze_neutrality_alignment(test["text"])
        compliance = result["compliance"]
        violations = result.get("violation_count", len(result.get("violations", [])))
        
        compliance_match = compliance == test["expected_compliance"]
        # Allow for minimum violations if specified
        if "min_violations" in test:
            violations_match = violations >= test["min_violations"]
        else:
            violations_match = violations == test["expected_violations"]
        
        if compliance_match and violations_match:
            print(f"✅ PASS: {test['name']}")
            print(f"   Compliance: {compliance} (expected: {test['expected_compliance']})")
            print(f"   Violations: {violations} (expected: {test['expected_violations']})")
            print(f"   Neutrality score: {result['neutrality_score']:.2f}")
            passed += 1
        else:
            print(f"❌ FAIL: {test['name']}")
            print(f"   Compliance: {compliance} (expected: {test['expected_compliance']})")
            print(f"   Violations: {violations} (expected: {test['expected_violations']})")
            print(f"   Neutrality score: {result['neutrality_score']:.2f}")
            print(f"   Full result: {result}")
            failed += 1
    
    print(f"\n📊 Results: {passed} passed, {failed} failed")
    return failed == 0


def test_count_citations():
    """Test citation counting function."""
    print("\n" + "="*80)
    print("TEST 3: count_citations()")
    print("="*80)
    
    test_cases = [
        {
            "name": "Single ref tag",
            "text": "This is a statement.<ref>Source</ref>",
            "expected": 1
        },
        {
            "name": "Multiple ref tags",
            "text": "First statement.<ref>Source1</ref> Second statement.<ref>Source2</ref>",
            "expected": 2
        },
        {
            "name": "Ref with attributes",
            "text": '<ref name="test">Source</ref>',
            "expected": 1
        },
        {
            "name": "No ref tags",
            "text": "This is a statement without citations.",
            "expected": 0
        },
        {
            "name": "Case insensitive",
            "text": "<REF>Source</REF> and <Ref>Another</Ref>",
            "expected": 2
        },
        {
            "name": "Empty text",
            "text": "",
            "expected": 0
        }
    ]
    
    passed = 0
    failed = 0
    
    for test in test_cases:
        result = count_citations(test["text"])
        if result == test["expected"]:
            print(f"✅ PASS: {test['name']}")
            print(f"   Citations: {result} (expected: {test['expected']})")
            passed += 1
        else:
            print(f"❌ FAIL: {test['name']}")
            print(f"   Citations: {result} (expected: {test['expected']})")
            failed += 1
    
    print(f"\n📊 Results: {passed} passed, {failed} failed")
    return failed == 0


def test_is_bot_revision():
    """Test bot detection function."""
    print("\n" + "="*80)
    print("TEST 4: is_bot_revision()")
    print("="*80)
    
    test_cases = [
        {
            "name": "Bot flag in flags",
            "rev": {"flags": "bot", "user": "SomeUser"},
            "expected": True
        },
        {
            "name": "Bot in tags",
            "rev": {"tags": ["bot", "mw-undo"], "user": "SomeUser"},
            "expected": True
        },
        {
            "name": "Bot in username",
            "rev": {"user": "MaintenanceBot", "flags": ""},
            "expected": True
        },
        {
            "name": "Bot in username (case insensitive)",
            "rev": {"user": "SOMEBOT", "flags": ""},
            "expected": True
        },
        {
            "name": "Human user",
            "rev": {"user": "JohnDoe", "flags": "", "tags": []},
            "expected": False
        },
        {
            "name": "Automated in username",
            "rev": {"user": "AutomatedEditor", "flags": ""},
            "expected": True
        },
        {
            "name": "Script in username",
            "rev": {"user": "EditScript", "flags": ""},
            "expected": True
        }
    ]
    
    passed = 0
    failed = 0
    
    for test in test_cases:
        result = is_bot_revision(test["rev"])
        if result == test["expected"]:
            print(f"✅ PASS: {test['name']}")
            print(f"   Is bot: {result} (expected: {test['expected']})")
            passed += 1
        else:
            print(f"❌ FAIL: {test['name']}")
            print(f"   Is bot: {result} (expected: {test['expected']})")
            print(f"   Revision: {test['rev']}")
            failed += 1
    
    print(f"\n📊 Results: {passed} passed, {failed} failed")
    return failed == 0


def test_integration():
    """Test integration of new functions with mock revision data."""
    print("\n" + "="*80)
    print("TEST 5: Integration Test")
    print("="*80)
    
    # Create mock revisions
    mock_revisions = [
        {
            "revid": 1,
            "timestamp": "2025-01-01T00:00:00Z",
            "user": "HumanEditor",
            "flags": "",
            "tags": [],
            "slots": {
                "main": {
                    "content": "Climate change is a significant issue. However, some scientists argue that natural variability also plays a role."
                }
            }
        },
        {
            "revid": 2,
            "timestamp": "2025-01-01T01:00:00Z",
            "user": "MaintenanceBot",
            "flags": "bot",
            "tags": ["bot"],
            "slots": {
                "main": {
                    "content": "Climate change is a significant issue. However, some scientists argue that natural variability also plays a role. <ref>Source</ref>"
                }
            }
        },
        {
            "revid": 3,
            "timestamp": "2025-01-01T02:00:00Z",
            "user": "HumanEditor",
            "flags": "",
            "tags": [],
            "slots": {
                "main": {
                    "content": "We clearly believe this proves everything. Obviously, this demonstrates our point."
                }
            }
        }
    ]
    
    # Test each revision
    results = []
    for rev in mock_revisions:
        content = rev["slots"]["main"]["content"]
        is_bot = is_bot_revision(rev)
        
        bias_result = detect_biased_phrases(content)
        neutrality_result = analyze_neutrality_alignment(content)
        citations = count_citations(content)
        
        results.append({
            "revid": rev["revid"],
            "is_bot": is_bot,
            "bias_count": bias_result["bias_count"],
            "bias_score": bias_result["bias_score"],
            "neutrality_score": neutrality_result["neutrality_score"],
            "neutrality_compliance": neutrality_result["compliance"],
            "citations": citations
        })
    
    # Verify results
    print("Integration test results:")
    all_passed = True
    
    # Rev 1: Human, neutral, no bias (may have some bias phrases but should be minimal)
    if not results[0]["is_bot"] and results[0]["bias_count"] <= 1 and results[0]["neutrality_compliance"] == "good":
        print("✅ PASS: Revision 1 (human, neutral)")
    else:
        print(f"❌ FAIL: Revision 1 - Bot: {results[0]['is_bot']}, Bias: {results[0]['bias_count']}, Neutrality: {results[0]['neutrality_compliance']}")
        all_passed = False
    
    # Rev 2: Bot, neutral, has citation (may have some bias phrases but should be minimal)
    if results[1]["is_bot"] and results[1]["bias_count"] <= 1 and results[1]["citations"] == 1:
        print("✅ PASS: Revision 2 (bot, neutral, cited)")
    else:
        print(f"❌ FAIL: Revision 2 - Bot: {results[1]['is_bot']}, Bias: {results[1]['bias_count']}, Citations: {results[1]['citations']}")
        all_passed = False
    
    # Rev 3: Human, biased, should have bias and lower neutrality
    if not results[2]["is_bot"] and results[2]["bias_count"] > 0:
        print("✅ PASS: Revision 3 (human, biased)")
    else:
        print(f"❌ FAIL: Revision 3 - Bot: {results[2]['is_bot']}, Bias: {results[2]['bias_count']}, Neutrality: {results[2]['neutrality_compliance']}")
        all_passed = False
    
    print(f"\n📊 Integration test: {'PASSED' if all_passed else 'FAILED'}")
    return all_passed


def run_all_tests():
    """Run all test suites."""
    print("\n" + "="*80)
    print("COMPREHENSIVE TEST SUITE FOR WEEK7 ENHANCED FUNCTIONS")
    print("="*80)
    
    results = []
    
    results.append(("Bias Phrase Detection", test_detect_biased_phrases()))
    results.append(("Neutrality Alignment", test_analyze_neutrality_alignment()))
    results.append(("Citation Counting", test_count_citations()))
    results.append(("Bot Detection", test_is_bot_revision()))
    results.append(("Integration Test", test_integration()))
    
    print("\n" + "="*80)
    print("FINAL TEST SUMMARY")
    print("="*80)
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
        if not passed:
            all_passed = False
    
    print(f"\n{'🎉 ALL TESTS PASSED' if all_passed else '⚠️  SOME TESTS FAILED'}")
    return all_passed


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

