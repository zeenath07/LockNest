from supabase import create_client, Client
import datetime

# Replace these with your actual Supabase project details
SUPABASE_URL = "https://czilbctugcypmgymjddd.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImN6aWxiY3R1Z2N5cG1neW1qZGRkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIyNzQ4NzEsImV4cCI6MjA3Nzg1MDg3MX0.4P9YC2SOU-TVgYK05Bdu1w28PmI4Fo4E-b-_XXpV2qM"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# --- USERS table functions ---
def add_user(vault_id, password):
    response = supabase.table('users').insert({
        "vault_id": vault_id,
        "password": password
    }).execute()
    if response.error:
        raise Exception(response.error.message)
    return response.data


def get_user_by_vault_id(vault_id):
    response = supabase.table('users').select("*").eq("vault_id", vault_id).single().execute()
    if response.error:
        raise Exception(response.error.message)
    return response.data


# --- VAULT_FILES table functions ---
def add_vault_file(vault_id, filename, filepath):
    response = supabase.table('vault_files').insert({
        "vault_id": vault_id,
        "filename": filename,
        "filepath": filepath,
        "uploaded_at": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }).execute()
    if response.error:
        raise Exception(response.error.message)
    return response.data


def get_vault_files(vault_id):
    response = supabase.table('vault_files').select("*").eq("vault_id", vault_id).execute()
    if response.error:
        raise Exception(response.error.message)
    return response.data


def delete_vault_file(vault_id, filename):
    response = supabase.table('vault_files').delete().eq("vault_id", vault_id).eq("filename", filename).execute()
    if response.error:
        raise Exception(response.error.message)
    return response.data


# --- INTRUDERS table functions ---
def insert_intruder(vault_id, image_path):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    response = supabase.table('intruders').insert({
        "vault_id": vault_id,
        "image_path": image_path,
        "timestamp": timestamp
    }).execute()
    if response.error:
        raise Exception(response.error.message)
    return response.data


def get_intruders(vault_id):
    response = supabase.table('intruders').select("*").eq("vault_id", vault_id).execute()
    if response.error:
        raise Exception(response.error.message)
    return response.data
