from app.database import engine, Base
import app.models  # triggers all model imports

def init_db():
    Base.metadata.create_all(bind=engine)
    print("✅ All tables created successfully!")

if __name__ == "__main__":
    init_db()