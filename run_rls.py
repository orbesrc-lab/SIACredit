import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv('SUPABASE_DB_URL') or os.getenv('DATABASE_URL')
conn = psycopg2.connect(db_url)
conn.autocommit = True
cur = conn.cursor()
tables = [
    'skel_empresas', 'skel_sedes', 'skel_areas', 'skel_procesos', 'skel_cargos',
    'skel_cargos_roles', 'skel_colaboradores', 'skel_diccionario_competencias',
    'skel_diccionario_comportamientos', 'skel_cargos_competencias',
    'skel_evaluaciones', 'skel_evaluaciones_colaboradores',
    'skel_evaluaciones_respuestas', 'skel_evaluaciones_resultados',
    'skel_tokens_acceso', 'skel_notificaciones'
]
for t in tables:
    try:
        cur.execute(f'ALTER TABLE {t} DISABLE ROW LEVEL SECURITY;')
        print(f'Disabled RLS on {t}')
    except Exception as e:
        print(f'Error on {t}: {e}')
cur.close()
conn.close()
