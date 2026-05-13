import docx

def extract_from(filename):
    print(f"\n{'='*60}\nExtracting from: {filename}\n{'='*60}")
    try:
        doc = docx.Document(filename)
        for idx, table in enumerate(doc.tables):
            table_data = []
            for row in table.rows:
                row_data = []
                for cell in row.cells:
                    row_data.append(cell.text.strip().replace('\n', ' '))
                if any(row_data):
                    table_data.append(row_data)
            
            if table_data:
                print(f"Table {idx} headers: {table_data[0]}")
    except Exception as e:
        print(f"Error reading {filename}: {e}")

files = [
    'c:/SIAC/Capitulo3_Aspectos_Curriculares_Contaduria (1) (1).docx',
    'c:/SIAC/Capitulo5_Relaciones_Sector_Externo_Contaduria.docx',
    'c:/SIAC/Capitulo8_Medios_Educativos_Contaduria.docx'
]

for f in files:
    extract_from(f)
