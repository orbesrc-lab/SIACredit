import sys

def trace_divs(filepath, target_line):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    stack = []
    for i in range(target_line):
        line = lines[i]
        # extremely naive but good enough for rough idea
        if '<div' in line:
            # find all <div and count
            start_idx = 0
            while True:
                idx = line.find('<div', start_idx)
                if idx == -1: break
                
                # find id or class
                id_start = line.find('id="', idx)
                class_start = line.find('class="', idx)
                desc = "div"
                if id_start != -1 and id_start < line.find('>', idx):
                    desc += f" id={line[id_start+4:line.find('\"', id_start+4)]}"
                elif class_start != -1 and class_start < line.find('>', idx):
                    desc += f" class={line[class_start+7:line.find('\"', class_start+7)]}"
                
                stack.append(f"{desc} (line {i+1})")
                start_idx = idx + 4
                
        if '</div' in line:
            count = line.count('</div')
            for _ in range(count):
                if stack:
                    stack.pop()

    print("DIV STACK AT LINE", target_line)
    for s in stack:
        print("  " + s)

trace_divs('c:/SIAC/templates/formacion.html', 974)
