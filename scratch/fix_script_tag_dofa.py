import os

file_informes = r'c:\SIAC\templates\informes.html'
with open(file_informes, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix premature </script> on line 3585 before renderDOFA
old_block = """            Swal.fire('Error', 'No se pudieron guardar los permisos', 'error');
        }
    }
</script>



        function renderDOFA(dofaData) {"""

new_block = """            Swal.fire('Error', 'No se pudieron guardar los permisos', 'error');
        }
    }

        function renderDOFA(dofaData) {"""

if old_block in content:
    content = content.replace(old_block, new_block)
else:
    # Remove any extra </script> right before function renderDOFA
    content = content.replace("</script>\n\n\n\n        function renderDOFA(dofaData) {", "\n        function renderDOFA(dofaData) {")
    content = content.replace("</script>\n\n        function renderDOFA(dofaData) {", "\n        function renderDOFA(dofaData) {")

with open(file_informes, 'w', encoding='utf-8') as f:
    f.write(content)

print("Premature </script> tag before renderDOFA removed successfully!")
