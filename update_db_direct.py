import psycopg2

db_url = 'postgresql://postgres:Johnorbes2026*@db.ftpkhueqooyqvwliifzb.supabase.co:5432/postgres'

try:
    print('Connecting to:', db_url.replace('Johnorbes2026*', '***'))
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    
    # Add name column if not exists
    cur.execute('ALTER TABLE users ADD COLUMN IF NOT EXISTS name TEXT;')
    print('✓ Columna name agregada (o ya existia)')
    
    # Populate name from email prefix
    cur.execute("UPDATE users SET name = split_part(email, '@', 1) WHERE name IS NULL OR name = '';")
    print(f'✓ Nombres actualizados: {cur.rowcount} registros')
    
    conn.commit()
    
    # Verify
    cur.execute('SELECT id, email, role, name, inst_id FROM users LIMIT 5;')
    rows = cur.fetchall()
    print('\nUsuarios en la BD:')
    for r in rows:
        print(f'  ID={r[0]}, email={r[1]}, role={r[2]}, name={r[3]}, inst_id={r[4]}')
    
    conn.close()
    print('\n✅ Esquema actualizado correctamente.')
    
except Exception as e:
    print(f'❌ Error: {e}')
