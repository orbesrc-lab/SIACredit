with open(r'c:\SIAC\app.py', 'r', encoding='utf-8') as f:
    content = f.read()

replacement = """app.register_blueprint(backup_bp)

from routes.ai import ai_bp, call_ai
app.register_blueprint(ai_bp)
"""
content = content.replace("app.register_blueprint(backup_bp)", replacement)

with open(r'c:\SIAC\app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Registered ai blueprint.")
