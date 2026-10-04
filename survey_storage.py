import os
import json
import uuid

def generate_id():
    return uuid.uuid4().hex[:9]

IS_VERCEL = os.environ.get("VERCEL") == "1"

if IS_VERCEL:
    SURVEYS_FILE = "/tmp/local_surveys.json"
    RESPONSES_FILE = "/tmp/local_responses.json"
else:
    SURVEYS_FILE = os.path.join("instance", "local_surveys.json")
    RESPONSES_FILE = os.path.join("instance", "local_responses.json")

def ensure_files_exist():
    if IS_VERCEL:
        if not os.path.exists(SURVEYS_FILE):
            try:
                with open(SURVEYS_FILE, 'w', encoding='utf-8') as f:
                    json.dump([], f)
            except Exception as e:
                print(f"Error creating SURVEYS_FILE in /tmp: {e}")
        if not os.path.exists(RESPONSES_FILE):
            try:
                with open(RESPONSES_FILE, 'w', encoding='utf-8') as f:
                    json.dump([], f)
            except Exception as e:
                print(f"Error creating RESPONSES_FILE in /tmp: {e}")
    else:
        os.makedirs("instance", exist_ok=True)
        if not os.path.exists(SURVEYS_FILE):
            with open(SURVEYS_FILE, 'w', encoding='utf-8') as f:
                json.dump([], f)
        if not os.path.exists(RESPONSES_FILE):
            with open(RESPONSES_FILE, 'w', encoding='utf-8') as f:
                json.dump([], f)


def load_local_surveys(inst_id, program_id):
    ensure_files_exist()
    try:
        with open(SURVEYS_FILE, 'r', encoding='utf-8') as f:
            all_surveys = json.load(f)
        target_inst = int(inst_id) if str(inst_id).isdigit() else inst_id
        target_prog = int(program_id) if str(program_id).isdigit() else program_id
        
        return [
            s for s in all_surveys 
            if (s.get('inst_id') == target_inst or str(s.get('inst_id')) == str(target_inst))
            and (
                s.get('program_id') == target_prog 
                or str(s.get('program_id')) == str(target_prog)
                or s.get('program_id') in (0, None, '0')
                or target_prog in (0, None, '0')
            )
        ]
    except Exception as e:
        print(f"Error loading surveys: {e}")
        return []

def get_survey_by_id_only(survey_id):
    ensure_files_exist()
    try:
        with open(SURVEYS_FILE, 'r', encoding='utf-8') as f:
            all_surveys = json.load(f)
        for s in all_surveys:
            if str(s.get('id')) == str(survey_id):
                return s
    except Exception as e:
        print(f"Error getting survey by id: {e}")
    return None

