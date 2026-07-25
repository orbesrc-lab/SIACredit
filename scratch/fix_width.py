import codecs

path = r"c:\SIAC\templates\formacion.html"
with codecs.open(path, 'r', 'utf-8') as f:
    lines = f.readlines()

# 1. Find <!-- REPOSITORIO GLOBAL -->
repo_idx = -1
for i, line in enumerate(lines):
    if '<!-- REPOSITORIO GLOBAL -->' in line:
        repo_idx = i
        break

# 2. Look above it for the </div> that closes content-area
# The structure before it was:
# </div> (closes studentCourseViewer or something)
# </div> (closes studentClassroom)
# </div> (closes settings-card)
# </div> (closes content-area)
#
# Let's just find the exact </div> that closes content-area.
# It is the </div> immediately preceding <!-- REPOSITORIO GLOBAL --> that corresponds to depth 0.
# Actually, the easiest way is to move the `</div>` that is directly ABOVE <!-- REPOSITORIO GLOBAL --> 
# and move it to the END of the settings-card of the global repository.

if repo_idx != -1:
    # Fix the title text
    for i in range(repo_idx, repo_idx + 10):
        if 'Y"s Repositorio SKEL y Metabuscador Global' in lines[i]:
            lines[i] = lines[i].replace('Y"s Repositorio SKEL y Metabuscador Global', '<i class="fas fa-globe" style="color: #6366f1; margin-right: 10px;"></i>Repositorio SKEL y Metabuscador Global')
            break

    # Now let's move the </div> closing content-area.
    # The line right before repo_idx is usually empty or `            </div>`
    for i in range(repo_idx - 1, repo_idx - 5, -1):
        if '</div>' in lines[i]:
            # This is the </div> that closes content-area
            lines[i] = '\n' # Remove it
            print(f"Removed </div> at {i+1}")
            break

    # Now find the end of globalLibraryContainer's settings-card
    end_idx = -1
    for i in range(len(lines)-1, repo_idx, -1):
        if '</div>' in lines[i]:
            end_idx = i
            break
            
    # Insert </div> at the very end
    if end_idx != -1:
        lines.insert(end_idx + 1, '            </div> <!-- END content-area -->\n')
        print(f"Added </div> at {end_idx + 2}")

    with codecs.open(path, 'w', 'utf-8') as f:
        f.writelines(lines)
    print("Done!")
else:
    print("Could not find REPOSITORIO GLOBAL")
