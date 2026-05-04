-- =====================================================
-- RECREAR USUARIO ADMIN y primera institución
-- Ejecutar en Supabase SQL Editor
-- =====================================================

-- 1. Crear institución base
INSERT INTO institution (name, code, description)
VALUES ('SKEL Administración', '2025', 'Institución administrativa principal')
ON CONFLICT DO NOTHING;

-- 2. Crear usuario admin (contraseña: Admin2025!)
-- El hash corresponde a Admin2025! con werkzeug
INSERT INTO users (name, email, password, role, inst_id)
VALUES (
    'Administrador SKEL',
    'admin@siacredit.edu.co',
    'scrypt:32768:8:1$TEMP$HASH',
    'admin',
    (SELECT id FROM institution WHERE code = '2025' LIMIT 1)
)
ON CONFLICT (email) DO NOTHING;
