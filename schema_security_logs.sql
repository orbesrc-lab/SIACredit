-- Crear tabla para auditoría de backups
CREATE TABLE public.security_backup_logs (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.users(id) ON DELETE SET NULL,
    user_email TEXT NOT NULL,
    inst_id INTEGER REFERENCES public.institution(id) ON DELETE CASCADE,
    action_type TEXT NOT NULL, -- Ej: 'FULL_BACKUP', 'FACTOR_BACKUP', 'EVIDENCIAS_BACKUP', 'CSV_BACKUP'
    status TEXT NOT NULL, -- 'SUCCESS' o 'DENIED'
    timestamp TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL,
    details TEXT -- Para información extra como IP o motivo de denegación
);

-- Políticas de Seguridad (RSL)
ALTER TABLE public.security_backup_logs ENABLE ROW LEVEL SECURITY;

-- Los admins pueden ver los logs de su propia institución
CREATE POLICY "Admins pueden ver logs de su institución"
    ON public.security_backup_logs
    FOR SELECT
    USING (
        auth.uid() IN (
            SELECT id FROM public.users 
            WHERE role IN ('admin', 'inst_admin', 'super_admin') 
            AND users.inst_id = security_backup_logs.inst_id
        )
    );

-- Permitir inserción desde el backend (service role)
-- Supabase por defecto permite inserciones al service role (que usa el backend)
