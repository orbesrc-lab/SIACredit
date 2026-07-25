with open(r'c:\SIAC\app.py', 'r', encoding='utf-8') as f:
    content = f.read()

replacement = """app.register_blueprint(surveys_bp)

from routes.planning import planning_bp
app.register_blueprint(planning_bp)
"""
content = content.replace("app.register_blueprint(surveys_bp)", replacement)

with open(r'c:\SIAC\app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Registered planning blueprint.")
