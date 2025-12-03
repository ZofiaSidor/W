"""
START_HERE.py - Quick verification that everything works
Run this to verify the system is ready
"""

import sys
import time

print("\n" + "="*70)
print("LEGAL ACT TRACKER - STARTUP VERIFICATION")
print("="*70 + "\n")

# Step 1: Check imports
print("📦 Step 1: Checking imports...")
try:
    from hash_chain import (
        LLMSummaryGenerator, Amendment, ChainNode, 
        HashChain, RateLimiter, AuditLog, Config
    )
    print("  ✅ All imports successful\n")
except ImportError as e:
    print(f"  ❌ Import failed: {e}")
    print("  Fix: Run 'pip install -r requirements.txt'\n")
    sys.exit(1)

# Step 2: Quick functionality test
print("🧪 Step 2: Testing core functionality...")
try:
    llm = LLMSummaryGenerator()
    amendment = Amendment("Test content", "substantive", "Test Author")
    chain = HashChain("TEST", "Test Act")
    chain.add_amendment(amendment)
    assert chain.verify_integrity()
    print("  ✅ Core functionality works\n")
except Exception as e:
    print(f"  ❌ Functionality test failed: {e}\n")
    sys.exit(1)

# Step 3: Check configuration
print("⚙️  Step 3: Verifying configuration...")
try:
    config = Config()
    print(f"  ✅ API Port: {config.RATE_LIMIT_REQUESTS}")
    print(f"  ✅ Max chain size: {config.MAX_CHAIN_SIZE}")
    print(f"  ✅ Audit log: {config.AUDIT_LOG}\n")
except Exception as e:
    print(f"  ❌ Configuration error: {e}\n")
    sys.exit(1)

# Step 4: Ready to start
print("="*70)
print("✅ SYSTEM READY TO START")
print("="*70)
print("\nNext steps:")
print("  1. Run: python main.py")
print("  2. Wait for 'RELEASE APPROVED' message")
print("  3. Open: http://localhost:8000/docs")
print("\nTroubleshooting:")
print("  - If port 8000 is busy: python main.py --port 8001")
print("  - For errors: check console output")
print("  - View API docs at: http://localhost:8000/docs")
print("\n" + "="*70 + "\n")
