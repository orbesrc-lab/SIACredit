-- ====================================================================================
-- SKEL HUMAN CAPITAL 360 - MOTOR DE EVALUACIONES (Fase 3)
-- ====================================================================================

-- 12. EVALUACIONES (Cabecera)
CREATE TABLE skel_evaluaciones (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    empresa_id UUID NOT NULL REFERENCES skel_empresas(id) ON DELETE CASCADE,
    nombre VARCHAR(255) NOT NULL,
    descripcion TEXT,
    tipo VARCHAR(50) DEFAULT 'Diagnóstico', -- Diagnóstico, Desempeño, 360, Clima, etc.
    estado VARCHAR(20) DEFAULT 'Borrador', -- Borrador, Activa, Cerrada, Archivada
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- 13. VERSIONES DE EVALUACIÓN
-- BR-403: Una evaluación nunca se modifica. Si cambia, se crea otra versión.
CREATE TABLE skel_evaluaciones_versiones (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    evaluacion_id UUID NOT NULL REFERENCES skel_evaluaciones(id) ON DELETE CASCADE,
    version INT NOT NULL DEFAULT 1,
    fecha_publicacion TIMESTAMP WITH TIME ZONE,
    activa BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    UNIQUE(evaluacion_id, version)
);

-- 14. SECCIONES DE EVALUACIÓN
CREATE TABLE skel_secciones_evaluacion (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    version_id UUID NOT NULL REFERENCES skel_evaluaciones_versiones(id) ON DELETE CASCADE,
    orden INT NOT NULL,
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT,
    tipo VARCHAR(50) DEFAULT 'Estandar', -- Estandar, MatrizCompetencias
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- 15. PREGUNTAS
-- BR-404: Las preguntas podrán reutilizarse.
CREATE TABLE skel_preguntas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    empresa_id UUID REFERENCES skel_empresas(id) ON DELETE CASCADE, -- Null si es pregunta global SKEL
    enunciado TEXT NOT NULL,
    tipo VARCHAR(50) NOT NULL, -- Likert, Multiple, Unica, Abierta, MatrizCompetencia
    escala VARCHAR(50), -- General, Prioridad, Frecuencia, Dominio
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- 16. PREGUNTAS POR SECCIÓN (N a N)
CREATE TABLE skel_seccion_preguntas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    seccion_id UUID NOT NULL REFERENCES skel_secciones_evaluacion(id) ON DELETE CASCADE,
    pregunta_id UUID NOT NULL REFERENCES skel_preguntas(id) ON DELETE CASCADE,
    orden INT NOT NULL,
    obligatoria BOOLEAN DEFAULT true,
    UNIQUE(seccion_id, pregunta_id)
);

-- 17. OPCIONES DE RESPUESTA (Para Selección Múltiple/Única)
CREATE TABLE skel_opciones_respuesta (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pregunta_id UUID NOT NULL REFERENCES skel_preguntas(id) ON DELETE CASCADE,
    texto TEXT NOT NULL,
    valor INT,
    orden INT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- 18. RESPUESTAS ESTÁNDAR
-- BR-406: Una respuesta queda asociada a Persona, Pregunta, Fecha, Versión
CREATE TABLE skel_respuestas_estandar (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    colaborador_id UUID NOT NULL REFERENCES skel_colaboradores(id) ON DELETE CASCADE,
    version_id UUID NOT NULL REFERENCES skel_evaluaciones_versiones(id) ON DELETE CASCADE,
    pregunta_id UUID NOT NULL REFERENCES skel_preguntas(id) ON DELETE CASCADE,
    fecha TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    valor_int INT, -- Para escalas
    valor_texto TEXT, -- Para abiertas
    opcion_id UUID REFERENCES skel_opciones_respuesta(id) ON DELETE SET NULL, -- Para selección
    tiempo_segundos INT
);

-- 19. RESPUESTAS MATRIZ INTEGRAL DE COMPETENCIAS
-- Tabla especializada requerida por el usuario para historial e impacto.
CREATE TABLE skel_respuestas_matriz_competencias (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    colaborador_id UUID NOT NULL REFERENCES skel_colaboradores(id) ON DELETE CASCADE,
    version_id UUID NOT NULL REFERENCES skel_evaluaciones_versiones(id) ON DELETE CASCADE,
    competencia_id UUID NOT NULL REFERENCES skel_competencias(id) ON DELETE CASCADE,
    
    fecha TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()), -- Para histórico (Usuario solicitó esto)
    
    -- Las 5 dimensiones evaluadas (Escalas 1 a 5)
    importancia INT CHECK (importancia BETWEEN 1 AND 5),
    nivel_actual INT CHECK (nivel_actual BETWEEN 1 AND 5),
    frecuencia_uso INT CHECK (frecuencia_uso BETWEEN 1 AND 5),
    impacto_mejora INT CHECK (impacto_mejora BETWEEN 1 AND 5),
    prioridad_capacitacion INT CHECK (prioridad_capacitacion BETWEEN 1 AND 5),
    
    -- Indicadores Clave Calculados Automáticamente (Se calcularán vía Trigger/Función o Backend)
    brecha_competencia INT, -- Importancia - Nivel Actual
    indice_prioridad_formacion DECIMAL(10,2) -- Fórmula analítica SKEL
);


-- ====================================================================================
-- RLS (ROW LEVEL SECURITY) - MULTITENANT
-- ====================================================================================

-- Habilitar RLS en las tablas
ALTER TABLE skel_evaluaciones ENABLE ROW LEVEL SECURITY;
ALTER TABLE skel_preguntas ENABLE ROW LEVEL SECURITY;
ALTER TABLE skel_respuestas_estandar ENABLE ROW LEVEL SECURITY;
ALTER TABLE skel_respuestas_matriz_competencias ENABLE ROW LEVEL SECURITY;

-- Nota: Como siempre, en Supabase debes crear las políticas de acceso (Policies).
-- Ejemplo para la matriz de competencias:
-- CREATE POLICY "Aislamiento Tenant" ON skel_respuestas_matriz_competencias
-- FOR ALL USING (
--     colaborador_id IN (
--         SELECT id FROM skel_colaboradores WHERE empresa_id = (SELECT empresa_id FROM users WHERE id = auth.uid())
--     )
-- );
