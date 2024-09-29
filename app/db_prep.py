from db import init_db
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    print("Initializing database...")
    init_db()
