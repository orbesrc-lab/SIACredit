-- ====================================================================================
-- SKEL HUMAN CAPITAL 360 - MOTOR DE LOGÍSTICA (Fase 7)
-- ====================================================================================

-- 1. EXTENSIÓN A LA TABLA EMPRESAS
-- Añadir los interruptores para controlar qué logística usa cada empresa
ALTER TABLE skel_empresas
ADD COLUMN IF NOT EXISTS habilitar_magic_links BOOLEAN DEFAULT true,
ADD COLUMN IF NOT EXISTS habilitar_portal_colaborador BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS habilitar_kiosco_qr BOOLEAN DEFAULT false;

-- 2. TABLA DE TOKENS DE ACCESO
-- BR-701: Permite el acceso sin contraseña (Magic Links o sesiones de Kiosco)
CREATE TABLE skel_tokens_acceso (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(), -- El Token
    empresa_id UUID NOT NULL REFERENCES skel_empresas(id) ON DELETE CASCADE,
    colaborador_id UUID NOT NULL REFERENCES skel_colaboradores(id) ON DELETE CASCADE,
    evaluacion_id UUID NOT NULL REFERENCES skel_evaluaciones(id) ON DELETE CASCADE,
    
    tipo VARCHAR(50) DEFAULT 'MagicLink', -- MagicLink, KioscoSession
    estado VARCHAR(20) DEFAULT 'Pendiente', -- Pendiente, En Progreso, Completado, Expirado
    
    fecha_generacion TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    fecha_expiracion TIMESTAMP WITH TIME ZONE,
    fecha_uso TIMESTAMP WITH TIME ZONE
);

-- Habilitar RLS en la nueva tabla
ALTER TABLE skel_tokens_acceso ENABLE ROW LEVEL SECURITY;

-- Índice para búsquedas rápidas al hacer login con MagicLink
CREATE INDEX idx_tokens_colab ON skel_tokens_acceso(colaborador_id);
