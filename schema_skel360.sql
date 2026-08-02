-- ====================================================================================
-- SKEL HUMAN CAPITAL 360 - MODELO FÍSICO DE DATOS (Fase 1)
-- ====================================================================================

-- Habilitar extensión para UUIDs si no está habilitada
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. EMPRESAS (Tenant Base)
CREATE TABLE skel_empresas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nit VARCHAR(50) UNIQUE,
    nombre VARCHAR(200) NOT NULL,
    sector VARCHAR(100),
    pais VARCHAR(100),
    ciudad VARCHAR(100),
    logo_url TEXT,
    estado VARCHAR(20) DEFAULT 'Activa',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- 2. SEDES
CREATE TABLE skel_sedes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    empresa_id UUID NOT NULL REFERENCES skel_empresas(id) ON DELETE CASCADE,
    nombre VARCHAR(150) NOT NULL,
    ciudad VARCHAR(100),
    estado VARCHAR(20) DEFAULT 'Activa',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- 3. ÁREAS
CREATE TABLE skel_areas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    empresa_id UUID NOT NULL REFERENCES skel_empresas(id) ON DELETE CASCADE,
    sede_id UUID REFERENCES skel_sedes(id) ON DELETE SET NULL,
    nombre VARCHAR(150) NOT NULL,
    estado VARCHAR(20) DEFAULT 'Activa',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- 4. PROCESOS
CREATE TABLE skel_procesos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    empresa_id UUID NOT NULL REFERENCES skel_empresas(id) ON DELETE CASCADE,
    area_id UUID REFERENCES skel_areas(id) ON DELETE SET NULL,
    nombre VARCHAR(150) NOT NULL,
    estado VARCHAR(20) DEFAULT 'Activa',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- 5. CARGOS
CREATE TABLE skel_cargos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    empresa_id UUID NOT NULL REFERENCES skel_empresas(id) ON DELETE CASCADE,
    nombre VARCHAR(200) NOT NULL,
    nivel_jerarquico VARCHAR(50), -- ej. Director, Analista, Auxiliar
    mision_cargo TEXT,
    estado VARCHAR(20) DEFAULT 'Activa',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- 6. COLABORADORES
CREATE TABLE skel_colaboradores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    empresa_id UUID NOT NULL REFERENCES skel_empresas(id) ON DELETE CASCADE,
    cargo_id UUID REFERENCES skel_cargos(id) ON DELETE SET NULL,
    area_id UUID REFERENCES skel_areas(id) ON DELETE SET NULL,
    jefe_id UUID REFERENCES skel_colaboradores(id) ON DELETE SET NULL,
    documento VARCHAR(50) NOT NULL,
    nombres VARCHAR(150) NOT NULL,
    apellidos VARCHAR(150) NOT NULL,
    email VARCHAR(200),
    fecha_ingreso DATE,
    estado VARCHAR(20) DEFAULT 'Activo',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- 7. FAMILIAS DE COMPETENCIAS
CREATE TABLE skel_familias_competencias (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    empresa_id UUID NOT NULL REFERENCES skel_empresas(id) ON DELETE CASCADE, -- Si es null, es catálogo genérico
    nombre VARCHAR(150) NOT NULL,
    descripcion TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- 8. COMPETENCIAS
CREATE TABLE skel_competencias (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    familia_id UUID NOT NULL REFERENCES skel_familias_competencias(id) ON DELETE CASCADE,
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT,
    tipo VARCHAR(50), -- Organizacional, Transversal, Liderazgo, Técnica
    estado VARCHAR(20) DEFAULT 'Activa',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- 9. NIVELES DE COMPETENCIA
CREATE TABLE skel_niveles_competencias (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    competencia_id UUID NOT NULL REFERENCES skel_competencias(id) ON DELETE CASCADE,
    nombre VARCHAR(100) NOT NULL, -- Básico, Intermedio, Avanzado
    valor INT NOT NULL, -- 1, 2, 3
    resultado_esperado TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- 10. CONDUCTAS OBSERVABLES
CREATE TABLE skel_conductas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nivel_id UUID NOT NULL REFERENCES skel_niveles_competencias(id) ON DELETE CASCADE,
    descripcion TEXT NOT NULL,
    estado VARCHAR(20) DEFAULT 'Activa',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- 11. CARGO - COMPETENCIAS (N a N)
CREATE TABLE skel_cargos_competencias (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cargo_id UUID NOT NULL REFERENCES skel_cargos(id) ON DELETE CASCADE,
    competencia_id UUID NOT NULL REFERENCES skel_competencias(id) ON DELETE CASCADE,
    nivel_esperado_id UUID NOT NULL REFERENCES skel_niveles_competencias(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    UNIQUE(cargo_id, competencia_id)
);

-- ====================================================================================
-- RLS (ROW LEVEL SECURITY) - MULTITENANT
-- ====================================================================================

-- Habilitar RLS en las tablas
ALTER TABLE skel_empresas ENABLE ROW LEVEL SECURITY;
ALTER TABLE skel_sedes ENABLE ROW LEVEL SECURITY;
ALTER TABLE skel_areas ENABLE ROW LEVEL SECURITY;
ALTER TABLE skel_procesos ENABLE ROW LEVEL SECURITY;
ALTER TABLE skel_cargos ENABLE ROW LEVEL SECURITY;
ALTER TABLE skel_colaboradores ENABLE ROW LEVEL SECURITY;
ALTER TABLE skel_familias_competencias ENABLE ROW LEVEL SECURITY;
ALTER TABLE skel_competencias ENABLE ROW LEVEL SECURITY;

-- Nota para el usuario:
-- Las políticas (Policies) exactas dependerán de cómo estés manejando el JWT de Supabase
-- con tus usuarios actuales. Si tu backend en Flask usa la Service Key, hará un bypass de estas políticas.
-- Si consultas desde el frontend, deberás crear políticas como:
-- CREATE POLICY "Aislamiento por Empresa" ON skel_sedes 
-- FOR ALL USING (empresa_id = (SELECT empresa_id FROM users WHERE id = auth.uid()));
