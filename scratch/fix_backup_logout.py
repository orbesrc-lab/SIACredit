import re

def fix_backup_html():
    with open('c:\\SIAC\\templates\\backup.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Add logout() if missing
    if 'function logout()' not in content:
        logout_func = "\n    function logout() { localStorage.removeItem('siac_user'); window.location.href = 'index.html'; }\n"
        content = content.replace('<script>', '<script>' + logout_func)

    # 2. Add an explicit click handler for the modal close and backdrop if missing?
    # Ensure all buttons actually exist.
    
    # 3. Add console logs for debugging
    if 'console.log("requireSecurity' not in content:
        content = content.replace('function requireSecurity(actionFunc, args) {', 'function requireSecurity(actionFunc, args) { console.log("requireSecurity called with", actionFunc, args);')
        
    if 'console.log("confirmSecurity' not in content:
        content = content.replace('async function confirmSecurity() {', 'async function confirmSecurity() { console.log("confirmSecurity clicked");')

    with open('c:\\SIAC\\templates\\backup.html', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    fix_backup_html()
