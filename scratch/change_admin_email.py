import os
import requests
from dotenv import load_dotenv

load_dotenv()

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')

def change_email():
    old_email = "admin@siacredit.edu.co"
    new_email = "orbesrc@gmail.com"
    
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    
    # Search
    print(f"Buscando {old_email}...")
    res = requests.get(f"{url}/rest/v1/users?email=eq.{old_email}", headers=headers)
    print(f"Status: {res.status_code}")
    data = res.json()
    
    if data:
        print(f"Encontrado. Actualizando a {new_email}...")
        patch_res = requests.patch(f"{url}/rest/v1/users?email=eq.{old_email}", headers=headers, json={"email": new_email})
        print(f"Patch Status: {patch_res.status_code}")
        if patch_res.status_code in [200, 204]:
            print("✅ Exito.")
        else:
            print(f"❌ Fallo: {patch_res.text}")
    else:
        print(f"No se encontro {old_email}. Probando si ya es {new_email}...")
        res2 = requests.get(f"{url}/rest/v1/users?email=eq.{new_email}", headers=headers)
        if res2.json():
            print(f"✅ Ya existe {new_email}.")
        else:
            print("❌ No se encontro ninguno.")

if __name__ == "__main__":
    change_email()
