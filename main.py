import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

try:
    from config import Config
except ImportError:
    # Fallback if config module is not available
    class Config:
        OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
        OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        MIMO_BASE_URL = os.getenv("MIMO_BASE_URL", "https://api.mimo.com/v1")
        DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "anthropic/claude-3.5-sonnet")
        
        @classmethod
        def validate(cls):
            if not cls.OPENROUTER_API_KEY:
                print("Warning: OPENROUTER_API_KEY is not set")
                return False
            return True

def healthcheck():
    """Simple healthcheck to verify API key works."""
    print("🔍 Running healthcheck...")
    
    # Validate configuration
    if not Config.validate():
        print("❌ Configuration validation failed")
        return False
    
    print("✅ Configuration is valid")
    print(f"   - OpenRouter API Key: {'✓ Set' if Config.OPENROUTER_API_KEY else '✗ Missing'}")
    print(f"   - OpenRouter Base URL: {Config.OPENROUTER_BASE_URL}")
    print(f"   - Mimo Base URL: {Config.MIMO_BASE_URL}")
    print(f"   - Default Model: {Config.DEFAULT_MODEL}")
    
    # Optional: Test API connectivity (requires requests library)
    try:
        import requests
        response = requests.get(
            f"{Config.OPENROUTER_BASE_URL}/models",
            headers={"Authorization": f"Bearer {Config.OPENROUTER_API_KEY}"}
        )
        if response.status_code == 200:
            print("✅ OpenRouter API connection successful")
            return True
        else:
            print(f"⚠️  OpenRouter API returned status: {response.status_code}")
            return False
    except ImportError:
        print("ℹ️  Install 'requests' library for API connectivity test")
        return True
    except Exception as e:
        print(f"⚠️  Could not test API connectivity: {e}")
        return False

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "healthcheck":
        success = healthcheck()
        sys.exit(0 if success else 1)
    else:
        print("Usage: python main.py healthcheck")
        print("  healthcheck - Verify API configuration and connectivity")

if __name__ == '__main__':
    main()
