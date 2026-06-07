import os
from dotenv import load_dotenv

load_dotenv('c:\\SIAC\\.env')

import sys
sys.path.append('c:\\SIAC')
from formacion_storage import delete_teacher, load_teachers

print("Teachers before:")
print(load_teachers(1))

print("Deleting teacher 'undefined':", delete_teacher(1, "undefined"))
# Try deleting if there's any other teacher with no id
print("Deleting teacher None:", delete_teacher(1, None))

print("Teachers after:")
print(load_teachers(1))
