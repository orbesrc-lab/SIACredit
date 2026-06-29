import os, json
from dotenv import load_dotenv
load_dotenv('c:\\SIAC\\.env')
from supabase import create_client

sb = create_client(os.environ.get('SUPABASE_URL'), os.environ.get('SUPABASE_KEY'))

records = [
  {
    "id": "s_e624c6b11",
    "inst_id": 1,
    "program_id": 47,
    "student_email": "jperez@gmail.com",
    "data": {
      "email": "jperez@gmail.com",
      "enrolled_courses": ["c_bc4a727f2"],
      "id": "s_e624c6b11",
      "inst_id": 1,
      "name": "[ASPIRANTE] Juan Perez"
    }
  },
  {
    "id": "s_40fcfc1b3",
    "inst_id": 1,
    "program_id": 47,
    "student_email": "jorbes@gmail.com",
    "data": {
      "name": "jisela Orbes",
      "email": "jorbes@gmail.com",
      "id": "s_40fcfc1b3",
      "inst_id": 1,
      "enrolled_courses": []
    }
  }
]

res = sb.table('statistics').update({'data_json': json.dumps(records)}).eq('table_id', 'LMS_STUDENTS_1').execute()
print('Restored LMS_STUDENTS_1')
