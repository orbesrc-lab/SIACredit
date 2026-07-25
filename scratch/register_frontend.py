with open(r'c:\SIAC\app.py', 'r', encoding='utf-8') as f:
    content = f.read()

replacement = """app.register_blueprint(crm_bp)

from routes.frontend import frontend_bp
app.register_blueprint(frontend_bp)
"""
content = content.replace("app.register_blueprint(crm_bp)", replacement)

with open(r'c:\SIAC\app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Registered frontend blueprint.")
