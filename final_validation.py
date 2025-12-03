"""
FINAL VALIDATION SUITE
Comprehensive testing before production deployment
"""

import sys
import json
from datetime import datetime

print("\n" + "="*80)
print("FINAL VALIDATION & CODE REVIEW SUITE")
print("="*80)

# ============================================================================
# PHASE 1: SYNTAX & IMPORT VALIDATION
# ============================================================================

print("\n📋 PHASE 1: SYNTAX & IMPORT VALIDATION")
print("-" * 80)

errors = []
warnings = []

# TEST 1.1: Import all modules
print("\n✓ TEST 1.1: Module Imports")
try:
    import hash_chain
    print("  ✓ hash_chain.py imports successfully")
except Exception as e:
    errors.append(f"hash_chain.py import failed: {e}")
    print(f"  ✗ FAILED: {e}")

try:
    import data_ingestion
    print("  ✓ data_ingestion.py imports successfully")
except Exception as e:
    errors.append(f"data_ingestion.py import failed: {e}")
    print(f"  ✗ FAILED: {e}")

try:
    import api
    print("  ✓ api.py imports successfully")
except Exception as e:
    errors.append(f"api.py import failed: {e}")
    print(f"  ✗ FAILED: {e}")

try:
    import main
    print("  ✓ main.py imports successfully")
except Exception as e:
    errors.append(f"main.py import failed: {e}")
    print(f"  ✗ FAILED: {e}")

# ============================================================================
# PHASE 2: UNIT TEST VALIDATION
# ============================================================================

print("\n📋 PHASE 2: UNIT TEST VALIDATION")
print("-" * 80)

from hash_chain import (
    LLMSummaryGenerator, Amendment, ChainNode, HashChain,
    RateLimiter, APIKeyManager, AuditLogger, DigitalSigner,
    BackupManager, HealthMonitor, ProductionConfig
)

test_results = {}

# TEST 2.1: LLMSummaryGenerator
print("\n✓ TEST 2.1: LLMSummaryGenerator")
try:
    llm = LLMSummaryGenerator()
    assert llm.api_key is None
    assert llm.use_real_llm == False
    
    test_text = "Artykuł 1: Niniejszym ustawą osoby powinni mieć prawo."
    simplified = llm.simplify(test_text)
    assert isinstance(simplified, str)
    assert len(simplified) > 0
    
    # Test with invalid input
    result = llm.simplify(123)
    assert "Error" in result
    
    test_results['LLMSummaryGenerator'] = True
    print("  ✓ LLMSummaryGenerator passed all checks")
except Exception as e:
    test_results['LLMSummaryGenerator'] = False
    errors.append(f"LLMSummaryGenerator failed: {e}")
    print(f"  ✗ FAILED: {e}")

# TEST 2.2: Amendment
print("\n✓ TEST 2.2: Amendment")
try:
    # Valid amendment
    amendment = Amendment(
        content="Test content",
        change_type="substantive",
        author="Test Author"
    )
    assert amendment.content == "Test content"
    assert amendment.change_type == "substantive"
    assert amendment.author == "Test Author"
    assert hasattr(amendment, 'timestamp')
    assert hasattr(amendment, 'summary')
    
    # Test to_dict
    dict_data = amendment.to_dict()
    assert 'content' in dict_data
    assert 'change_type' in dict_data
    assert 'author' in dict_data
    assert 'summary' in dict_data
    assert 'timestamp' in dict_data
    
    # Test validation - empty content
    try:
        bad_amendment = Amendment("", "substantive", "Author")
        errors.append("Amendment should reject empty content")
    except ValueError:
        pass  # Expected
    
    # Test validation - invalid change_type
    try:
        bad_amendment = Amendment("Content", "invalid", "Author")
        errors.append("Amendment should reject invalid change_type")
    except ValueError:
        pass  # Expected
    
    # Test validation - empty author
    try:
        bad_amendment = Amendment("Content", "substantive", "")
        errors.append("Amendment should reject empty author")
    except ValueError:
        pass  # Expected
    
    test_results['Amendment'] = True
    print("  ✓ Amendment passed all checks")
except Exception as e:
    test_results['Amendment'] = False
    errors.append(f"Amendment failed: {e}")
    print(f"  ✗ FAILED: {e}")

# TEST 2.3: ChainNode & Hashing
print("\n✓ TEST 2.3: ChainNode & Hashing")
try:
    amendment = Amendment("Test", "substantive", "Author")
    node = ChainNode(amendment, parent_hash=None)
    
    assert hasattr(node, 'hash')
    assert len(node.hash) == 64  # SHA-256
    assert node.parent_hash is None
    assert node.verify() == True
    
    # Test with parent
    node2 = ChainNode(amendment, parent_hash=node.hash)
    assert node2.parent_hash == node.hash
    assert node2.verify() == True
    
    # Test invalid amendment
    try:
        bad_node = ChainNode("not an amendment")
        errors.append("ChainNode should reject non-Amendment objects")
    except TypeError:
        pass  # Expected
    
    test_results['ChainNode'] = True
    print("  ✓ ChainNode & Hashing passed all checks")
