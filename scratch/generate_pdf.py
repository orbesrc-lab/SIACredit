import os
import time
import json
from fpdf import FPDF
from supabase import create_client

print("Iniciando generacion de PDF...")

# Generar PDF
pdf = FPDF()
pdf.add_page()
pdf.set_font('helvetica', 'B', 16)
pdf.cell(0, 10, 'Manual de Usuario - Sistema SIAC', ln=True, align='C')
pdf.ln(10)

pdf.set_font('helvetica', '', 12)
text = """Bienvenido al Manual de Usuario del Sistema SIAC.

1. CONFIGURACION INICIAL
Al ingresar al sistema, lo primero que debe hacer es seleccionar la 'Institucion' y el 'Programa Academico' en la esquina superior derecha. Esto filtrara todos los datos, evidencias y estadisticas para mostrar solo lo correspondiente a ese programa.

2. MODULO DE EVIDENCIAS
En este modulo podra subir los soportes de cada uno de los Factores.
- Para subir un archivo: Haga clic en 'Subir Archivo' o el icono de nube. Seleccione su PDF. El sistema lo subira directamente a la nube (Supabase) evitando limites de peso.
- Para ver un archivo: Haga clic en el boton con el icono del 'Ojo' (Ver). Se abrira un visor flotante.
- Si sube un archivo con el mismo nombre, el sistema le asignara un codigo unico para evitar colisiones.

3. MODULO DE ESTADISTICAS
Aqui puede registrar datos numericos en tablas dinamicas (Ej. cantidad de profesores, aulas, etc).
- Modifique los valores directamente en las celdas.
- Puede subir un archivo de soporte (Adjunto) por cada fila usando el icono de clip.
- IMPORTANTE: Para que los cambios y los archivos adjuntos se guarden, debe presionar el boton 'Guardar Cuadros' que aparece flotando en la parte inferior.

4. BIBLIOTECA
Este modulo contiene documentos de referencia general e institucional.
- Puede subir archivos de gran tamano directamente.
- Puede previsualizar cualquier documento haciendo clic en 'Ver'.

5. VISOR DE DOCUMENTOS
El visor integrado permite leer PDFs sin salir de la plataforma. Si accede desde un celular o tablet, el sistema detectara su dispositivo y utilizara el motor de Google Docs para garantizar compatibilidad total.

(Documento generado automaticamente por Adriana - IA)"""

pdf.multi_cell(0, 10, text)

file_path = 'scratch/Manual_SIAC.pdf'
pdf.output(file_path)
print('PDF generated at', file_path)

print("Leyendo credenciales de app.py...")
from dotenv import load_dotenv
load_dotenv()

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')

if not url or not key:
    print("Error: No se pudieron obtener las credenciales de Supabase del .env.")
    exit(1)

print("Conectando a Supabase...")
supabase = create_client(url, key)

storage_path = 'inst_1/prog_1/BIBLIOTECA_GLOBAL/General/Manual_SIAC_Uso_General.pdf'
print("Subiendo PDF a Supabase Storage...")
with open(file_path, 'rb') as f:
    supabase.storage.from_('evidencias').upload(
        path=storage_path,
        file=f.read(),
        file_options={'content-type': 'application/pdf', 'upsert': 'true'}
    )

file_url = supabase.storage.from_('evidencias').get_public_url(storage_path)
print('Uploaded to Supabase:', file_url)

print("Actualizando base de datos (statistics)...")
aspect_id = 'BIBLIOTECA_GLOBAL'
doc_record = {
    'id': int(time.time() * 1000),
    'name': 'Manual_SIAC_Uso_General.pdf',
    'file_url': file_url,
    'aspect_id': aspect_id
}

check = supabase.table('statistics').select('id, data_json').eq('table_id', aspect_id).execute()
if check.data:
    current_data = json.loads(check.data[0]['data_json'])
    if not isinstance(current_data, list): current_data = []
    current_data.insert(0, doc_record)
    supabase.table('statistics').update({'data_json': json.dumps(current_data)}).eq('id', check.data[0]['id']).execute()
else:
    supabase.table('statistics').insert({
        'table_id': aspect_id,
        'data_json': json.dumps([doc_record]),
        'inst_id': 1,
        'program_id': 1
    }).execute()

print('EXITO! El manual fue subido y registrado en la biblioteca correctamente.')
