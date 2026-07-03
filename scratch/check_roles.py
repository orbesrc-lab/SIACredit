import sys
sys.path.insert(0, 'c:\\SIAC')
from app import supabase

def main():
    res = supabase.table('users').select('role').execute()
    roles = set([r['role'] for r in res.data if r.get('role')])
    print('Roles in DB:', roles)

if __name__ == "__main__":
    main()
