-- Schema para el CRM B2B de SKEL 360
-- Por favor ejecuta este comando en el "SQL Editor" de tu panel de Supabase.

CREATE TABLE IF NOT EXISTS prospects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    position VARCHAR(255),
    institution VARCHAR(255) NOT NULL,
    snies_code VARCHAR(50),
    email VARCHAR(255),
    linkedin TEXT,
    status VARCHAR(50) DEFAULT 'Pendiente',
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- Habilitar permisos (Opcional, pero recomendado si usas RLS)
-- ALTER TABLE prospects ENABLE ROW LEVEL SECURITY;
-- CREATE POLICY "Permitir todo a usuarios autenticados" ON prospects FOR ALL USING (true);
