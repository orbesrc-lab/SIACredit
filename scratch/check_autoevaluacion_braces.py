import re

filepath = "templates/autoevaluacion.html"
with open(filepath, "r", encoding="utf-8") as f:
    html = f.read()

# Extract script blocks
scripts = re.findall(r"<script>(.*?)</script>", html, re.DOTALL)

for idx, script in enumerate(scripts):
    print(f"Checking script block {idx+1}...")
    stack = []
    lines = script.split("\n")
    for line_num, line in enumerate(lines, 1):
        for char_num, char in enumerate(line, 1):
            if char in "({[":
                stack.append((char, line_num, char_num, line))
            elif char in ")}]":
                if not stack:
                    print(f"Error: Unmatched closing character '{char}' at line {line_num}, char {char_num}:")
                    print(f"  Line: {line}")
                    break
                top, t_line, t_char, t_content = stack.pop()
                if (char == ")" and top != "(") or (char == "}" and top != "{") or (char == "]" and top != "["):
                    print(f"Error: Mismatched closing character '{char}' at line {line_num}, char {char_num} matching '{top}' from line {t_line}, char {t_char}:")
                    print(f"  Current Line: {line}")
                    print(f"  Opening Line: {t_content}")
                    break
    if stack:
        print(f"Error: {len(stack)} unclosed opening characters left:")
        for top, t_line, t_char, t_content in stack[-5:]:
            print(f"  '{top}' at line {t_line}, char {t_char}: {t_content.strip()}")
    else:
        print(f"Script block {idx+1} is balanced!")
