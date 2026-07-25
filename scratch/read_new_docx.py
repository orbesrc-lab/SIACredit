import docx
import json

def extract_from(filename):
    print(f"Extracting tables from {filename}...")
    try:
        doc = docx.Document(filename)
        tables_data = []
        for idx, table in enumerate(doc.tables):
            table_data = []
            for row in table.rows:
                row_data = []
                for cell in row.cells:
                    row_data.append(cell.text.strip())
                table_data.append(row_data)
            tables_data.append({
                "index": idx,
                "data": table_data
            })
        
        for t in tables_data:
            if t["data"]:
                print(f"Table {t['index']} headers: {t['data'][0]}")
    except Exception as e:
        print(f"Error reading {filename}: {e}")

extract_from('c:/SIAC/Capitulo6_Investigacion_Contaduria.docx')
print("-" * 50)
extract_from('c:/SIAC/Capitulo9_Infraestructura_Fisica_Contaduria.docx')
