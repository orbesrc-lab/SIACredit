import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv('SUPABASE_DB_URL') or os.getenv('DATABASE_URL')
conn = psycopg2.connect(db_url)
conn.autocommit = True
cur = conn.cursor()

sql = """
CREATE TABLE IF NOT EXISTS skel_360_respuestas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    evaluacion_id UUID NOT NULL REFERENCES skel_evaluaciones(id) ON DELETE CASCADE,
    evaluado_id UUID NOT NULL REFERENCES skel_colaboradores(id) ON DELETE CASCADE,
    evaluador_id UUID NOT NULL REFERENCES skel_colaboradores(id) ON DELETE CASCADE,
    comportamiento_id UUID NOT NULL REFERENCES skel_diccionario_comportamientos(id) ON DELETE CASCADE,
    puntaje INTEGER NOT NULL CHECK(puntaje >= 1 AND puntaje <= 5),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

ALTER TABLE skel_360_respuestas DISABLE ROW LEVEL SECURITY;
"""

try:
    cur.execute(sql)
    print("Tabla skel_360_respuestas creada exitosamente.")
except Exception as e:
    print("Error creando tabla:", e)

cur.close()
conn.close()
