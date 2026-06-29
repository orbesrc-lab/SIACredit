with open('c:\\SIAC\\templates\\formacion.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Remove addTopicPrompt function definition if it still exists
import re
# We just need to replace the onclick call
html = html.replace('onclick="addTopicPrompt(', 'onclick="openAddTopicModal(')

# Update openStudentCourse to render dynamic icons for topics
def replace_student_topic(m):
    # This is complex, better to do it manually via replace_file_content
    pass

with open('c:\\SIAC\\templates\\formacion.html', 'w', encoding='utf-8') as f:
    f.write(html)
