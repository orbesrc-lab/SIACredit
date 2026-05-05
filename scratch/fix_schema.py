import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv('DATABASE_URL')

def fix_schema():
    print("Conectando a la base de datos para corregir esquema...")
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        # 1. Agregar leader_id a la tabla factors si no existe
        print("Agregando columna leader_id a 'factors'...")
        cur.execute("""
            ALTER TABLE factors 
            ADD COLUMN IF NOT EXISTS leader_id UUID REFERENCES users(id) ON DELETE SET NULL;
        """)
        
        # 2. Asegurar que la tabla users tenga la columna name
        print("Agregando columna name a 'users'...")
        cur.execute("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS name TEXT;
        """)
        
        conn.commit()
        print("✅ Esquema actualizado correctamente.")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ Error al actualizar esquema: {e}")

if __name__ == "__main__":
    fix_schema()
