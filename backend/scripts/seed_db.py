import sys
import os

# Add the backend directory to Python path so 'app' can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.hcp import HCP
from app.models.product import Product

def seed():
    db = SessionLocal()
    
    # Check if we already have HCPs
    if db.query(HCP).count() > 0:
        print("Database already seeded with HCPs.")
        db.close()
        return

    # Create dummy products
    products = [
        Product(name="WonderDrug", category="Cardiology"),
        Product(name="HealPill", category="Neurology"),
        Product(name="CureAll", category="General Medicine"),
    ]
    db.add_all(products)
    
    # Create dummy HCPs
    hcps = [
        HCP(
            name="Dr. Smith",
            specialty="Cardiologist",
            hospital_affiliation="General Hospital",
            notes="Prefers morning meetings."
        ),
        HCP(
            name="Dr. Doe",
            specialty="Neurologist",
            hospital_affiliation="City Clinic",
            notes="Very analytical, requires detailed clinical data."
        ),
        HCP(
            name="Dr. Adams",
            specialty="General Practitioner",
            hospital_affiliation="Community Health Center",
            notes="High volume of patients."
        )
    ]
    
    db.add_all(hcps)
    db.commit()
    print("Successfully seeded the database with HCPs and Products!")
    
    db.close()

if __name__ == "__main__":
    seed()
