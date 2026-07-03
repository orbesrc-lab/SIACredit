import re

with open(r'c:\SIAC\app.py', 'r', encoding='utf-8') as f:
    content = f.read()

replacement = """CORS(app)

from routes.crm import crm_bp
app.register_blueprint(crm_bp)
"""
content = content.replace("CORS(app)", replacement)

with open(r'c:\SIAC\app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Registered crm blueprint.")