except Exception as e:
    test_results['ChainNode'] = False
    errors.append(f"ChainNode failed: {e}")
    print(f"  ✗ FAILED: {e}")

# TEST 2.4: HashChain
print("\n✓ TEST 2.4: HashChain")
try:
    chain = HashChain("ACT-001", "Test Act")
    assert chain.act_id == "ACT-001"
    assert chain.act_title == "Test Act"
    assert len(chain.chain) == 0
    
    # Add amendment
    amendment = Amendment("Test", "substantive", "Author")
    hash1 = chain.add_amendment(amendment)
    assert len(chain.chain) == 1
    assert isinstance(hash1, str)
    
    # Add second amendment
    amendment2 = Amendment("Test 2", "substantive", "Author 2")
    hash2 = chain.add_amendment(amendment2)
    assert len(chain.chain) == 2
    assert hash1 != hash2
    
    # Test parent linking
    assert chain.chain[1].parent_hash == chain.chain[0].hash
    
    # Get history
    history = chain.get_history()
    assert len(history) == 2
    assert history[0]['version'] == 1
    assert history[1]['version'] == 2
    
    # Verify integrity
    is_valid = chain.verify_integrity()
    assert is_valid == True
    
    # Test invalid inputs
    try:
        chain.add_amendment("not an amendment")
        errors.append("HashChain should reject non-Amendment objects")
    except TypeError:
        pass  # Expected
    
    test_results['HashChain'] = True
    print("  ✓ HashChain passed all checks")
except Exception as e:
    test_results['HashChain'] = False
    errors.append(f"HashChain failed: {e}")
    print(f"  ✗ FAILED: {e}")

# ============================================================================
# PHASE 3: SECURITY VALIDATION
# ============================================================================

print("\n📋 PHASE 3: SECURITY VALIDATION")
print("-" * 80)

# TEST 3.1: RateLimiter
print("\n✓ TEST 3.1: RateLimiter")
try:
    limiter = RateLimiter(max_requests=3, window_seconds=60)
    
    assert limiter.is_allowed("client1") == True
    assert limiter.is_allowed("client1") == True
    assert limiter.is_allowed("client1") == True
    assert limiter.is_allowed("client1") == False
    
    assert limiter.get_remaining("client1") == 0
    assert limiter.get_remaining("client2") == 3
    
    test_results['RateLimiter'] = True
    print("  ✓ RateLimiter passed all checks")
except Exception as e:
    test_results['RateLimiter'] = False
    errors.append(f"RateLimiter failed: {e}")
    print(f"  ✗ FAILED: {e}")

# TEST 3.2: APIKeyManager
print("\n✓ TEST 3.2: APIKeyManager")
try:
    api_mgr = APIKeyManager()
    
    key = api_mgr.create_key("test", ['read', 'write'])
    assert isinstance(key, str)
    assert len(key) == 64
    
    assert api_mgr.verify_key(key) == True
    assert api_mgr.has_permission(key, 'read') == True
    assert api_mgr.has_permission(key, 'write') == True
    assert api_mgr.has_permission(key, 'admin') == False
    
    api_mgr.revoke_key(key)
    assert api_mgr.verify_key(key) == False
    
    test_results['APIKeyManager'] = True
    print("  ✓ APIKeyManager passed all checks")
except Exception as e:
    test_results['APIKeyManager'] = False
    errors.append(f"APIKeyManager failed: {e}")
    print(f"  ✗ FAILED: {e}")

# TEST 3.3: DigitalSigner
print("\n✓ TEST 3.3: DigitalSigner")
try:
    signer = DigitalSigner("test-key")
    
    test_data = {'content': 'test', 'author': 'me'}
    signature = signer.sign_amendment(test_data)
    
    assert isinstance(signature, str)
    assert len(signature) == 64
    
    assert signer.verify_signature(test_data, signature) == True
    
    # Test with modified data
    modified_data = {'content': 'modified', 'author': 'me'}
    assert signer.verify_signature(modified_data, signature) == False
    
    test_results['DigitalSigner'] = True
    print("  ✓ DigitalSigner passed all checks")
except Exception as e:
    test_results['DigitalSigner'] = False
    errors.append(f"DigitalSigner failed: {e}")
    print(f"  ✗ FAILED: {e}")

# ============================================================================
# PHASE 4: INTEGRATION VALIDATION
# ============================================================================

print("\n📋 PHASE 4: INTEGRATION VALIDATION")
print("-" * 80)

# TEST 4.1: End-to-end workflow
print("\n✓ TEST 4.1: End-to-End Workflow")
try:
    llm = LLMSummaryGenerator()
    chain = HashChain("ACT-FINAL", "Final Test Act", llm_generator=llm)
    
    # Create amendments
    amendments = [
        Amendment(f"Amendment {i}: Artykuł 1: Niniejszym ustawą", 
                 "substantive", f"Author {i}", llm_generator=llm)
        for i in range(5)
    ]
    
    # Add to chain
    hashes = []
    for amendment in amendments:
        h = chain.add_amendment(amendment)
        hashes.append(h)
    
    assert len(chain.chain) == 5
    
    # Verify all hashes are unique
    assert len(set(hashes)) == 5
    
    # Verify integrity
    assert chain.verify_integrity() == True
    
    # Get history
    history = chain.get_history()
    assert len(history) == 5
    
    test_results['End-to-End'] = True
    print("  ✓ End-to-end workflow passed all checks")
