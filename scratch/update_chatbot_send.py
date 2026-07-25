import re

with open('static/chatbot.js', 'r', encoding='utf-8') as f:
    content = f.read()

new_logic = '''
    // 2. Simular tiempo de "escribiendo" (300ms a 600ms)
    setTimeout(() => {
        const reply = getBotResponse(msg);
        
        // Si no se encontró respuesta, enviar al servidor para registro
        if (reply === FALLBACK_RESPONSE) {
            fetch('/api/bot/unanswered', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question: msg })
            }).catch(e => console.log("Error registrando log:", e));
        }

        const botBubble = document.createElement('div');
        botBubble.className = 'skel-message bot';
'''

content = content.replace('''
    // 2. Simular tiempo de "escribiendo" (300ms a 600ms)
    setTimeout(() => {
        const reply = getBotResponse(msg);
        
        const botBubble = document.createElement('div');
        botBubble.className = 'skel-message bot';'''.strip(), new_logic.strip())

with open('static/chatbot.js', 'w', encoding='utf-8') as f:
    f.write(content)
print('Updated chatbot logic')
