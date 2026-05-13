import docx
import json

doc = docx.Document('c:\\SIAC\\Capitulo4_Profesores_Contaduria.docx')

tables_data = []

for idx, table in enumerate(doc.tables):
    table_data = []
    for row in table.rows:
        row_data = []
        for cell in row.cells:
            row_data.append(cell.text.strip().replace("\n", " "))
        table_data.append(row_data)
    tables_data.append({"index": idx, "data": table_data})

print(json.dumps(tables_data, indent=2, ensure_ascii=False))
