with open('c:\\SIAC\\templates\\formacion.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add .form-input CSS to the existing style block
form_input_css = """
        /* Quiz editor inputs */
        .form-input {
            width: 100%;
            padding: 10px 12px;
            border: 1px solid #cbd5e1;
            border-radius: 8px;
            font-size: 0.9rem;
            font-family: 'Outfit', sans-serif;
            background: #ffffff;
            color: #0f172a;
            box-sizing: border-box;
            outline: none;
            display: block;
        }
        .form-input:focus {
            border-color: #6366f1;
            box-shadow: 0 0 0 3px rgba(99,102,241,0.15);
        }
        select.form-input {
            cursor: pointer;
        }
        textarea.form-input {
            resize: vertical;
            min-height: 70px;
        }
"""

# Add CSS before the closing </style> of the first style block
style_end_idx = html.find('</style>')
if style_end_idx > 0:
    html = html[:style_end_idx] + form_input_css + html[style_end_idx:]
    print('Added form-input CSS')

# 2. Fix topicModal select and input - they use class="form-input" in HTML  
# These are in the static HTML, so they'll now be styled by the CSS above

# 3. Fix the topic modal 'form-input' on the input and select in HTML
old_topic_input = '<input type="text" id="topicName" class="form-input" placeholder="Ej. Introducción">'
new_topic_input = '<input type="text" id="topicName" style="width:100%; padding:10px 12px; border:1px solid #cbd5e1; border-radius:8px; font-size:0.9rem; font-family:sans-serif; background:#fff; color:#0f172a; box-sizing:border-box; display:block;" placeholder="Ej. Introducción al tema...">'

if old_topic_input in html:
    html = html.replace(old_topic_input, new_topic_input)
    print('Fixed topicName input')

old_topic_select = '<select id="topicType" class="form-input">'
new_topic_select = '<select id="topicType" style="width:100%; padding:10px 12px; border:1px solid #cbd5e1; border-radius:8px; font-size:0.9rem; font-family:sans-serif; background:#fff; color:#0f172a; box-sizing:border-box; display:block;">'

if old_topic_select in html:
    html = html.replace(old_topic_select, new_topic_select)
    print('Fixed topicType select')

with open('c:\\SIAC\\templates\\formacion.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('Done')