except Exception as e:
    test_results['End-to-End'] = False
    errors.append(f"End-to-end workflow failed: {e}")
    print(f"  ✗ FAILED: {e}")

# ============================================================================
# PHASE 5: CODE QUALITY CHECKS
# ============================================================================

print("\n📋 PHASE 5: CODE QUALITY CHECKS")
print("-" * 80)

# TEST 5.1: Documentation
print("\n✓ TEST 5.1: Documentation")
try:
    doc_checks = {
        'LLMSummaryGenerator': bool(LLMSummaryGenerator.__doc__),
        'Amendment': bool(Amendment.__doc__),
        'ChainNode': bool(ChainNode.__doc__),
        'HashChain': bool(HashChain.__doc__),
        'RateLimiter': bool(RateLimiter.__doc__),
        'APIKeyManager': bool(APIKeyManager.__doc__),
        'DigitalSigner': bool(DigitalSigner.__doc__),
    }
    
    missing_docs = [k for k, v in doc_checks.items() if not v]
    
    if missing_docs:
        warnings.append(f"Missing docstrings: {missing_docs}")
    
    print(f"  ✓ Documentation check complete ({len(doc_checks)-len(missing_docs)}/{len(doc_checks)} documented)")
except Exception as e:
    print(f"  ⚠️  Warning: {e}")

# TEST 5.2: Type hints
print("\n✓ TEST 5.2: Type Hints")
try:
    import inspect
    
    classes = [
        LLMSummaryGenerator, Amendment, ChainNode, HashChain,
        RateLimiter, APIKeyManager, DigitalSigner, BackupManager
    ]
    
    type_hints_count = 0
    for cls in classes:
        for method_name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
            sig = inspect.signature(method)
            if sig.return_annotation != inspect.Signature.empty:
                type_hints_count += 1
    
    print(f"  ✓ Type hints found in {type_hints_count} method signatures")
except Exception as e:
    warnings.append(f"Type hints check: {e}")

# ============================================================================
# PHASE 6: PERFORMANCE VALIDATION
# ============================================================================

print("\n📋 PHASE 6: PERFORMANCE VALIDATION")
print("-" * 80)

# TEST 6.1: Performance under load
print("\n✓ TEST 6.1: Performance Under Load")
try:
    import time
    
    llm = LLMSummaryGenerator()
    chain = HashChain("ACT-PERF", "Performance Test", llm_generator=llm)
    
    start = time.time()
    
    for i in range(1000):
        amendment = Amendment(
            content=f"Amendment {i}",
            change_type="substantive",
            author=f"Author {i}",
            summary=f"Summary {i}"
        )
        chain.add_amendment(amendment)
    
    elapsed = time.time() - start
    avg_per_amendment = (elapsed / 1000) * 1000  # ms
    
    if avg_per_amendment < 10:
        print(f"  ✓ Performance excellent: {avg_per_amendment:.2f}ms per amendment")
    elif avg_per_amendment < 50:
        print(f"  ✓ Performance good: {avg_per_amendment:.2f}ms per amendment")
    else:
        warnings.append(f"Performance may need optimization: {avg_per_amendment:.2f}ms per amendment")
    
    # Verify integrity still works
    assert chain.verify_integrity() == True
    print(f"  ✓ Chain integrity verified after 1000 amendments")
    
except Exception as e:
    errors.append(f"Performance test failed: {e}")
    print(f"  ✗ FAILED: {e}")

# ============================================================================
# FINAL REPORT
# ============================================================================

print("\n" + "="*80)
print("FINAL VALIDATION REPORT")
print("="*80)

print("\n✅ TEST RESULTS:")
passed = sum(1 for v in test_results.values() if v)
failed = sum(1 for v in test_results.values() if not v)
print(f"   Passed: {passed}/{len(test_results)}")
print(f"   Failed: {failed}/{len(test_results)}")

if errors:
    print(f"\n❌ ERRORS ({len(errors)}):")
    for error in errors:
        print(f"   - {error}")
else:
    print(f"\n✅ NO ERRORS FOUND")

if warnings:
    print(f"\n⚠️  WARNINGS ({len(warnings)}):")
    for warning in warnings:
        print(f"   - {warning}")
else:
    print(f"\n✅ NO WARNINGS")

# Final verdict
print("\n" + "="*80)
if not errors and failed == 0:
    print("✅ READY FOR PRODUCTION DEPLOYMENT")
    print("="*80 + "\n")
    sys.exit(0)
elif failed < len(test_results) * 0.1 and not errors:
    print("⚠️  READY WITH MINOR ISSUES (see warnings above)")
    print("="*80 + "\n")
    sys.exit(0)
else:
    print("❌ NOT READY FOR DEPLOYMENT - Fix errors above first")
    print("="*80 + "\n")
    sys.exit(1)
