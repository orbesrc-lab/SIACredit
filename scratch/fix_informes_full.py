import re

# ============================================================
# FIX 1: informes.html - Audit and repair all script tags
# ============================================================
with open(r'c:\SIAC\templates\informes.html', 'r', encoding='utf-8') as f:
    content = f.read()

print(f"Before: <script={content.count('<script')}, </script>={content.count('</script>')}")
print(f"Before: </body>={content.count('</body>')}, </html>={content.count('</html>')}")

# Remove ALL extra </body> and </html> except the last ones
# Strategy: split on </html>, keep all content but ensure only 1 at the end
# Find all positions of </body> and </html>
body_positions = [m.start() for m in re.finditer(r'</body>', content)]
html_positions = [m.start() for m in re.finditer(r'</html>', content)]

print("body positions:", body_positions)
print("html positions:", html_positions)

# Remove all premature </body></html> that are NOT at the end of the file
# The last one should stay
if len(body_positions) > 1:
    # Remove all but the last
    for pos in reversed(body_positions[:-1]):
        end_pos = pos + len('</body>')
        # Check context - if it's followed by \n</html> or similar, remove both
        snippet = content[pos:pos+20]
        if '</html>' in snippet:
            # Remove both </body> and </html>
            content = content[:pos] + content[pos:].replace(snippet, '', 1)
        else:
            content = content[:pos] + content[pos+len('</body>'):]

if len(html_positions) > 1:
    html_positions = [m.start() for m in re.finditer(r'</html>', content)]
    for pos in reversed(html_positions[:-1]):
        content = content[:pos] + content[pos+len('</html>'):]

print(f"\nAfter body/html cleanup:")
print(f"  <script={content.count('<script')}, </script>={content.count('</script>')}")
print(f"  </body>={content.count('</body>')}, </html>={content.count('</html>')}")

# Now fix script tag imbalance
# Find script blocks that are NOT closed
opens = [m.start() for m in re.finditer(r'<script[^>]*>', content)]
closes = [m.start() for m in re.finditer(r'</script>', content)]
print(f"\n<script open positions (count={len(opens)}): {opens[:5]}...")
print(f"</script> close positions (count={len(closes)}): {closes[:5]}...")

with open(r'c:\SIAC\templates\informes.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("\nFile saved. Now manual inspection needed.")
