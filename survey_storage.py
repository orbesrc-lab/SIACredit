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
        # Filter by inst_id and program_id
        return [s for s in all_surveys if s.get('inst_id') == inst_id and s.get('program_id') == program_id]
    except Exception as e:
        print(f"Error loading surveys: {e}")
        return []

def get_survey_by_id_only(survey_id):
    ensure_files_exist()
    try:
        with open(SURVEYS_FILE, 'r', encoding='utf-8') as f:
            all_surveys = json.load(f)
        for s in all_surveys:
            if s.get('id') == survey_id:
                return s
    except Exception as e:
        print(f"Error getting survey by id: {e}")
    return None

def save_local_surveys(inst_id, program_id, surveys_list):
    ensure_files_exist()
    try:
        with open(SURVEYS_FILE, 'r', encoding='utf-8') as f:
            all_surveys = json.load(f)
        # Remove existing ones for this inst/prog
        all_surveys = [s for s in all_surveys if not (s.get('inst_id') == inst_id and s.get('program_id') == program_id)]
        # Add new ones
        for s in surveys_list:
            s['inst_id'] = inst_id
            s['program_id'] = program_id
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
        return [r for r in all_responses if r.get('inst_id') == inst_id and r.get('program_id') == program_id]
    except Exception as e:
        print(f"Error loading responses: {e}")
        return []

def load_local_responses_for_survey(survey_id):
    ensure_files_exist()
    try:
        with open(RESPONSES_FILE, 'r', encoding='utf-8') as f:
            all_responses = json.load(f)
        return [r for r in all_responses if r.get('survey_id') == survey_id]
    except Exception as e:
        print(f"Error loading responses for survey: {e}")
        return []

def save_local_response(inst_id, program_id, response_data):
    ensure_files_exist()
    try:
        with open(RESPONSES_FILE, 'r', encoding='utf-8') as f:
            all_responses = json.load(f)
        response_data['inst_id'] = inst_id
        response_data['program_id'] = program_id
        all_responses.append(response_data)
        with open(RESPONSES_FILE, 'w', encoding='utf-8') as f:
            json.dump(all_responses, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving response: {e}")
        return False

def sync_to_supabase(inst_id, program_id, supabase_client):
    """
    Syncs local surveys and responses for inst_id and program_id to Supabase table 'statistics'
    using table_id = 'SURVEY_DEFINITIONS' and 'SURVEY_RESPONSES'
    """
    try:
        local_surveys = load_local_surveys(inst_id, program_id)
        local_responses = load_local_responses(inst_id, program_id)
        
        # 1. Sync Surveys
        check_surv = supabase_client.table('statistics').select("id").eq("table_id", "SURVEY_DEFINITIONS").eq("inst_id", inst_id).eq("program_id", program_id).execute()
        if check_surv.data:
            supabase_client.table('statistics').update({"data_json": json.dumps(local_surveys, ensure_ascii=False)}).eq("id", check_surv.data[0]['id']).execute()
        else:
            supabase_client.table('statistics').insert({
                "table_id": "SURVEY_DEFINITIONS",
                "data_json": json.dumps(local_surveys, ensure_ascii=False),
                "inst_id": inst_id,
                "program_id": program_id
            }).execute()
            
        # 2. Sync Responses
        check_resp = supabase_client.table('statistics').select("id").eq("table_id", "SURVEY_RESPONSES").eq("inst_id", inst_id).eq("program_id", program_id).execute()
        if check_resp.data:
            supabase_client.table('statistics').update({"data_json": json.dumps(local_responses, ensure_ascii=False)}).eq("id", check_resp.data[0]['id']).execute()
        else:
            supabase_client.table('statistics').insert({
                "table_id": "SURVEY_RESPONSES",
                "data_json": json.dumps(local_responses, ensure_ascii=False),
                "inst_id": inst_id,
                "program_id": program_id
            }).execute()
        return True
    except Exception as e:
        print(f"Error syncing to Supabase: {e}")
        raise e

def pull_from_supabase(inst_id, program_id, supabase_client):
    """
    Loads surveys and responses from Supabase and overwrites/saves to local JSON
    """
    try:
        # 1. Fetch surveys from Supabase
        surv_res = supabase_client.table('statistics').select("data_json").eq("table_id", "SURVEY_DEFINITIONS").eq("inst_id", inst_id).eq("program_id", program_id).execute()
        if surv_res.data:
            surveys = json.loads(surv_res.data[0]['data_json'])
            save_local_surveys(inst_id, program_id, surveys)
            
        # 2. Fetch responses from Supabase
        resp_res = supabase_client.table('statistics').select("data_json").eq("table_id", "SURVEY_RESPONSES").eq("inst_id", inst_id).eq("program_id", program_id).execute()
        if resp_res.data:
            responses = json.loads(resp_res.data[0]['data_json'])
            ensure_files_exist()
            with open(RESPONSES_FILE, 'r', encoding='utf-8') as f:
                all_responses = json.load(f)
            # Remove existing ones
            all_responses = [r for r in all_responses if not (r.get('inst_id') == inst_id and r.get('program_id') == program_id)]
            # Add fetched ones
            all_responses.extend(responses)
            with open(RESPONSES_FILE, 'w', encoding='utf-8') as f:
                json.dump(all_responses, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error pulling from Supabase: {e}")
        return False
