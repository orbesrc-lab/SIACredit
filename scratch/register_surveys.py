with open(r'c:\SIAC\app.py', 'r', encoding='utf-8') as f:
    content = f.read()

replacement = """app.register_blueprint(ai_bp)

from routes.surveys import surveys_bp
app.register_blueprint(surveys_bp)
"""
content = content.replace("app.register_blueprint(ai_bp)", replacement)

with open(r'c:\SIAC\app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Registered surveys blueprint.")
