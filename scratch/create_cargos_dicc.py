import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv('SUPABASE_DB_URL') or os.getenv('DATABASE_URL')
conn = psycopg2.connect(db_url)
conn.autocommit = True
cur = conn.cursor()

sql = """
CREATE TABLE IF NOT EXISTS skel_cargos_diccionario (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cargo_id UUID NOT NULL REFERENCES skel_cargos(id) ON DELETE CASCADE,
    competencia_id UUID NOT NULL REFERENCES skel_diccionario_competencias(id) ON DELETE CASCADE,
    nivel_esperado INTEGER DEFAULT 3,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    UNIQUE(cargo_id, competencia_id)
);

ALTER TABLE skel_cargos_diccionario DISABLE ROW LEVEL SECURITY;
"""

try:
    cur.execute(sql)
    print("Tabla skel_cargos_diccionario creada exitosamente.")
except Exception as e:
    print("Error creando tabla:", e)

cur.close()
conn.close()
