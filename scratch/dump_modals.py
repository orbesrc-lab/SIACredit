import re

with open('c:/SIAC/templates/formacion.html', encoding='utf-8') as f:
    content = f.read()

def extract_modal(modal_id):
    start = content.find(f'id="{modal_id}"')
    if start == -1: return f"Not found: {modal_id}"
    start = content.rfind('<div', 0, start)
    # Simple extraction of the next 2000 chars to cover the modal
    return content[start:start+2500]

with open('c:/SIAC/scratch/modals_dump.txt', 'w', encoding='utf-8') as out:
    out.write("=== TOPIC EDITOR ===\n")
    out.write(extract_modal("topicEditorModal"))
    out.write("\n\n=== SUBMISSIONS ===\n")
    out.write(extract_modal("studentSubmitActivityModal")) # Try to find this or similar
    out.write("\n\n=== RESOURCE ===\n")
    out.write(extract_modal("unitResourceModal"))
