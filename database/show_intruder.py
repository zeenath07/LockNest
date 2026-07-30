from backend.models.db import get_intruders

# Example vault_id for filtering; set to None or value as needed
vault_id = None  # Use None for all, or "your_vault_id" for one user's records

if vault_id:
    logs = get_intruders(vault_id)
else:
    # To fetch ALL entries regardless of vault, add a new helper or use direct client call:
    from supabase import create_client
    SUPABASE_URL = "https://czilbctugcypmgymjddd.supabase.co"
    SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImN6aWxiY3R1Z2N5cG1neW1qZGRkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIyNzQ4NzEsImV4cCI6MjA3Nzg1MDg3MX0.4P9YC2SOU-TVgYK05Bdu1w28PmI4Fo4E-b-_XXpV2qM"
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    logs = supabase.table('intruders').select("image_path").execute().data

for row in logs:
    print(row["image_path"])
