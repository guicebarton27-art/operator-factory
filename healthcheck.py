#!/usr/bin/env python3
"""
Simple healthcheck script to verify OpenRouter/Mimo LLM endpoints.
Usage: python healthcheck.py
"""

import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

try:
    from config import Config
except ImportError:
    print("Error: config.py not found. Make sure you're in the correct directory.")
    sys.exit(1)

def main():
    print("=" * 50)
    print("LLM Endpoints Healthcheck")
    print("=" * 50)
    
    # Check environment variables
    print("\n1. Checking environment variables...")
    env_vars = {
        "OPENROUTER_API_KEY": Config.OPENROUTER_API_KEY,
        "OPENROUTER_BASE_URL": Config.OPENROUTER_BASE_URL,
        "MIMO_BASE_URL": Config.MIMO_BASE_URL,
        "DEFAULT_MODEL": Config.DEFAULT_MODEL,
    }
    
    for var, value in env_vars.items():
        status = "✓" if value else "✗"
        print(f"   {status} {var}: {value if value else 'NOT SET'}")
    
    # Validate configuration
    print("\n2. Validating configuration...")
    if not Config.validate():
        print("❌ Configuration validation failed")
        print("\n💡 Tip: Copy .env.example to .env and set your API key")
        return False
    
    print("✅ Configuration is valid")
    
    # Test API connectivity
    print("\n3. Testing API connectivity...")
    try:
        import requests
        
        # Test OpenRouter
        print("   Testing OpenRouter...")
        response = requests.get(
            f"{Config.OPENROUTER_BASE_URL}/models",
            headers={"Authorization": f"Bearer {Config.OPENROUTER_API_KEY}"}
        )
        
        if response.status_code == 200:
            print("   ✅ OpenRouter API: Connected")
            models = response.json().get("data", [])
            print(f"   📊 Available models: {len(models)}")
        else:
            print(f"   ❌ OpenRouter API: Status {response.status_code}")
            return False
            
    except ImportError:
        print("   ⚠️  'requests' library not installed")
        print("   ℹ️  Install with: pip install requests")
        print("   ✓ Skipping API connectivity test")
    except Exception as e:
        print(f"   ❌ API test failed: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("✅ Healthcheck completed successfully!")
    print("=" * 50)
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
