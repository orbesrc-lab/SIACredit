import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv('DATABASE_URL')
if not db_url:
    print("DATABASE_URL not found in .env")
    exit(1)

try:
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    
    print("Actualizando tabla 'planes_mejora' con las nuevas columnas...")
    
    cur.execute("""
        ALTER TABLE planes_mejora 
        ADD COLUMN IF NOT EXISTS fecha_inicio DATE DEFAULT CURRENT_DATE,
        ADD COLUMN IF NOT EXISTS meta TEXT,
        ADD COLUMN IF NOT EXISTS indicador_tipo VARCHAR(50) DEFAULT 'porcentaje',
        ADD COLUMN IF NOT EXISTS indicador_meta_num INT DEFAULT 0,
        ADD COLUMN IF NOT EXISTS indicador_meta_den INT DEFAULT 1,
        ADD COLUMN IF NOT EXISTS indicador_documento_url TEXT,
        ADD COLUMN IF NOT EXISTS indicador_survey_id INT,
        ADD COLUMN IF NOT EXISTS indicador_question_id VARCHAR(50),
        ADD COLUMN IF NOT EXISTS presupuesto_tiempo VARCHAR(100),
        ADD COLUMN IF NOT EXISTS presupuesto_dinero NUMERIC DEFAULT 0,
        ADD COLUMN IF NOT EXISTS responsable_rol VARCHAR(50) DEFAULT 'lider';
    """)
    
    print("OK - Columnas agregadas exitosamente o ya existentes.")
    
    conn.commit()
    conn.close()
    print("SUCCESS - Migracion de columnas completada con exito.")
    
except Exception as e:
    print(f"ERROR - Error durante la migracion: {e}")
    exit(1)
