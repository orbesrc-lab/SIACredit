import os
from supabase import create_client, Client
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

load_dotenv()

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def recover():
    print("--- RECUERACIÓN DE ADMIN ---")
    
    # 1. Verificar instituciones
    insts = supabase.table('institution').select("*").execute().data
    print(f"Instituciones actuales: {len(insts)}")
    for i in insts:
        print(f" - ID: {i['id']}, Name: {i['name']}, Code: {i.get('code')}")
    
    if not insts:
        print("No hay instituciones. Creando institución base...")
        new_inst = {
            "id": 1,
            "name": "SIACREDIT - ADMINISTRACIÓN",
            "code": "MAIN",
            "description": "Institución administrativa principal"
        }
        res = supabase.table('institution').insert(new_inst).execute()
        inst_id = res.data[0]['id']
        print(f"Creada institución ID: {inst_id}")
    else:
        # Usar la primera disponible o la 1 si existe
        inst_id = insts[0]['id']
        for i in insts:
            if i['id'] == 1:
                inst_id = 1
                break
    
    # 2. Recrear Admin
    admin_email = "orbesrc@gmail.com"
    admin_pass = "Admin2025!"
    hashed_pass = generate_password_hash(admin_pass)
    
    print(f"Verificando usuario {admin_email}...")
    existing = supabase.table('users').select("*").eq("email", admin_email).execute().data
    
    if existing:
        print(f"El usuario {admin_email} ya existe. Actualizando contraseña...")
        supabase.table('users').update({
            "password_hash": hashed_pass,
            "role": "admin",
            "inst_id": None
        }).eq("email", admin_email).execute()
    else:
        print(f"Creando usuario {admin_email}...")
        new_user = {
            "email": admin_email,
            "password_hash": hashed_pass,
            "role": "admin",
            "inst_id": None,
            "name": "Super Administrador"
        }
        try:
            supabase.table('users').insert(new_user).execute()
        except Exception as e:
            print(f"Error al insertar (probablemente falta columna name): {e}")
            # Fallback sin 'name'
            del new_user['name']
            supabase.table('users').insert(new_user).execute()
            
    print(f"\n--- ÉXITO ---")
    print(f"Usuario: {admin_email}")
    print(f"Contraseña: {admin_pass}")
    print(f"Asociado a Institución ID: {inst_id}")

    print("\n--- LISTA DE USUARIOS ACTUALES ---")
    users = supabase.table('users').select("email, role, inst_id").execute().data
    for u in users:
        print(f" - Email: {u['email']}, Role: {u['role']}, Inst ID: {u['inst_id']}")

if __name__ == "__main__":
    recover()
