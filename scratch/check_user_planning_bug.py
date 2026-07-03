import sys
sys.path.insert(0, 'c:\\SIAC')
from app import supabase

def main():
    print("Checking user data...")
    res = supabase.table('users').select('*').eq('id', '52ed4bc8-bbc1-4c2c-ab53-9e2e8a46ddc1').execute()
    print("User Data:", res.data)

if __name__ == "__main__":
    main()
