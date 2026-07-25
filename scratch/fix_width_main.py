import codecs

path = r"c:\SIAC\templates\formacion.html"
with codecs.open(path, 'r', 'utf-8') as f:
    lines = f.readlines()

# Find the end of content-area that we just added at the very end of the file
end_idx = -1
for i in range(len(lines) - 1, -1, -1):
    if '</div> <!-- END content-area -->' in lines[i]:
        end_idx = i
        break

if end_idx != -1:
    line_to_move = lines.pop(end_idx)
    
    # Find </main>
    main_idx = -1
    for i in range(len(lines)):
        if '</main>' in lines[i]:
            main_idx = i
            break
            
    if main_idx != -1:
        lines.insert(main_idx, line_to_move)
        
        with codecs.open(path, 'w', 'utf-8') as f:
            f.writelines(lines)
        print("Moved </div> successfully before </main>")
    else:
        print("Could not find </main>")
else:
    print("Could not find the </div> we added")
