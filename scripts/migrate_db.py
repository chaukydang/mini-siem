import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from backend.db.database import get_engine
from backend.db.models import Base

if __name__ == "__main__":
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    print("✅ Database schema created/migrated.")