def save_local_surveys(inst_id, program_id, surveys_list):
    ensure_files_exist()
    try:
        with open(SURVEYS_FILE, 'r', encoding='utf-8') as f:
            all_surveys = json.load(f)
        target_inst = int(inst_id) if str(inst_id).isdigit() else inst_id
        target_prog = int(program_id) if str(program_id).isdigit() else program_id
        
        # Remove existing ones for this inst/prog
        all_surveys = [
            s for s in all_surveys 
            if not (
                (s.get('inst_id') == target_inst or str(s.get('inst_id')) == str(target_inst))
                and (s.get('program_id') == target_prog or str(s.get('program_id')) == str(target_prog))
            )
        ]
        # Add new ones
        for s in surveys_list:
            s['inst_id'] = target_inst
            s['program_id'] = target_prog
        all_surveys.extend(surveys_list)
        
        with open(SURVEYS_FILE, 'w', encoding='utf-8') as f:
            json.dump(all_surveys, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving surveys: {e}")
        return False

def load_local_responses(inst_id, program_id):
    ensure_files_exist()
    try:
        with open(RESPONSES_FILE, 'r', encoding='utf-8') as f:
            all_responses = json.load(f)
        target_inst = int(inst_id) if str(inst_id).isdigit() else inst_id
        target_prog = int(program_id) if str(program_id).isdigit() else program_id
        return [
            r for r in all_responses 
            if (r.get('inst_id') == target_inst or str(r.get('inst_id')) == str(target_inst))
            and (
                r.get('program_id') == target_prog 
                or str(r.get('program_id')) == str(target_prog)
                or r.get('program_id') in (0, None, '0')
                or target_prog in (0, None, '0')
            )
        ]
    except Exception as e:
        print(f"Error loading responses: {e}")
        return []

def load_local_responses_for_survey(survey_id):
    ensure_files_exist()
    try:
        with open(RESPONSES_FILE, 'r', encoding='utf-8') as f:
            all_responses = json.load(f)
        return [r for r in all_responses if str(r.get('survey_id')) == str(survey_id)]
    except Exception as e:
        print(f"Error loading responses for survey: {e}")
        return []

def save_local_response(inst_id, program_id, response_data):
    ensure_files_exist()
    try:
        with open(RESPONSES_FILE, 'r', encoding='utf-8') as f:
            all_responses = json.load(f)
        target_inst = int(inst_id) if str(inst_id).isdigit() else inst_id
        target_prog = int(program_id) if str(program_id).isdigit() else program_id
        response_data['inst_id'] = target_inst
        response_data['program_id'] = target_prog
        all_responses.append(response_data)
        with open(RESPONSES_FILE, 'w', encoding='utf-8') as f:
            json.dump(all_responses, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving response: {e}")
        return False

def sync_surveys_only(inst_id, program_id, supabase_client):
    """
    Syncs ONLY local surveys for inst_id and program_id to Supabase
    """
    try:
        target_inst = int(inst_id) if str(inst_id).isdigit() else inst_id
        target_prog = int(program_id) if str(program_id).isdigit() else program_id
        local_surveys = load_local_surveys(target_inst, target_prog)
        
        table_key = f"SURVEY_DEFINITIONS_{target_inst}_{target_prog}"
        check_surv = supabase_client.table('statistics').select("id").eq("table_id", table_key).eq("inst_id", target_inst).eq("program_id", target_prog).execute()
        if check_surv.data:
            supabase_client.table('statistics').update({"data_json": json.dumps(local_surveys, ensure_ascii=False)}).eq("id", check_surv.data[0]['id']).execute()
        else:
            old_check = supabase_client.table('statistics').select("id").eq("table_id", "SURVEY_DEFINITIONS").eq("inst_id", target_inst).eq("program_id", target_prog).execute()
            if old_check.data:
                supabase_client.table('statistics').update({
                    "table_id": table_key,
                    "data_json": json.dumps(local_surveys, ensure_ascii=False)
                }).eq("id", old_check.data[0]['id']).execute()
            else:
                supabase_client.table('statistics').insert({
                    "table_id": table_key,
                    "data_json": json.dumps(local_surveys, ensure_ascii=False),
                    "inst_id": target_inst,
                    "program_id": target_prog
                }).execute()
        return True
    except Exception as e:
        print(f"Error syncing surveys only: {e}")
        raise e

def sync_responses_only(inst_id, program_id, supabase_client):
    """
    Syncs ONLY local responses for inst_id and program_id to Supabase
    """
    try:
        target_inst = int(inst_id) if str(inst_id).isdigit() else inst_id
        target_prog = int(program_id) if str(program_id).isdigit() else program_id
        local_responses = load_local_responses(target_inst, target_prog)
        table_key = f"SURVEY_RESPONSES_{target_inst}_{target_prog}"
        check_resp = supabase_client.table('statistics').select("id").eq("table_id", table_key).eq("inst_id", target_inst).eq("program_id", target_prog).execute()
        if check_resp.data:
            supabase_client.table('statistics').update({"data_json": json.dumps(local_responses, ensure_ascii=False)}).eq("id", check_resp.data[0]['id']).execute()
        else:
            old_check = supabase_client.table('statistics').select("id").eq("table_id", "SURVEY_RESPONSES").eq("inst_id", target_inst).eq("program_id", target_prog).execute()
            if old_check.data:
                supabase_client.table('statistics').update({
                    "table_id": table_key,
                    "data_json": json.dumps(local_responses, ensure_ascii=False)
                }).eq("id", old_check.data[0]['id']).execute()
            else:
                supabase_client.table('statistics').insert({
                    "table_id": table_key,
                    "data_json": json.dumps(local_responses, ensure_ascii=False),
                    "inst_id": target_inst,
                    "program_id": target_prog
                }).execute()
        return True
    except Exception as e:
        print(f"Error syncing responses only: {e}")
        raise e

def sync_to_supabase(inst_id, program_id, supabase_client):
    try:
        sync_surveys_only(inst_id, program_id, supabase_client)
        sync_responses_only(inst_id, program_id, supabase_client)
        return True
    except Exception as e:
        print(f"Error syncing to Supabase: {e}")
        raise e

def pull_from_supabase(inst_id, program_id, supabase_client):
    """
    Loads surveys and responses from Supabase and overwrites/saves to local JSON
    ONLY if valid data is present (prevents wiping local files with empty arrays).
    """
    try:
        target_inst = int(inst_id) if str(inst_id).isdigit() else inst_id
        target_prog = int(program_id) if str(program_id).isdigit() else program_id
        
        # 1. Fetch surveys from Supabase
        table_key_surv = f"SURVEY_DEFINITIONS_{target_inst}_{target_prog}"
        table_key_inst = f"SURVEY_DEFINITIONS_{target_inst}_0"
        
        surv_res = supabase_client.table('statistics').select("data_json").eq("table_id", table_key_surv).eq("inst_id", target_inst).execute()
        if not surv_res.data and target_prog != 0:
            surv_res = supabase_client.table('statistics').select("data_json").eq("table_id", table_key_inst).eq("inst_id", target_inst).execute()
        if not surv_res.data:
            surv_res = supabase_client.table('statistics').select("data_json").eq("table_id", "SURVEY_DEFINITIONS").eq("inst_id", target_inst).execute()
            
        if surv_res.data and surv_res.data[0].get('data_json'):
            try:
                surveys = json.loads(surv_res.data[0]['data_json'])
                if isinstance(surveys, list) and len(surveys) > 0:
                    save_local_surveys(target_inst, target_prog, surveys)
            except Exception as ex_json:
                print("Error parsing survey json from cloud:", ex_json)
            
        # 2. Fetch responses from Supabase
        table_key_resp = f"SURVEY_RESPONSES_{target_inst}_{target_prog}"
        resp_res = supabase_client.table('statistics').select("data_json").eq("table_id", table_key_resp).eq("inst_id", target_inst).execute()
        if not resp_res.data:
            resp_res = supabase_client.table('statistics').select("data_json").eq("table_id", "SURVEY_RESPONSES").eq("inst_id", target_inst).execute()
            
        if resp_res.data and resp_res.data[0].get('data_json'):
            try:
                responses = json.loads(resp_res.data[0]['data_json'])
                if isinstance(responses, list) and len(responses) > 0:
                    ensure_files_exist()
                    with open(RESPONSES_FILE, 'r', encoding='utf-8') as f:
                        all_responses = json.load(f)
                    # Remove existing ones for this inst/prog
                    all_responses = [
                        r for r in all_responses 
                        if not (
                            (r.get('inst_id') == target_inst or str(r.get('inst_id')) == str(target_inst))
                            and (r.get('program_id') == target_prog or str(r.get('program_id')) == str(target_prog))
                        )
                    ]
                    all_responses.extend(responses)
                    with open(RESPONSES_FILE, 'w', encoding='utf-8') as f:
                        json.dump(all_responses, f, indent=2, ensure_ascii=False)
            except Exception as ex_json:
                print("Error parsing response json from cloud:", ex_json)
        return True
    except Exception as e:
        print(f"Error pulling from Supabase: {e}")
        return False
