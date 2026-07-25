with open('c:\\SIAC\\templates\\formacion.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Count occurrences of the QUIZ TAKER marker
marker = '// --- QUIZ TAKER (ESTUDIANTE) ---'
count = html.count(marker)
print(f'Found {count} occurrences of QUIZ TAKER marker')

if count > 1:
    # Keep only the first occurrence of the full block
    # Find the first occurrence
    first_idx = html.find(marker)
    # Find the second occurrence
    second_idx = html.find(marker, first_idx + len(marker))
    
    if second_idx > 0:
        # Remove from second_idx onwards (up to </script> before it)
        # Actually we need to remove the duplicate block between second_idx and the next non-duplicate boundary
        # Better: find ALL blocks and keep only the first
        # The marker appears before 'function takeQuiz' and ends at the closing of submitQuizAnswers
        # Let's remove everything from second marker to just before the next non-quiz content
        
        # Find the third occurrence if any
        third_idx = html.find(marker, second_idx + len(marker))
        
        if third_idx > 0:
            # Remove the block from second_idx to third_idx
            block_to_remove = html[second_idx:third_idx]
            html = html[:second_idx] + html[third_idx:]
            print(f'Removed block from {second_idx} to {third_idx}')
        
        # Now remove the remaining duplicate (was third, now second)
        second_idx2 = html.find(marker, first_idx + len(marker))
        if second_idx2 > 0:
            # Find where this block ends - look for next '</script>' after it
            end_idx = html.find('</script>', second_idx2)
            block_to_remove2 = html[second_idx2:end_idx]
            html = html[:second_idx2] + html[end_idx:]
            print(f'Removed second block from {second_idx2} to {end_idx}')

# Also check and remove duplicate takeQuizModal HTML
modal_marker = '<!-- Modal para Presentar Cuestionario'
modal_count = html.count(modal_marker)
print(f'Found {modal_count} occurrences of takeQuizModal')

if modal_count > 1:
    first_m_idx = html.find(modal_marker)
    second_m_idx = html.find(modal_marker, first_m_idx + len(modal_marker))
    # Remove from second occurrence up to the closing </div>\n        </div>
    # The modal ends with </div>\n        </div>\n
    # Find the closing of the second modal by looking for '<!-- Modal de Calificación' after second
    end_m_idx = html.find('<!-- Modal de Calificación -->', second_m_idx)
    if end_m_idx > 0:
        html = html[:second_m_idx] + html[end_m_idx:]
        print(f'Removed duplicate modal from {second_m_idx} to {end_m_idx}')

with open('c:\\SIAC\\templates\\formacion.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('Done')
