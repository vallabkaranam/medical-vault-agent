import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def verify_db():
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("Error: Supabase credentials not found.")
        return

    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Fetch the most recent record
        response = supabase.table("compliance_results").select("*").order("processed_at", desc=True).limit(1).execute()
        
        if response.data:
            print("Successfully retrieved record from DB!")
            print(f"Record ID: {response.data[0].get('record_id')}")
            print(f"Standard: {response.data[0].get('standard')}")
            print(f"Processed At: {response.data[0].get('processed_at')}")
        else:
            print("No records found in 'compliance_results' table.")
            
    except Exception as e:
        print(f"Database verification failed: {e}")

if __name__ == "__main__":
    verify_db()
