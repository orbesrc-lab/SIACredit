import sys
import re

html_file = 'c:/SIAC/templates/formacion.html'
with open(html_file, 'r', encoding='utf-8') as f:
    content = f.read()

target_str = 'id="student_email"'
if target_str in content and 'id="student_course_id"' not in content:
    idx = content.find(target_str)
    # find the end of this form-group
    end_div_idx = content.find('</div>\n                  </div>', idx)
    
    if end_div_idx != -1:
        insert_idx = end_div_idx + len('</div>\n                  </div>')
        
        replacement = '''
                  
                  <div class="form-group" style="margin-bottom: 30px;" id="studentCourseGroup">
                      <label style="display: block; margin-bottom: 8px; font-size: 0.9rem; font-weight: 600; color: var(--text-main);">Matricular en Curso (Opcional)</label>
                      <div style="position: relative;">
                          <span style="position: absolute; left: 15px; top: 50%; transform: translateY(-50%); font-size: 1.1rem; color: var(--text-muted);">📚</span>
                          <select id="student_course_id" style="width: 100%; padding: 14px 14px 14px 45px; border: 1px solid var(--border-color); border-radius: 12px; font-size: 0.95rem; font-family: 'Outfit', sans-serif; background: var(--secondary-bg); color: var(--text-main); outline: none;">
                              <option value="">-- No matricular aún --</option>
                          </select>
                      </div>
                  </div>'''
        
        content = content[:insert_idx] + replacement + content[insert_idx:]
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print('Dropdown HTML added successfully.')
    else:
        print('End of form-group not found.')
else:
    print('Dropdown HTML already exists or target not found.')
