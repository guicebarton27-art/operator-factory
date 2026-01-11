try:
    from config import Config
except ImportError:
    # Fallback if config module is not available
    class Config:
        SECRET_KEY = 'fallback-secret-key'

def main():
    print(f"Builder Store is running with secret key: {Config.SECRET_KEY}")
    print("Welcome to the AI Department Store!")
    print("Ready to manage and deploy AI services.")

if __name__ == "__main__":
    main()
