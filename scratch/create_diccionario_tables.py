import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv('SUPABASE_DB_URL') or os.getenv('DATABASE_URL')
conn = psycopg2.connect(db_url)
conn.autocommit = True
cur = conn.cursor()

sql = """
CREATE TABLE IF NOT EXISTS skel_diccionario_competencias (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nombre VARCHAR(150) NOT NULL,
    descripcion TEXT,
    tipo VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS skel_diccionario_comportamientos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    competencia_id UUID NOT NULL REFERENCES skel_diccionario_competencias(id) ON DELETE CASCADE,
    descripcion TEXT NOT NULL,
    nivel_esperado INTEGER DEFAULT 3
);

-- Disable RLS on these new tables
ALTER TABLE skel_diccionario_competencias DISABLE ROW LEVEL SECURITY;
ALTER TABLE skel_diccionario_comportamientos DISABLE ROW LEVEL SECURITY;
"""

try:
    cur.execute(sql)
    print("Tablas de Diccionario creadas exitosamente.")
except Exception as e:
    print("Error creando tablas:", e)

cur.close()
conn.close()
