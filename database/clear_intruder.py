from supabase import create_client

SUPABASE_URL = "YOUR_SUPABASE_URL"
SUPABASE_KEY = "YOUR_SERVICE_ROLE_OR_ANON_KEY"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def delete_all_intruders():
    response = supabase.table('intruders').delete().neq('id', 0).execute()
    if response.error:
        print("Error deleting intruders:", response.error)
    else:
        print("All intruder records deleted")

delete_all_intruders()
