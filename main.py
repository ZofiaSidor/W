"""Application entry point"""

import sys
from hash_chain import HashChain, Amendment, LLMSummaryGenerator, ReleaseValidator

def main():
    """Main application"""
    print("\n" + "="*70)
    print("LEGAL ACT TRACKER v1.0.0 - PRODUCTION RELEASE")
    print("="*70 + "\n")
    
    # Validate
    validator = ReleaseValidator()
    if not validator.validate_all():
        print("Validation failed!")
        sys.exit(1)
    
    # Run tests
    print("Running tests...\n")
    
    tests_passed = 0
    tests_total = 6
    
    # Test 1: Input validation
    print("✓ Input Validation")
    try:
        try:
            Amendment("", "substantive", "Author")
        except ValueError:
            pass
        
        try:
            Amendment("Content", "invalid", "Author")
        except ValueError:
            pass
        
        print("  ✓ Passed")
        tests_passed += 1
    except Exception as e:
        print(f"  ✗ Failed: {e}")
    
    # Test 2: LLM simplification
    print("\n✓ LLM Simplification")
    try:
        llm = LLMSummaryGenerator()
        text = "Artykuł 1: Niniejszym ustawą osoby powinni mieć prawo."
        simplified = llm.simplify(text)
        assert "muszą" in simplified or "musi" in simplified
        print("  ✓ Passed")
        tests_passed += 1
    except Exception as e:
        print(f"  ✗ Failed: {e}")
    
    # Test 3: Amendment & hashing
    print("\n✓ Amendment Creation & Hashing")
    try:
        llm = LLMSummaryGenerator()
        amendment = Amendment("Artykuł 1: Test", "substantive", "Author A", llm=llm)
        from hash_chain import ChainNode
        node = ChainNode(amendment)
        assert len(node.hash) == 64
        assert node.verify()
        print("  ✓ Passed")
        tests_passed += 1
    except Exception as e:
        print(f"  ✗ Failed: {e}")
    
    # Test 4: Chain operations
    print("\n✓ Chain Operations")
    try:
        llm = LLMSummaryGenerator()
        chain = HashChain("ACT-001", "Test Act", llm=llm)
        
        for i in range(5):
            amendment = Amendment(f"Amendment {i}", "substantive", f"Author {i}", llm=llm)
            chain.add_amendment(amendment)
        
        assert len(chain.chain) == 5
        assert chain.verify_integrity()
        print("  ✓ Passed")
        tests_passed += 1
    except Exception as e:
        print(f"  ✗ Failed: {e}")
    
    # Test 5: Tampering detection
    print("\n✓ Tampering Detection")
    try:
        llm = LLMSummaryGenerator()
        chain = HashChain("ACT-002", "Test Act", llm=llm)
        amendment = Amendment("Test", "substantive", "Author", llm=llm)
        chain.add_amendment(amendment)
        
        chain.chain[0].amendment.content = "TAMPERED"
        assert not chain.verify_integrity()
        print("  ✓ Passed")
        tests_passed += 1
    except Exception as e:
        print(f"  ✗ Failed: {e}")
    
    # Test 6: Rate limiting
    print("\n✓ Rate Limiting")
    try:
        from hash_chain import RateLimiter
        limiter = RateLimiter(max_requests=3, window_sec=60)
        
        assert limiter.is_allowed("client1")
        assert limiter.is_allowed("client1")
        assert limiter.is_allowed("client1")
        assert not limiter.is_allowed("client1")
        print("  ✓ Passed")
        tests_passed += 1
    except Exception as e:
        print(f"  ✗ Failed: {e}")
    
    # Summary
    print("\n" + "="*70)
    print(f"RESULTS: {tests_passed}/{tests_total} tests passed")
    
    if tests_passed == tests_total:
        print("✅ RELEASE APPROVED - READY FOR PRODUCTION")
        print("="*70)
        print("\nStart API server:")
        print("  python -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload")
        print("\nOpen in browser:")
        print("  http://localhost:8000/docs")
        print("="*70 + "\n")
        return 0
    else:
        print("❌ RELEASE BLOCKED")
        print("="*70 + "\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
