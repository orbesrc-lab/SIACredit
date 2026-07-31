import os
import psycopg2
from dotenv import load_dotenv

load_dotenv(dotenv_path="c:/SIAC/.env")
db_url = os.environ.get("DATABASE_URL")

sql = """
CREATE TABLE IF NOT EXISTS public.business_matrices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    inst_id INTEGER REFERENCES public.institution(id) ON DELETE CASCADE,
    matrix_type TEXT NOT NULL,
    data JSONB NOT NULL DEFAULT '{}'::jsonb,
    results JSONB,
    created_by UUID REFERENCES public.users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS but allow insert/select/update for appropriate roles
ALTER TABLE public.business_matrices ENABLE ROW LEVEL SECURITY;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'business_matrices' AND policyname = 'Admins pueden gestionar matrices') THEN
        CREATE POLICY "Admins pueden gestionar matrices" 
        ON public.business_matrices 
        FOR ALL 
        USING (
            auth.uid() IN (
                SELECT id FROM public.users 
                WHERE role IN ('admin', 'empresa_admin', 'super_admin') 
                AND users.inst_id = business_matrices.inst_id
            )
        )
        WITH CHECK (
            auth.uid() IN (
                SELECT id FROM public.users 
                WHERE role IN ('admin', 'empresa_admin', 'super_admin') 
                AND users.inst_id = business_matrices.inst_id
            )
        );
    END IF;
END $$;
"""

try:
    conn = psycopg2.connect(db_url)
    conn.autocommit = True
    cursor = conn.cursor()
    cursor.execute(sql)
    print("Table business_matrices created successfully.")
    cursor.close()
    conn.close()
except Exception as e:
    print(f"Error creating table: {e}")
