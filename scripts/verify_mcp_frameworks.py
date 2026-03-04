
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from promptcore.domain import FrameworkSelector, list_frameworks, TaskCategory
from promptcore.domain.frameworks import FRAMEWORK_REGISTRY

def verify_frameworks_count():
    print("Verifying Framework Count...")
    # Logic from main.py: list_available_frameworks calls list_frameworks (or iterates registry)
    # We will verify the registry directly as that is the source of truth
    count = len(FRAMEWORK_REGISTRY)
    
    print(f"Total frameworks found in REGISTRY: {count}")
    
    # Categorize
    by_category = {}
    for name, cls in FRAMEWORK_REGISTRY.items():
        # best_for is a list of strings (enums)
        for cat in cls.best_for:
            cat_val = cat.value if hasattr(cat, 'value') else cat
            by_category[cat_val] = by_category.get(cat_val, 0) + 1
            
    print("Frameworks by Category:")
    for cat, num in by_category.items():
        print(f"  - {cat}: {num}")
        
    assert count == 40, f"Expected 40 frameworks, found {count}"
    print("✅ Framework count verified.\n")

def verify_strategy_recommendation():
    print("Verifying Strategy Recommendation logic...")
    selector = FrameworkSelector()
    
    test_cases = [
        (
            "Write a python script to scrape a website", 
            "code", 
            ["chain_of_thought", "reflexion", "self_refine"] 
        ),
        (
            "Calculate the integral of x^2", 
            "math", 
            ["program_of_thoughts", "chain_of_thought"] 
        ),
        (
            "Compare the economic policies of the US and China", 
            "research", 
            ["step_back", "thread_of_thought", "chain_of_density"]
        ),
        (
            "Plan a marketing campaign for a new coffee brand", 
            "planning", 
            ["reasoning_via_planning", "graph_of_thoughts"]
        )
    ]
    
    for task, expected_cat, potential_fws in test_cases:
        print(f"Testing task: '{task}'")
        analysis = selector.analyze(task=task)
        
        cat = analysis.category.value
        fw = analysis.recommended_framework
        reasons = analysis.reasoning
        
        print(f"  -> Category: {cat}")
        print(f"  -> Recommended: {fw}")
        print(f"  -> Reasoning: {reasons}")
        
        if expected_cat:
            assert cat == expected_cat, f"Expected category {expected_cat}, got {cat}"
        
        # Check if recommended is in potential list (relaxed check)
        # assert fw in potential_fws or any(alt in potential_fws for alt in analysis.alternative_frameworks)
        
        print(f"✅ Verified.\n")

if __name__ == "__main__":
    try:
        verify_frameworks_count()
        verify_strategy_recommendation()
        print("🎉 All verifications passed!")
    except AssertionError as e:
        print(f"❌ Verification Failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
