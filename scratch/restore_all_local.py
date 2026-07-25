import json
import os
import sys
from dotenv import load_dotenv

load_dotenv('c:/SIAC/.env')
sys.path.append(os.path.abspath('c:/SIAC'))

import formacion_storage

def restore_file(filename, save_func, name_key='name'):
    try:
        with open(f'c:/SIAC/instance/{filename}', 'r', encoding='utf-8') as f:
            items = json.load(f)
    except FileNotFoundError:
        print(f"No {filename} found.")
        return

    count = 0
    for item in items:
        inst_id = item.get('inst_id', 1)
        if save_func == formacion_storage.save_submission:
            program_id = item.get('program_id', 47)
            saved = save_func(inst_id, program_id, item)
        else:
            saved = save_func(inst_id, item)
            
        if saved:
            count += 1
            print(f"Restored {filename}: {item.get(name_key, item.get('id'))}")

    print(f"Total {filename} restored: {count}")

restore_file('local_teachers.json', formacion_storage.save_teacher, 'name')
restore_file('local_students.json', formacion_storage.save_student, 'email')
restore_file('local_submissions.json', formacion_storage.save_submission, 'id')
