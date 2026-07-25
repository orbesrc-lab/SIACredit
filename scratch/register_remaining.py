with open(r'c:\SIAC\app.py', 'r', encoding='utf-8') as f:
    content = f.read()

replacement = """app.register_blueprint(planning_bp)

from routes.core import core_bp
from routes.reports import reports_bp
from routes.prospects import prospects_bp
app.register_blueprint(core_bp)
app.register_blueprint(reports_bp)
app.register_blueprint(prospects_bp)
"""
content = content.replace("app.register_blueprint(planning_bp)", replacement)

with open(r'c:\SIAC\app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Registered core, reports, and prospects blueprints.")
