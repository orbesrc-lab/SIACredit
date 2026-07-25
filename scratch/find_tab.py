with open('c:/SIAC/templates/formacion.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

def trace_div(id_str):
    start = 0
    for i, line in enumerate(lines):
        if f'id="{id_str}"' in line:
            start = i
            break
    
    stack = []
    for i in range(start, len(lines)):
        line = lines[i]
        if '<div' in line: stack.extend(['div'] * line.count('<div'))
        if '</div' in line:
            for _ in range(line.count('</div')):
                if stack: stack.pop()
            if len(stack) == 0:
                print(f"{id_str} closes at line {i+1}")
                return i+1

print("Tracing tabs...")
t_end = trace_div('coursesTab')
t_end = trace_div('teachersTab')
t_end = trace_div('studentsTab')
t_end = trace_div('studentCourseViewer')
