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
    
    print("Creando tablas para la Fase 3...")
    
    # 1. Crear tabla planes_mejora
    cur.execute("""
        CREATE TABLE IF NOT EXISTS planes_mejora (
            id SERIAL PRIMARY KEY,
            inst_id INT NOT NULL,
            program_id INT NOT NULL,
            char_id VARCHAR(50) NOT NULL,
            accion TEXT NOT NULL,
            responsable VARCHAR(255) NOT NULL,
            fecha_limite DATE NOT NULL,
            estado VARCHAR(50) DEFAULT 'Pendiente',
            avance INT DEFAULT 0,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_planes_mejora_inst FOREIGN KEY (inst_id) REFERENCES institution(id) ON DELETE CASCADE,
            CONSTRAINT fk_planes_mejora_prog FOREIGN KEY (program_id) REFERENCES programs(id) ON DELETE CASCADE,
            CONSTRAINT fk_planes_mejora_char FOREIGN KEY (char_id) REFERENCES characteristics(id) ON DELETE CASCADE
        );
    """)
    print("OK - Tabla 'planes_mejora' creada o ya existente.")
    
    # 2. Crear tabla notificaciones
    cur.execute("""
        CREATE TABLE IF NOT EXISTS notificaciones (
            id SERIAL PRIMARY KEY,
            inst_id INT NOT NULL,
            program_id INT NOT NULL,
            usuario_email VARCHAR(255) NOT NULL,
            tipo VARCHAR(50) NOT NULL,
            titulo VARCHAR(255) NOT NULL,
            mensaje TEXT NOT NULL,
            leido BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_notificaciones_inst FOREIGN KEY (inst_id) REFERENCES institution(id) ON DELETE CASCADE,
            CONSTRAINT fk_notificaciones_prog FOREIGN KEY (program_id) REFERENCES programs(id) ON DELETE CASCADE
        );
    """)
    print("OK - Tabla 'notificaciones' creada o ya existente.")
    
    conn.commit()
    conn.close()
    print("SUCCESS - Migracion de la Fase 3 completada con exito.")
    
except Exception as e:
    print(f"ERROR - Error durante la migracion: {e}")
    exit(1)
