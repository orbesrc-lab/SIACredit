import os
import io
import json
import uuid
import datetime
import PyPDF2
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
from flask import Blueprint, jsonify, request, render_template, send_file
from routes.ai import call_ai
from utils.db import supabase, get_active_inst_id
from utils.auth import require_permission

asesor_juridico_bp = Blueprint('asesor_juridico', __name__)

# ==============================================================================
# NORMAGRAMA BASE DE EDUCACIÓN SUPERIOR EN COLOMBIA
# ==============================================================================
NORMAGRAMA_BASE = [
    {
        "id": "ley_30_1992",
        "norma": "Ley 30 de 1992",
        "titulo": "Ley de Educación Superior",
        "entidad": "Congreso de la República",
        "fecha": "1992-12-28",
        "estado": "Vigente con modificaciones",
        "alcance": "Organización del servicio público de la educación superior, campos de acción, autonomía universitaria (Art. 28 y 29), órganos de gobierno y régimen contractual (Art. 93).",
        "aplicabilidad_ies": "Universal para todas las IES (Públicas, Privadas, Oficiales y Adscritas)."
    },
    {
        "id": "ley_749_2002",
        "norma": "Ley 749 de 2002",
        "titulo": "Ciclos Propedéuticos y Redefinición / Cambio de Carácter",
        "entidad": "Congreso de la República",
        "fecha": "2002-07-19",
        "estado": "Vigente",
        "alcance": "Organización de la formación técnica profesional y tecnológica por ciclos propedéuticos. Establece el régimen y requisitos para el cambio de carácter académico a Institución Universitaria o Escuela Tecnológica.",
        "aplicabilidad_ies": "Instituciones Técnicas Profesionales e Instituciones Tecnológicas en proceso de redefinición."
    },
    {
        "id": "dec_2038_2024",
        "norma": "Decreto 2038 de 2024 (y 2023)",
        "titulo": "Reglamentación del Proceso de Redefinición y Cambio de Carácter",
        "entidad": "Ministerio de Educación Nacional",
        "fecha": "2024-11-27",
        "estado": "Vigente",
        "alcance": "Reglamenta las etapas, requisitos, condiciones institucionales, evaluación por CONACES y resolución ministerial para la redefinición institucional y cambio de carácter.",
        "aplicabilidad_ies": "Trámites de cambio de carácter ante el MEN."
    },
    {
        "id": "dur_1075_2015",
        "norma": "Decreto 1075 de 2015 (DUR)",
        "titulo": "Decreto Único Reglamentario del Sector Educación",
        "entidad": "Ministerio de Educación Nacional",
        "fecha": "2015-05-26",
        "estado": "Vigente con modificaciones sucesivas",
        "alcance": "Compilación del régimen general de la educación superior en Colombia (Libro 2, Parte 5). Marco transversal para trámites, inspección y vigilancia.",
        "aplicabilidad_ies": "Marco regulatorio único del sector."
    },
    {
        "id": "dec_1330_2019",
        "norma": "Decreto 1330 de 2019",
        "titulo": "Condiciones de Calidad para Registro Calificado",
        "entidad": "Ministerio de Educación Nacional",
        "fecha": "2019-07-25",
        "estado": "Modificado puntualmente por Decreto 0529 de 2024",
        "alcance": "Sustituye el Capítulo 2 del Título 3 Parte 5 Libro 2 del DUR 1075 de 2015. Define las 9 condiciones institucionales y 9 de programa para registro calificado y resultados de aprendizaje.",
        "aplicabilidad_ies": "Registros calificados nuevos, renovaciones y modificaciones."
    },
    {
        "id": "dec_0529_2024",
        "norma": "Decreto 0529 de 2024",
        "titulo": "Modernización y Agilidad en Registro Calificado y Calidad",
        "entidad": "Ministerio de Educación Nacional",
        "fecha": "2024-04-29",
        "estado": "Vigente",
        "alcance": "Modifica disposiciones del DUR 1075 y Dec. 1330 para simplificar trámites de registro calificado, flexibilizar evidencias, reconocer diversidad territorial e institucional y articular trámites ágiles.",
        "aplicabilidad_ies": "Todos los trámites actuales ante Sala CONACES."
    },
    {
        "id": "acuerdo_01_cesu_2025",
        "norma": "Acuerdo 01 de 2025 del CESU",
        "titulo": "Nuevo Modelo y Lineamientos de Acreditación en Alta Calidad",
        "entidad": "Consejo Nacional de Educación Superior (CESU)",
        "fecha": "2025-01-20",
        "estado": "Vigente",
        "alcance": "Actualiza el Sistema Nacional de Acreditación (SNA), factores y características de autoevaluación y evaluación externa por pares CNA.",
        "aplicabilidad_ies": "Procesos de Acreditación Institucional y de Programas."
    },
    {
        "id": "ley_115_1994",
        "norma": "Ley 115 de 1994",
        "titulo": "Ley General de Educación",
        "entidad": "Congreso de la República",
        "fecha": "1994-02-08",
        "estado": "Vigente con modificaciones",
        "alcance": "Fines de la educación, articulación de niveles educativos y principios pedagógicos del sistema educativo colombiano.",
        "aplicabilidad_ies": "Articulación con la media y formación docente."
    },
    {
        "id": "ley_1437_2011",
        "norma": "Ley 1437 de 2011 (CPACA)",
        "titulo": "Código de Procedimiento Administrativo y de lo Contencioso Administrativo",
        "entidad": "Congreso de la República",
        "fecha": "2011-01-18",
        "estado": "Vigente con modificaciones de la Ley 2080 de 2021",
        "alcance": "Procedimientos administrativos ante el MEN, régimen de recursos (reposición y apelación), expedición de actos administrativos, silencio administrativo y caducidad.",
        "aplicabilidad_ies": "Defensa jurídica institucional ante actos del MEN y CONACES."
    },
    {
        "id": "ley_489_1998",
        "norma": "Ley 489 de 1998",
        "titulo": "Estatuto Básico de la Administración Pública",
        "entidad": "Congreso de la República",
        "fecha": "1998-12-29",
        "estado": "Vigente",
        "alcance": "Estructura y principios de la función pública, descentralización, desconcentración y delegación aplicable a IES oficiales y adscritas.",
        "aplicabilidad_ies": "IES Públicas, Oficiales, Adscritas o Vinculadas."
    },
    {
        "id": "ley_909_2004",
        "norma": "Ley 909 de 2004",
        "titulo": "Régimen del Empleo Público y Carrera Administrativa",
        "entidad": "Congreso de la República",
        "fecha": "2004-09-23",
        "estado": "Vigente",
        "alcance": "Regulación de personal administrativo en IES oficiales, empleos de libre nombramiento vs. carrera administrativa.",
        "aplicabilidad_ies": "Personal no docente en IES de carácter público."
    },
    {
        "id": "jur_autonomia_corte",
        "norma": "Jurisprudencia de la Corte Constitucional (Sentencias C-220/97, C-008/01, C-1435/00)",
        "titulo": "Línea Jurisprudencial en Autonomía Universitaria",
        "entidad": "Corte Constitucional de Colombia",
        "fecha": "2001-01-31",
        "estado": "Doctrina Constitucional Vinculante",
        "alcance": "Garantiza a las IES la potestad de autodeterminación ideológica, académica, administrativa y de gobierno propio, limitada únicamente por el orden público y la inspección y vigilancia del Estado sin intromisiones indebidas.",
        "aplicabilidad_ies": "Blindaje de reglamentos, estatutos y decisiones de Consejo Directivo."
    }
]

# ==============================================================================
# HELPERS DE BASE DE DATOS Y PERSISTENCIA
# ==============================================================================
def get_juridico_project(inst_id):
    """Obtiene el estado de casos y expedientes jurídicos para la institución."""
    table_id = f"ASESOR_JURIDICO_{inst_id}"
    try:
        res = supabase.table('statistics').select('data_json').eq('table_id', table_id).execute()
        if res.data and res.data[0].get('data_json'):
            return json.loads(res.data[0]['data_json'])
    except Exception as e:
        print(f"[Asesor Juridico] Error fetch: {e}")

    # Estructura inicial
    return {
        "inst_id": inst_id,
        "casos": [],
        "normagrama_personalizado": list(NORMAGRAMA_BASE),
        "estatuto_institucional_resumen": "INTENALCO EDUCACIÓN SUPERIOR: Institución Técnica Profesional en proceso de redefinición a Institución Universitaria conforme a Ley 749 de 2002 y Decreto 2038. Órganos de gobierno: Consejo Directivo y Rectoría.",
        "updated_at": datetime.datetime.now().isoformat()
    }


def save_juridico_project(inst_id, data):
    """Guarda el proyecto y casos del asesor jurídico en Supabase."""
    table_id = f"ASESOR_JURIDICO_{inst_id}"
    data["updated_at"] = datetime.datetime.now().isoformat()
    data_json = json.dumps(data, ensure_ascii=False)
    try:
        check = supabase.table('statistics').select('id').eq('table_id', table_id).execute()
        if check.data:
            supabase.table('statistics').update({'data_json': data_json}).eq('table_id', table_id).execute()
        else:
            supabase.table('statistics').insert({
                'table_id': table_id,
                'inst_id': inst_id,
                'data_json': data_json
            }).execute()
        return True
    except Exception as e:
        print(f"[Asesor Juridico] Error save: {e}")
        return False


def extract_text_from_file_storage(file_storage):
    """Extrae texto de archivos PDF, DOCX o texto plano cargados por el usuario."""
    filename = file_storage.filename or ""
    ext = os.path.splitext(filename)[1].lower()
    text = ""
    try:
        content_bytes = file_storage.read()
        file_storage.seek(0)
        
        if ext == '.pdf':
            reader = PyPDF2.PdfReader(io.BytesIO(content_bytes))
            pages_text = []
            for idx_p, page in enumerate(reader.pages):
                pt = page.extract_text() or ""
                pages_text.append(f"--- [Página {idx_p + 1}] ---\n{pt}")
            text = "\n\n".join(pages_text)
        elif ext in ('.docx', '.doc'):
            try:
                doc = docx.Document(io.BytesIO(content_bytes))
                text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
                # También tablas
                for tbl in doc.tables:
                    for row in tbl.rows:
                        text += "\n| " + " | ".join([c.text.strip().replace('\n', ' ') for c in row.cells]) + " |"
            except Exception:
                # Fallback simple
                import docx2txt
                text = docx2txt.process(io.BytesIO(content_bytes))
        else:
            # Texto plano
            text = content_bytes.decode('utf-8', errors='ignore')
    except Exception as ex:
        text = f"[Error extrayendo texto del archivo {filename}: {ex}]"
    return text.strip()


def set_docx_cell_bg(cell, hex_color):
    """Aplica sombreado de fondo XML a una celda de tabla en python-docx."""
    try:
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
        cell._tc.get_or_add_tcPr().append(shd)
    except Exception:
        pass


def set_table_borders(table, color="CBD5E1", sz="4", val="single"):
    """Aplica bordes sutiles horizontales a una tabla en Word."""
    try:
        tblPr = table._tbl.tblPr
        borders = parse_xml(
            f'<w:tblBorders {nsdecls("w")}>'
            f'  <w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
            f'  <w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
            f'  <w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
            f'  <w:insideV w:val="none"/>'
            f'  <w:left w:val="none"/>'
            f'  <w:right w:val="none"/>'
            f'</w:tblBorders>'
        )
        tblPr.append(borders)
    except Exception:
        pass


def set_cell_margins(cell, top=100, bottom=100, left=140, right=140):
    """Configura padding interno en twips (20 twips = 1 pt)."""
    try:
        tcPr = cell._tc.get_or_add_tcPr()
        tcMar = parse_xml(
            f'<w:tcMar {nsdecls("w")}>'
            f'  <w:top w:w="{top}" w:type="dxa"/>'
            f'  <w:bottom w:w="{bottom}" w:type="dxa"/>'
            f'  <w:left w:w="{left}" w:type="dxa"/>'
            f'  <w:right w:w="{right}" w:type="dxa"/>'
            f'</w:tcMar>'
        )
        tcPr.append(tcMar)
    except Exception:
        pass


def add_footer_page_number(run):
    """Inserta el campo nativo PAGE de Word en un run."""
    try:
        fld1 = parse_xml(r'<w:fldChar %s w:fldCharType="begin"/>' % nsdecls('w'))
        instr = parse_xml(r'<w:instrText %s xml:space="preserve"> PAGE </w:instrText>' % nsdecls('w'))
        fld2 = parse_xml(r'<w:fldChar %s w:fldCharType="separate"/>' % nsdecls('w'))
        fld3 = parse_xml(r'<w:fldChar %s w:fldCharType="end"/>' % nsdecls('w'))
        run._r.extend([fld1, instr, fld2, fld3])
    except Exception:
        pass


def add_formatted_runs_to_paragraph(paragraph, text, base_font_size=Pt(10), base_color=RGBColor(51, 65, 85), italic_all=False):
    """Divide texto con **negrita** y *cursiva* y lo agrega con formato editorial profesional."""
    import re
    tokens = re.split(r'(\*\*.*?\*\*|\*.*?\*|_.*?_)', text)
    for tok in tokens:
        if not tok:
            continue
        if tok.startswith('**') and tok.endswith('**') and len(tok) >= 4:
            r = paragraph.add_run(tok[2:-2])
            r.bold = True
            r.font.name = 'Calibri'
            r.font.size = base_font_size
            r.font.color.rgb = RGBColor(15, 23, 42)
            if italic_all:
                r.italic = True
        elif ((tok.startswith('*') and tok.endswith('*')) or (tok.startswith('_') and tok.endswith('_'))) and len(tok) >= 2:
            r = paragraph.add_run(tok[1:-1])
            r.italic = True
            r.font.name = 'Calibri'
            r.font.size = base_font_size
            r.font.color.rgb = base_color
        else:
            r = paragraph.add_run(tok)
            r.font.name = 'Calibri'
            r.font.size = base_font_size
            r.font.color.rgb = base_color
            if italic_all:
                r.italic = True


def clean_latin_pdf(text):
    """Limpia caracteres especiales y comillas curvas para FPDF con fuente core latin-1."""
    if not text:
        return ""
    t = str(text)
    replacements = {
        '“': '"', '”': '"', '‘': "'", '’': "'",
        '–': '-', '—': '-', '…': '...', '•': '*',
        'á': 'á', 'é': 'é', 'í': 'í', 'ó': 'ó', 'ú': 'ú',
        'Á': 'Á', 'É': 'É', 'Í': 'Í', 'Ó': 'Ó', 'Ú': 'Ú',
        'ñ': 'ñ', 'Ñ': 'Ñ', 'ü': 'ü', 'Ü': 'Ü'
    }
    for k, v in replacements.items():
        t = t.replace(k, v)
    try:
        return t.encode('latin-1', 'replace').decode('latin-1')
    except Exception:
        return t.encode('ascii', 'replace').decode('ascii')


def parse_markdown_blocks(md_text):
    """Parsea texto Markdown en bloques estructurados: encabezados, tablas, viñetas, listas y párrafos."""
    if not md_text:
        return []
    import re
    lines = md_text.split('\n')
    blocks = []
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        line_str = line.strip()
        if not line_str:
            i += 1
            continue
        
        # Tabla Markdown (| Col1 | Col2 | ...)
        if line_str.startswith('|') and '|' in line_str[1:]:
            tbl_lines = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                tbl_lines.append(lines[i].strip())
                i += 1
            rows = []
            for tl in tbl_lines:
                cleaned = re.sub(r'[\s\-:|]', '', tl)
                if not cleaned:
                    continue  # Separador (| --- | --- |)
                cells = [c.strip() for c in tl.strip().strip('|').split('|')]
                rows.append(cells)
            if rows:
                blocks.append({'type': 'table', 'headers': rows[0], 'rows': rows[1:]})
            continue

        if line_str.startswith('# '):
            blocks.append({'type': 'h1', 'text': line_str[2:].strip()})
        elif line_str.startswith('## '):
            blocks.append({'type': 'h2', 'text': line_str[3:].strip()})
        elif line_str.startswith('### '):
            blocks.append({'type': 'h3', 'text': line_str[4:].strip()})
        elif line_str.startswith('#### '):
            blocks.append({'type': 'h4', 'text': line_str[5:].strip()})
        elif line_str.startswith('- ') or line_str.startswith('* '):
            blocks.append({'type': 'bullet', 'text': line_str[2:].strip()})
        elif re.match(r'^\d+\.\s+', line_str):
            m = re.match(r'^(\d+)\.\s+(.*)$', line_str)
            blocks.append({'type': 'numbered', 'num': m.group(1), 'text': m.group(2).strip()})
        elif line_str.startswith('>'):
            blocks.append({'type': 'quote', 'text': line_str[1:].strip()})
        elif line_str in ['---', '***', '___']:
            blocks.append({'type': 'hr'})
        else:
            blocks.append({'type': 'p', 'text': line_str})
        i += 1
    return blocks


def run_juridico_ai_complete(messages, inst_id, max_tokens=16384, max_loops=3):
    """Ejecuta la llamada a la IA con amplio límite de tokens y detecta si el texto quedó cortado para continuarlo automáticamente hasta completitud total."""
    full_text = call_ai(messages, max_tokens=max_tokens, temperature=0.3, inst_id=inst_id)
    if not full_text:
        return ""
    
    for _ in range(max_loops):
        trimmed = full_text.rstrip()
        if not trimmed:
            break
        last_char = trimmed[-1]
        
        palabras_cortadas = [
            ' de', ' y', ' la', ' el', ' los', ' las', ' en', ' con', ' por', ' para',
            ' que', ' del', ' al', ' según', ' conforme', ' mediante', ' dicho', ' dicha',
            ' artículo', ' parágrafo', ' numeral', ' literal', ' inciso', ' acuerdo',
            ' decreto', ' institución', ' universitaria', ' consejo', ' ministerio', ' conaces'
        ]
        parece_incompleto = False
        
        if last_char not in ('.', '!', '?', ';', ':', '}', ']', ')') and not trimmed.endswith('**.'):
            parece_incompleto = True
        elif any(trimmed.lower().endswith(p) for p in palabras_cortadas):
            parece_incompleto = True
        elif trimmed.splitlines()[-1].strip().startswith(('ARTÍCULO', 'CAPÍTULO', 'PARÁGRAFO', 'CONSIDERANDO', 'NUMERAL', 'LITERAL')) and len(trimmed.splitlines()[-1].strip()) < 150 and not trimmed.endswith('.'):
            parece_incompleto = True
        elif ('ARTÍCULO' in trimmed or 'ESTATUTO' in trimmed.upper()) and not any(term in trimmed.upper() for term in ['VIGENCIA', 'DEROGATORIA', 'TRANSITORIO', 'TRANSITORIA', 'COMUNÍQUESE', 'PUBLÍQUESE', 'CÚMPLASE', 'FIRMAS', 'DISPOSICIONES FINALES', 'DISPOSICIONES GENERALES Y FINALES']):
            # Si contiene articulado estatutario pero no ha llegado al cierre formal de vigencia/derogatorias
            parece_incompleto = True
        
        if not parece_incompleto:
            break
        
        last_lines = "\n".join(trimmed.splitlines()[-3:])[-300:]
        continuation_msg = {
            "role": "user",
            "content": (
                f"El texto del dictamen / estatuto se detuvo antes de su finalización total. Quedó exactamente en:\n"
                f"\"{last_lines}\"\n\n"
                "Por favor continúa INMEDIATAMENTE a partir de ese punto exacto, sin repetir lo anterior, desarrollando con total libertad de extensión la totalidad de los artículos faltantes, parágrafos, numerales, capítulos restantes, disposiciones transitorias, vigencia, derogatorias y firmas hasta concluir el 100% del documento oficial."
            )
        }
        next_messages = list(messages) + [
            {"role": "assistant", "content": full_text},
            continuation_msg
        ]
        try:
            cont_text = call_ai(next_messages, max_tokens=max_tokens, temperature=0.3, inst_id=inst_id)
            if cont_text and len(cont_text.strip()) > 30:
                full_text = full_text.rstrip() + " " + cont_text.lstrip()
            else:
                break
        except Exception as e:
            print(f"[Juridico Auto-Continuation Warning] {e}")
            break
            
    return full_text


# ==============================================================================
# RUTAS FRONTEND Y API
# ==============================================================================
@asesor_juridico_bp.route('/asesor_juridico', methods=['GET'])
@asesor_juridico_bp.route('/asesor_juridico.html', methods=['GET'])
def asesor_juridico_view():
    """Renderiza la vista principal del módulo Asesor Jurídico SKEL."""
    inst_id = get_active_inst_id()
    project = get_juridico_project(inst_id)
    return render_template('asesor_juridico.html', project=project, normagrama=NORMAGRAMA_BASE)


@asesor_juridico_bp.route('/api/asesor_juridico/data', methods=['GET'])
def api_asesor_juridico_data():
    """Retorna los datos de casos e historial del Asesor Jurídico."""
    inst_id = request.args.get('inst_id', get_active_inst_id(), type=int)
    project = get_juridico_project(inst_id)
    return jsonify({
        "status": "success",
        "project": project,
        "normagrama_base": NORMAGRAMA_BASE
    })


@asesor_juridico_bp.route('/api/asesor_juridico/analyze', methods=['POST'])
def api_asesor_juridico_analyze():
    """Procesa el caso legal, extrae el texto de las evidencias adjuntas y genera el concepto vinculante."""
    try:
        inst_id = request.form.get('inst_id', get_active_inst_id(), type=int)
        titulo = request.form.get('titulo', 'Consulta Jurídica Especializada').strip()
        asunto_tipo = request.form.get('asunto_tipo', 'Cambio de Carácter y Redefinición').strip()
        pregunta_caso = request.form.get('pregunta_caso', '').strip()
        normas_seleccionadas = request.form.get('normas_seleccionadas', '')
        estatuto_contexto = request.form.get('estatuto_contexto', '').strip()
        caso_id = request.form.get('caso_id', '').strip()

        if not pregunta_caso:
            return jsonify({"status": "error", "message": "Debe formular el problema jurídico o consulta a analizar."}), 400

        # Procesar múltiples archivos adjuntos
        archivos_data = []
        archivos_texto_combinado = []
        uploaded_files = request.files.getlist('evidencias_files')

        for f in uploaded_files:
            if f and f.filename:
                fn = f.filename
                text_extracted = extract_text_from_file_storage(f)
                size_kb = len(text_extracted.encode('utf-8')) // 1024
                archivos_data.append({
                    "id": str(uuid.uuid4()),
                    "nombre": fn,
                    "tamano_kb": size_kb,
                    "fecha_subida": datetime.datetime.now().isoformat()
                })
                # Truncar razonablemente si es extremadamente largo para no desbordar el contexto
                snippet = text_extracted[:25000] if len(text_extracted) > 25000 else text_extracted
                archivos_data[-1]["texto_extraido"] = snippet
                archivos_texto_combinado.append(f"=== EVIDENCIA NUEVA: {fn} ===\n{snippet}\n")

        # Caso existente: recuperar evidencias previas y dictamen anterior para reestructurar
        instrucciones_reestructura = request.form.get('instrucciones_reestructura', '').strip()
        project_prev = get_juridico_project(inst_id)
        caso_prev = next((c for c in project_prev.get("casos", []) if c.get("id") == caso_id), None) if caso_id else None
        dictamen_previo = ""
        if caso_prev:
            for a_prev in caso_prev.get("archivos", []):
                if a_prev.get("texto_extraido"):
                    archivos_texto_combinado.insert(0, f"=== EVIDENCIA PREVIA DEL EXPEDIENTE: {a_prev.get('nombre')} ===\n{a_prev['texto_extraido'][:15000]}\n")
            dictamen_previo = caso_prev.get("dictamen", "")

        evidencias_prompt = "\n".join(archivos_texto_combinado) if archivos_texto_combinado else "No se adjuntaron documentos adicionales. El análisis se realiza con base en el marco normativo y los hechos descritos."

        # Construir el Prompt del Posdoctor en Derecho Educativo y Administrativo
        system_prompt = f"""Eres el ASESOR JURÍDICO SENIOR Y POSDOCTOR EN DERECHO EDUCATIVO Y ADMINISTRATIVO de SKEL 360.
Posees el más alto nivel de peritaje en Colombia:
- Posdoctor en Leyes Educativas y Derecho Administrativo.
- Ex-Secretario de Sala CONACES (Comisión Nacional Intersectorial de Aseguramiento de la Calidad).
- Ex-Asesor Jurídico del Despacho del Ministerio de Educación Nacional (MEN).
- Ex-Miembro Directivo del Consejo Nacional de Acreditación (CNA).
- Experto en inspección, vigilancia y control de la educación superior en Colombia.

TU MARCO NORMATIVO RIGUROSO Y VIGENTE INCLUYE:
1. Ley 30 de 1992 (Educación Superior, autonomía universitaria en Art. 28 y 29, órganos de dirección, régimen de contratación y personal).
2. Ley 749 de 2002 (Ciclos propedéuticos y redefinición institucional / cambio de carácter).
3. Decreto 2038 de 2024 / 2023 (Reglamenta el trámite y evaluación del cambio de carácter ante MEN y CONACES).
4. Decreto Único Reglamentario 1075 de 2015 (Sector Educación - Título 5 Educación Superior).
5. Decreto 1330 de 2019 (Condiciones institucionales y de programa para Registro Calificado).
6. Decreto 0529 de 2024 (Modificación y agilización de trámites de calidad y registro calificado ante el MEN).
7. Acuerdo 01 de 2025 del CESU (Nuevo modelo de Acreditación en Alta Calidad).
8. Ley 115 de 1994 (Ley General de Educación).
9. Ley 1437 de 2011 (CPACA - Vía gubernativa, recursos de reposición ante el MEN, términos y actos administrativos).
10. Régimen de Función Pública para Instituciones Oficiales y Adscritas al MEN (Ley 489 de 1998, Ley 909 de 2004, Decreto 1083 de 2015, límites y armonización con la autonomía universitaria).
11. Jurisprudencia Constitucional: Sentencias C-220/1997, C-008/2001, C-1435/2000, C-534/1997 (Alcance inviolable de la autonomía universitaria frente a intromisiones indebidas del Ejecutivo).

TUS REGLAS INQUEBRANTABLES DE RESPUESTA:
1. RIGOR Y CONTUNDENCIA JURÍDICA: Habla y redacta como un jurista del más alto rango del Estado colombiano. Cita siempre artículos, numerales, parágrafos e incisos precisos y reales.
2. BARRIDO NORMATIVO EXPRESO:
   - Identifica con claridad las normas vigentes.
   - Si la consulta o los documentos adjuntos citan normas derogadas o modificadas (ej: decretos anteriores derogados por el 1075, disposiciones superadas por el Decreto 0529 de 2024 o acuerdos CESU antiguos), DEBES DESVIRTUARLAS EXPRESAMENTE y señalar la norma vigente que las sustituyó.
3. DEFENSA Y PROTECCIÓN DE LA AUTONOMÍA INSTITUCIONAL:
   - Jamás desconozcas la autonomía de la institución educativa para definir sus propios estatutos, reglamentos docentes y estudiantiles, órganos de gobierno y políticas internas.
   - Si se trata de INTENALCO EDUCACIÓN SUPERIOR u otra IES oficial, defiende su competencia privativa para autorregularse mediante Acuerdos de su Consejo Directivo.
4. ANÁLISIS INTEGRAL DE LAS EVIDENCIAS ADJUNTAS:
   - Analiza con minucia el texto de los documentos adjuntos que te suministra el usuario, contrastándolos con los requisitos de ley.
5. ESTRUCTURA FORMAL OBLIGATORIA DEL DICTAMEN:
   - # CONCEPTO JURÍDICO VINCULANTE Y DICTAMEN TÉCNICO
   - ## 1. IDENTIFICACIÓN DEL CASO Y PROBLEMA JURÍDICO
   - ## 2. ANÁLISIS PROBATORIO DE LAS EVIDENCIAS Y DOCUMENTOS ADJUNTOS
   - ## 3. BARRIDO NORMATIVO: NORMAS VIGENTES VS. NORMAS DEROGADAS / MODIFICADAS
   - ## 4. MARCO JURISPRUDENCIAL Y ALCANCE DE LA AUTONOMÍA INSTITUCIONAL
   - ## 5. TESIS Y DICTAMEN DE FONDO
   - ## 6. PROPUESTA TEXTUAL DE ARTICULADO / MINUTA / MEMORIAL DE RESPUESTA OFICIAL (Texto listo para ser adoptado por Consejo Directivo o presentado al MEN)
6. LIBERTAD PLENA DE EXTENSIÓN, DESARROLLO INTEGRAL Y COMPLETITUD AL 100%:
   - Tienes total libertad para utilizar las líneas, párrafos y páginas que sean necesarias para desarrollar la respuesta de manera exhaustiva y sin restricciones de espacio.
   - Si la consulta solicita la redacción o reforma de estatutos o reglamentos (ej. Estatuto General para el cambio de carácter de INTENALCO a Institución Universitaria bajo Ley 749 de 2002 y Decreto 2038), DEBES REDACTAR EL ESTATUTO COMPLETO ARTÍCULO POR ARTÍCULO (desde el Artículo 1º, Capítulos I al final: Naturaleza, Gobierno Institucional, Órganos Colegiados, Rectoría, Patrimonio, Régimen Docente, Estudiantil, Disciplinario, hasta las Disposiciones Finales, Transitorias, Derogatorias y Vigencia).
   - ESTÁ COMPLETAMENTE PROHIBIDO cortar la respuesta, dejar artículos inconclusos, usar fórmulas evasivas como "(continúan los demás artículos...)" o resumir con puntos suspensivos. Se exige el articulado íntegro y detallado al 100%.

RESPONDE EXCLUSIVAMENTE EN ESPAÑOL, EN FORMATO MARKDOWN FORMAL Y CONTEXTUALIZADO."""

        user_prompt = f"""ASUNTO / CONSULTA:
Título: {titulo}
Tipo de Trámite: {asunto_tipo}
Normas señaladas como prioritarias: {normas_seleccionadas or 'Todas las aplicables'}

CONTEXTO INSTITUCIONAL / ESTATUTARIO PROPIO:
{estatuto_contexto or 'Institución de Educación Superior INTENALCO (oficial/adscrita), en proceso de cambio de carácter y actualización estatutaria bajo la Ley 749 de 2002 y Decreto 2038.'}

PROBLEMA JURÍDICO PLANTEADO POR LA INSTITUCIÓN:
{pregunta_caso}

EVIDENCIAS Y DOCUMENTOS APORTADOS AL CASO:
{evidencias_prompt}

Emita el Concepto Jurídico Vinculante formal, exhaustivo y contundente, con barrido normativo riguroso, desvirtuación de normas derogadas y propuesta articulada aplicable.
IMPORTANTE: Desarrolla la respuesta y el articulado en su TOTALIDAD y COMPLETITUD (100%), agotando cada artículo hasta las disposiciones finales y de vigencia, sin omitir ningún capítulo ni suspender la redacción."""

        if dictamen_previo:
            user_prompt += f"""

DICTAMEN PREVIO EMITIDO EN ESTE EXPEDIENTE (versión anterior a reestructurar):
{dictamen_previo[:20000]}

INSTRUCCIONES DE REESTRUCTURACIÓN DE LA INSTITUCIÓN:
{instrucciones_reestructura or 'Integrar las nuevas evidencias aportadas, corregir y profundizar el análisis.'}

Reestructure y emita una NUEVA VERSIÓN completa del dictamen, integrando las evidencias nuevas y previas, conservando lo que siga siendo jurídicamente válido y ajustando lo que corresponda. Indique al inicio una breve nota de los cambios frente a la versión anterior. Desarrolle el documento con total completitud al 100%."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        # Llamada a IA con soporte de auto-continuación y amplio límite de tokens
        response_text = run_juridico_ai_complete(messages, inst_id=inst_id, max_tokens=16384, max_loops=3)

        # Preparar registro del caso
        project = get_juridico_project(inst_id)
        now_iso = datetime.datetime.now().isoformat()
        
        if not caso_id:
            caso_id = str(uuid.uuid4())
            cod_num = len(project.get("casos", [])) + 1
            codigo_caso = f"CASO-JUR-{datetime.datetime.now().year}-{cod_num:03d}"
            nuevo_caso = {
                "id": caso_id,
                "codigo_caso": codigo_caso,
                "titulo": titulo,
                "asunto_tipo": asunto_tipo,
                "pregunta_caso": pregunta_caso,
                "normas_seleccionadas": normas_seleccionadas,
                "estatuto_contexto": estatuto_contexto,
                "archivos": archivos_data,
                "dictamen": response_text,
                "fecha_creacion": now_iso,
                "fecha_actualizacion": now_iso,
                "estado": "Emitido",
                "autor_concepto": "Asesor Jurídico Senior SKEL 360 (Posdoctor en Derecho Educativo)"
            }
            project["casos"].insert(0, nuevo_caso)
        else:
            # Actualizar caso existente
            target = next((c for c in project.get("casos", []) if c.get("id") == caso_id), None)
            if target:
                target["titulo"] = titulo
                target["asunto_tipo"] = asunto_tipo
                target["pregunta_caso"] = pregunta_caso
                target["normas_seleccionadas"] = normas_seleccionadas
                target["estatuto_contexto"] = estatuto_contexto
                if archivos_data:
                    target["archivos"] = target.get("archivos", []) + archivos_data
                hist = target.setdefault("versiones", [])
                if target.get("dictamen"):
                    hist.insert(0, {
                        "version": target.get("version", 1),
                        "fecha": target.get("fecha_actualizacion", now_iso),
                        "dictamen": target.get("dictamen", "")
                    })
                target["versiones"] = hist[:10]
                target["version"] = int(target.get("version", 1)) + 1
                target["instrucciones_reestructura"] = instrucciones_reestructura
                target["dictamen"] = response_text
                target["estado"] = "Reestructurado"
                target["fecha_actualizacion"] = now_iso
                codigo_caso = target.get("codigo_caso", "CASO-JUR")
            else:
                codigo_caso = f"CASO-JUR-{datetime.datetime.now().year}-001"

        save_juridico_project(inst_id, project)

        return jsonify({
            "status": "success",
            "caso_id": caso_id,
            "codigo_caso": codigo_caso,
            "dictamen": response_text,
            "archivos_procesados": len(archivos_data),
            "caso": next((c for c in project.get("casos", []) if c.get("id") == caso_id), None)
        })

    except Exception as e:
        print(f"[Asesor Jurídico Error] {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@asesor_juridico_bp.route('/api/asesor_juridico/save_case', methods=['POST'])
def api_asesor_juridico_save_case():
    """Guarda el caso (borrador o edición manual del dictamen) sin invocar el análisis, admitiendo nuevos adjuntos."""
    try:
        inst_id = request.form.get('inst_id', get_active_inst_id(), type=int)
        caso_id = request.form.get('caso_id', '').strip()
        project = get_juridico_project(inst_id)
        now_iso = datetime.datetime.now().isoformat()

        nuevos = []
        for f in request.files.getlist('evidencias_files'):
            if f and f.filename:
                txt = extract_text_from_file_storage(f)
                nuevos.append({
                    "id": str(uuid.uuid4()),
                    "nombre": f.filename,
                    "tamano_kb": len(txt.encode('utf-8')) // 1024,
                    "fecha_subida": now_iso,
                    "texto_extraido": txt[:25000]
                })

        campos = {
            "titulo": request.form.get('titulo', '').strip() or 'Caso Jurídico (Borrador)',
            "asunto_tipo": request.form.get('asunto_tipo', '').strip(),
            "pregunta_caso": request.form.get('pregunta_caso', '').strip(),
            "normas_seleccionadas": request.form.get('normas_seleccionadas', ''),
            "estatuto_contexto": request.form.get('estatuto_contexto', '').strip(),
        }
        dictamen_editado = request.form.get('dictamen', None)

        target = next((c for c in project.get("casos", []) if c.get("id") == caso_id), None) if caso_id else None
        if target:
            target.update(campos)
            target["archivos"] = target.get("archivos", []) + nuevos
            if dictamen_editado is not None and dictamen_editado != target.get("dictamen", ""):
                hist = target.setdefault("versiones", [])
                if target.get("dictamen"):
                    hist.insert(0, {"version": target.get("version", 1), "fecha": target.get("fecha_actualizacion", now_iso), "dictamen": target["dictamen"]})
                target["versiones"] = hist[:10]
                target["version"] = int(target.get("version", 1)) + 1
                target["dictamen"] = dictamen_editado
                target["estado"] = "Editado manualmente"
            target["fecha_actualizacion"] = now_iso
        else:
            caso_id = str(uuid.uuid4())
            cod_num = len(project.get("casos", [])) + 1
            target = {
                "id": caso_id,
                "codigo_caso": f"CASO-JUR-{datetime.datetime.now().year}-{cod_num:03d}",
                **campos,
                "archivos": nuevos,
                "dictamen": dictamen_editado or "",
                "version": 1,
                "versiones": [],
                "fecha_creacion": now_iso,
                "fecha_actualizacion": now_iso,
                "estado": "Borrador"
            }
            project.setdefault("casos", []).insert(0, target)

        save_juridico_project(inst_id, project)
        return jsonify({"status": "success", "caso_id": caso_id, "codigo_caso": target["codigo_caso"], "caso": target})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@asesor_juridico_bp.route('/api/asesor_juridico/remove_file', methods=['POST'])
def api_asesor_juridico_remove_file():
    """Retira una evidencia del expediente del caso."""
    try:
        inst_id = request.form.get('inst_id', get_active_inst_id(), type=int)
        caso_id = request.form.get('caso_id', '').strip()
        file_id = request.form.get('file_id', '').strip()
        project = get_juridico_project(inst_id)
        target = next((c for c in project.get("casos", []) if c.get("id") == caso_id), None)
        if not target:
            return jsonify({"status": "error", "message": "Caso no encontrado."}), 404
        target["archivos"] = [a for a in target.get("archivos", []) if a.get("id") != file_id]
        save_juridico_project(inst_id, project)
        return jsonify({"status": "success", "caso": target})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@asesor_juridico_bp.route('/api/asesor_juridico/delete_case', methods=['POST'])
def api_asesor_juridico_delete_case():
    """Elimina un caso del expediente jurídico."""
    try:
        inst_id = request.form.get('inst_id', get_active_inst_id(), type=int)
        caso_id = request.form.get('caso_id', '').strip()
        project = get_juridico_project(inst_id)
        project["casos"] = [c for c in project.get("casos", []) if c.get("id") != caso_id]
        save_juridico_project(inst_id, project)
        return jsonify({"status": "success", "message": "Caso eliminado del expediente."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@asesor_juridico_bp.route('/api/asesor_juridico/export_word', methods=['POST'])
def api_asesor_juridico_export_word():
    """Exporta el concepto jurídico formal maquetado a Word (.docx) listo para impresión directa."""
    try:
        import re
        inst_id = request.form.get('inst_id', get_active_inst_id(), type=int)
        caso_id = request.form.get('caso_id', '')
        titulo = request.form.get('titulo', 'Concepto Jurídico Especializado')
        dictamen = request.form.get('dictamen', '')
        asunto_tipo = request.form.get('asunto_tipo', 'Concepto Jurídico')
        codigo_caso = request.form.get('codigo_caso', 'CASO-JUR')

        doc = docx.Document()
        
        # 1. Configuración de Página (Letter estándar, márgenes exactos de 1 pulgada / 2.54 cm)
        for section in doc.sections:
            section.page_width = Inches(8.5)
            section.page_height = Inches(11.0)
            section.top_margin = Inches(1.0)
            section.bottom_margin = Inches(1.0)
            section.left_margin = Inches(1.0)
            section.right_margin = Inches(1.0)
            section.different_first_page_header_footer = False
            
            # --- ENCABEZADO OFICIAL NATIVO ---
            header = section.header
            header_p = header.paragraphs[0]
            header_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            header_p.paragraph_format.space_after = Pt(2)
            
            hdr_tbl = header.add_table(rows=1, cols=2, width=Inches(6.5))
            hdr_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
            
            # Celda izquierda del header
            c_left = hdr_tbl.cell(0, 0)
            p_hl = c_left.paragraphs[0]
            p_hl.alignment = WD_ALIGN_PARAGRAPH.LEFT
            r_hl1 = p_hl.add_run("INTENALCO EDUCACIÓN SUPERIOR\n")
            r_hl1.font.name = 'Calibri'
            r_hl1.font.size = Pt(8.5)
            r_hl1.font.bold = True
            r_hl1.font.color.rgb = RGBColor(30, 58, 138)
            
            r_hl2 = p_hl.add_run("SKEL 360 · DIRECCIÓN JURÍDICA Y REGULATORIA")
            r_hl2.font.name = 'Calibri'
            r_hl2.font.size = Pt(7.5)
            r_hl2.font.color.rgb = RGBColor(100, 116, 139)
            
            # Celda derecha del header
            c_right = hdr_tbl.cell(0, 1)
            p_hr = c_right.paragraphs[0]
            p_hr.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            r_hr1 = p_hr.add_run(f"Radicado: {codigo_caso}\n")
            r_hr1.font.name = 'Calibri'
            r_hr1.font.size = Pt(8.5)
            r_hr1.font.bold = True
            r_hr1.font.color.rgb = RGBColor(30, 41, 59)
            
            r_hr2 = p_hr.add_run(f"Expedición: {datetime.datetime.now().strftime('%d/%m/%Y')}")
            r_hr2.font.name = 'Calibri'
            r_hr2.font.size = Pt(7.5)
            r_hr2.font.color.rgb = RGBColor(100, 116, 139)
            
            # --- PIE DE PÁGINA OFICIAL NATIVO ---
            footer = section.footer
            ftr_tbl = footer.add_table(rows=1, cols=2, width=Inches(6.5))
            ftr_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
            
            c_fl = ftr_tbl.cell(0, 0)
            p_fl = c_fl.paragraphs[0]
            p_fl.alignment = WD_ALIGN_PARAGRAPH.LEFT
            r_fl = p_fl.add_run("Concepto Técnico-Legal Vinculante · Ley 30/1992 · Ley 749/2002 · Dec. 2038/2024")
            r_fl.font.name = 'Calibri'
            r_fl.font.size = Pt(7.5)
            r_fl.font.italic = True
            r_fl.font.color.rgb = RGBColor(148, 163, 184)
            
            c_fr = ftr_tbl.cell(0, 1)
            p_fr = c_fr.paragraphs[0]
            p_fr.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            r_fr = p_fr.add_run("Página ")
            r_fr.font.name = 'Calibri'
            r_fr.font.size = Pt(8.0)
            r_fr.font.color.rgb = RGBColor(30, 58, 138)
            add_footer_page_number(r_fr)
            r_fr2 = p_fr.add_run(" · Imprimible Oficial")
            r_fr2.font.name = 'Calibri'
            r_fr2.font.size = Pt(8.0)
            r_fr2.font.color.rgb = RGBColor(100, 116, 139)

        # 2. Carátula Institucional en el Cuerpo
        p_inst = doc.add_paragraph()
        p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_inst.paragraph_format.space_before = Pt(4)
        p_inst.paragraph_format.space_after = Pt(2)
        r_inst = p_inst.add_run("INTENALCO EDUCACIÓN SUPERIOR\n")
        r_inst.font.name = 'Calibri'
        r_inst.font.size = Pt(11)
        r_inst.font.bold = True
        r_inst.font.color.rgb = RGBColor(71, 85, 105)
        
        r_subinst = p_inst.add_run("ESTABLECIMIENTO PÚBLICO DE EDUCACIÓN SUPERIOR DEL ORDEN NACIONAL\nCONSEJO DIRECTIVO Y DIRECCIÓN JURÍDICA REGULATORIA")
        r_subinst.font.name = 'Calibri'
        r_subinst.font.size = Pt(8.5)
        r_subinst.font.color.rgb = RGBColor(100, 116, 139)
        
        # Línea divisoria decorativa
        p_div = doc.add_paragraph()
        p_div.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_div.paragraph_format.space_after = Pt(12)
        r_div = p_div.add_run("―" * 48)
        r_div.font.color.rgb = RGBColor(203, 213, 225)
        r_div.font.size = Pt(9)

        # Gran Título
        p_title = doc.add_paragraph()
        p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_title.paragraph_format.space_after = Pt(4)
        r_t1 = p_title.add_run("DICTAMEN JURÍDICO VINCULANTE\n")
        r_t1.font.name = 'Calibri'
        r_t1.font.size = Pt(15)
        r_t1.font.bold = True
        r_t1.font.color.rgb = RGBColor(30, 58, 138)
        
        r_t2 = p_title.add_run(titulo.upper())
        r_t2.font.name = 'Calibri'
        r_t2.font.size = Pt(11.5)
        r_t2.font.bold = True
        r_t2.font.color.rgb = RGBColor(49, 46, 129)

        # 3. Ficha Técnica de Radicación (Tabla estilizada)
        meta_table = doc.add_table(rows=2, cols=3)
        meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        set_table_borders(meta_table, color="CBD5E1", sz="6")
        
        meta_cols = [
            ("Nº RADICADO OFICIAL", codigo_caso),
            ("FECHA DE EXPEDICIÓN", datetime.datetime.now().strftime("%d/%m/%Y")),
            ("TIPO DE PROCESO", asunto_tipo)
        ]
        meta_cols_sub = [
            ("AUTORIDAD EMISORA", "Posdoctor en Derecho Educativo"),
            ("DESPACHO / INSTANCIA", "Dirección JurÍdica SKEL 360"),
            ("EFICACIA JURÍDICA", "Concepto Vinculante y Blindaje IES")
        ]
        
        for i, (k, v) in enumerate(meta_cols):
            cell = meta_table.cell(0, i)
            set_docx_cell_bg(cell, "1E3A8A")
            set_cell_margins(cell, top=100, bottom=100, left=140, right=140)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            rk = p.add_run(k + "\n")
            rk.font.name = 'Calibri'
            rk.font.size = Pt(7.5)
            rk.font.bold = True
            rk.font.color.rgb = RGBColor(224, 231, 255)
            rv = p.add_run(v)
            rv.font.name = 'Calibri'
            rv.font.size = Pt(9.0)
            rv.font.bold = True
            rv.font.color.rgb = RGBColor(255, 255, 255)

        for i, (k, v) in enumerate(meta_cols_sub):
            cell = meta_table.cell(1, i)
            set_docx_cell_bg(cell, "F8FAFC")
            set_cell_margins(cell, top=80, bottom=80, left=140, right=140)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            rk = p.add_run(k + "\n")
            rk.font.name = 'Calibri'
            rk.font.size = Pt(7.0)
            rk.font.bold = True
            rk.font.color.rgb = RGBColor(100, 116, 139)
            rv = p.add_run(v)
            rv.font.name = 'Calibri'
            rv.font.size = Pt(8.0)
            rv.font.color.rgb = RGBColor(30, 41, 59)

        doc.add_paragraph().paragraph_format.space_after = Pt(14)

        # 4. Parseo de Bloques Markdown Estructurados
        blocks = parse_markdown_blocks(dictamen)
        for b in blocks:
            b_type = b.get('type')
            if b_type == 'h1':
                p = doc.add_paragraph()
                p.paragraph_format.space_before = Pt(16)
                p.paragraph_format.space_after = Pt(6)
                p.paragraph_format.keep_with_next = True
                r = p.add_run(b.get('text', '').upper())
                r.font.name = 'Calibri'
                r.font.size = Pt(13)
                r.font.bold = True
                r.font.color.rgb = RGBColor(30, 58, 138)
            elif b_type == 'h2':
                p = doc.add_paragraph()
                p.paragraph_format.space_before = Pt(12)
                p.paragraph_format.space_after = Pt(4)
                p.paragraph_format.keep_with_next = True
                r = p.add_run(b.get('text', ''))
                r.font.name = 'Calibri'
                r.font.size = Pt(11.5)
                r.font.bold = True
                r.font.color.rgb = RGBColor(49, 46, 129)
            elif b_type == 'h3':
                p = doc.add_paragraph()
                p.paragraph_format.space_before = Pt(9)
                p.paragraph_format.space_after = Pt(3)
                p.paragraph_format.keep_with_next = True
                r = p.add_run(b.get('text', ''))
                r.font.name = 'Calibri'
                r.font.size = Pt(10.5)
                r.font.bold = True
                r.font.color.rgb = RGBColor(30, 41, 59)
            elif b_type == 'h4':
                p = doc.add_paragraph()
                p.paragraph_format.space_before = Pt(6)
                p.paragraph_format.space_after = Pt(2)
                p.paragraph_format.keep_with_next = True
                r = p.add_run(b.get('text', ''))
                r.font.name = 'Calibri'
                r.font.size = Pt(10)
                r.font.bold = True
                r.font.color.rgb = RGBColor(71, 85, 105)
            elif b_type == 'p':
                raw_text = b.get('text', '')
                p = doc.add_paragraph()
                p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                p.paragraph_format.line_spacing = 1.15
                p.paragraph_format.space_after = Pt(5)
                
                # Resaltar si empieza con ARTÍCULO, CAPÍTULO, PARÁGRAFO
                art_match = re.match(r'^(ARTÍCULO\s+[0-9º°\w\.\-]+[\.\:]?)(.*)$', raw_text, re.IGNORECASE)
                par_match = re.match(r'^(PARÁGRAFO\s+[0-9º°\w\.\-]+[\.\:]?)(.*)$', raw_text, re.IGNORECASE)
                cap_match = re.match(r'^(CAPÍTULO\s+[IVXLCDM0-9]+[\.\:]?)(.*)$', raw_text, re.IGNORECASE)
                
                if art_match:
                    prefix = art_match.group(1)
                    rest = art_match.group(2)
                    r_pre = p.add_run(prefix)
                    r_pre.font.name = 'Calibri'
                    r_pre.font.size = Pt(10)
                    r_pre.font.bold = True
                    r_pre.font.color.rgb = RGBColor(30, 58, 138)
                    add_formatted_runs_to_paragraph(p, rest, base_font_size=Pt(10))
                elif par_match:
                    prefix = par_match.group(1)
                    rest = par_match.group(2)
                    r_pre = p.add_run(prefix)
                    r_pre.font.name = 'Calibri'
                    r_pre.font.size = Pt(9.5)
                    r_pre.font.bold = True
                    r_pre.font.color.rgb = RGBColor(49, 46, 129)
                    add_formatted_runs_to_paragraph(p, rest, base_font_size=Pt(9.5))
                elif cap_match:
                    prefix = cap_match.group(1)
                    rest = cap_match.group(2)
                    p.paragraph_format.space_before = Pt(10)
                    p.paragraph_format.keep_with_next = True
                    r_pre = p.add_run(prefix + " ")
                    r_pre.font.name = 'Calibri'
                    r_pre.font.size = Pt(11)
                    r_pre.font.bold = True
                    r_pre.font.color.rgb = RGBColor(30, 58, 138)
                    add_formatted_runs_to_paragraph(p, rest, base_font_size=Pt(11))
                else:
                    add_formatted_runs_to_paragraph(p, raw_text, base_font_size=Pt(10))
            elif b_type == 'quote':
                p = doc.add_paragraph()
                p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                p.paragraph_format.left_indent = Inches(0.4)
                p.paragraph_format.right_indent = Inches(0.2)
                p.paragraph_format.line_spacing = 1.15
                p.paragraph_format.space_before = Pt(4)
                p.paragraph_format.space_after = Pt(6)
                add_formatted_runs_to_paragraph(p, b.get('text', ''), base_font_size=Pt(9.5), base_color=RGBColor(71, 85, 105), italic_all=True)
            elif b_type == 'bullet':
                p = doc.add_paragraph()
                p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                p.paragraph_format.left_indent = Inches(0.3)
                p.paragraph_format.space_after = Pt(3)
                r_bullet = p.add_run("▪  ")
                r_bullet.font.name = 'Calibri'
                r_bullet.font.size = Pt(8.5)
                r_bullet.font.bold = True
                r_bullet.font.color.rgb = RGBColor(30, 58, 138)
                add_formatted_runs_to_paragraph(p, b.get('text', ''), base_font_size=Pt(9.5))
            elif b_type == 'numbered':
                p = doc.add_paragraph()
                p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                p.paragraph_format.left_indent = Inches(0.3)
                p.paragraph_format.space_after = Pt(3)
                r_num = p.add_run(f"{b.get('num', '1')}.  ")
                r_num.font.name = 'Calibri'
                r_num.font.size = Pt(9.5)
                r_num.font.bold = True
                r_num.font.color.rgb = RGBColor(30, 58, 138)
                add_formatted_runs_to_paragraph(p, b.get('text', ''), base_font_size=Pt(9.5))
            elif b_type == 'hr':
                p = doc.add_paragraph()
                p.paragraph_format.space_before = Pt(8)
                p.paragraph_format.space_after = Pt(8)
                r_hr = p.add_run("―" * 52)
                r_hr.font.color.rgb = RGBColor(226, 232, 240)
            elif b_type == 'table':
                headers = b.get('headers', [])
                rows = b.get('rows', [])
                if headers:
                    tbl = doc.add_table(rows=len(rows) + 1, cols=len(headers))
                    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
                    set_table_borders(tbl, color="CBD5E1", sz="4")
                    
                    # Header row
                    header_tr = tbl.rows[0]._tr.get_or_add_trPr()
                    header_tr.append(parse_xml(r'<w:tblHeader %s/>' % nsdecls('w')))
                    header_tr.append(parse_xml(r'<w:cantSplit %s/>' % nsdecls('w')))
                    
                    for h_idx, h_text in enumerate(headers):
                        cell = tbl.cell(0, h_idx)
                        set_docx_cell_bg(cell, "1E3A8A")
                        set_cell_margins(cell, top=90, bottom=90, left=120, right=120)
                        p = cell.paragraphs[0]
                        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                        r = p.add_run(h_text.strip())
                        r.font.name = 'Calibri'
                        r.font.size = Pt(8.5)
                        r.font.bold = True
                        r.font.color.rgb = RGBColor(255, 255, 255)
                        
                    # Data rows
                    for r_idx, row_data in enumerate(rows):
                        row_tr = tbl.rows[r_idx + 1]._tr.get_or_add_trPr()
                        row_tr.append(parse_xml(r'<w:cantSplit %s/>' % nsdecls('w')))
                        bg_color = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
                        
                        for c_idx, c_text in enumerate(row_data):
                            if c_idx < len(headers):
                                cell = tbl.cell(r_idx + 1, c_idx)
                                set_docx_cell_bg(cell, bg_color)
                                set_cell_margins(cell, top=80, bottom=80, left=120, right=120)
                                p = cell.paragraphs[0]
                                p.paragraph_format.line_spacing = 1.1
                                p.paragraph_format.space_after = Pt(2)
                                add_formatted_runs_to_paragraph(p, c_text.strip(), base_font_size=Pt(8.5))
                                
                    doc.add_paragraph().paragraph_format.space_after = Pt(8)

        # 5. Bloque Final de Firmas para Impresión Directa
        doc.add_paragraph().paragraph_format.space_before = Pt(16)
        
        p_clausula = doc.add_paragraph()
        p_clausula.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_clausula.paragraph_format.space_after = Pt(20)
        p_clausula.paragraph_format.keep_with_next = True
        r_cl = p_clausula.add_run(
            "El presente Concepto Jurídico Vinculante se expide en derecho, con plena eficacia vinculante para la toma de decisiones institucionales, sustentado en la doctrina constitucional de la Autonomía Universitaria (Art. 69 CP, Sentencias C-220/97 y C-008/01) y en el marco normativo de la Ley 30 de 1992, la Ley 749 de 2002 y el Decreto 2038. Para constancia probatoria, se suscribe en dos (2) ejemplares de igual valor legal."
        )
        r_cl.font.name = 'Calibri'
        r_cl.font.size = Pt(8.5)
        r_cl.font.italic = True
        r_cl.font.color.rgb = RGBColor(100, 116, 139)
        
        # Tabla de Firmas
        sign_table = doc.add_table(rows=1, cols=2)
        sign_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        sign_trPr = sign_table.rows[0]._tr.get_or_add_trPr()
        sign_trPr.append(parse_xml(r'<w:cantSplit %s/>' % nsdecls('w')))
        
        # Firma 1: Perito Jurídico
        c_s1 = sign_table.cell(0, 0)
        set_cell_margins(c_s1, top=140, bottom=140, left=160, right=160)
        p_s1 = c_s1.paragraphs[0]
        p_s1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_s1_1 = p_s1.add_run("_________________________________________\n")
        r_s1_1.font.color.rgb = RGBColor(100, 116, 139)
        r_s1_2 = p_s1.add_run("POSDOCTOR EN DERECHO EDUCATIVO\n")
        r_s1_2.font.name = 'Calibri'
        r_s1_2.font.size = Pt(9.5)
        r_s1_2.font.bold = True
        r_s1_2.font.color.rgb = RGBColor(30, 58, 138)
        r_s1_3 = p_s1.add_run("Asesor Jurídico Senior Especializado\nDirección Jurídica SKEL 360\nCriterio CONACES · CNA · MEN")
        r_s1_3.font.name = 'Calibri'
        r_s1_3.font.size = Pt(8.0)
        r_s1_3.font.color.rgb = RGBColor(71, 85, 105)

        # Firma 2: Rectoría / Consejo Directivo
        c_s2 = sign_table.cell(0, 1)
        set_cell_margins(c_s2, top=140, bottom=140, left=160, right=160)
        p_s2 = c_s2.paragraphs[0]
        p_s2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_s2_1 = p_s2.add_run("_________________________________________\n")
        r_s2_1.font.color.rgb = RGBColor(100, 116, 139)
        r_s2_2 = p_s2.add_run("REPRESENTANTE LEGAL / RECTORÍA\n")
        r_s2_2.font.name = 'Calibri'
        r_s2_2.font.size = Pt(9.5)
        r_s2_2.font.bold = True
        r_s2_2.font.color.rgb = RGBColor(49, 46, 129)
        r_s2_3 = p_s2.add_run("INTENALCO EDUCACIÓN SUPERIOR\nÓrgano de Gobierno y Ejecución\nEn mérito de sus facultades legales y estatutarias")
        r_s2_3.font.name = 'Calibri'
        r_s2_3.font.size = Pt(8.0)
        r_s2_3.font.color.rgb = RGBColor(71, 85, 105)

        io_stream = io.BytesIO()
        doc.save(io_stream)
        io_stream.seek(0)
        filename = f"Concepto_Juridico_{codigo_caso}_{datetime.datetime.now().strftime('%Y%m%d')}.docx"
        return send_file(io_stream, as_attachment=True, download_name=filename, mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

    except Exception as e:
        print(f"[Asesor Jurídico Word Export Error] {e}")
        return str(e), 500


@asesor_juridico_bp.route('/api/asesor_juridico/export_pdf', methods=['POST'])
def api_asesor_juridico_export_pdf():
    """Exporta el concepto jurídico a PDF formal."""
    try:
        from fpdf import FPDF
        from fpdf.fonts import FontFace

        inst_id = request.form.get('inst_id', get_active_inst_id(), type=int)
        caso_id = request.form.get('caso_id', '')
        titulo = request.form.get('titulo', 'Concepto Jurídico Especializado')
        dictamen = request.form.get('dictamen', '')
        asunto_tipo = request.form.get('asunto_tipo', 'Concepto Jurídico')
        codigo_caso = request.form.get('codigo_caso', 'CASO-JUR')

        class JuridicoPDF(FPDF):
            def header(self):
                self.set_y(8)
                self.set_font("helvetica", "B", 9)
                self.set_text_color(30, 58, 138)
                self.cell(0, 5, "SKEL 360 - DIRECCION JURIDICA Y REGULATORIA EN EDUCACION SUPERIOR", border=0, align="C")
                self.ln(4.5)
                self.set_font("helvetica", "I", 7.5)
                self.set_text_color(100, 116, 139)
                self.cell(0, 4, "Concepto Juridico Vinculante - Posdoctorado en Derecho Educativo y Administrativo", border=0, align="C")
                self.ln(5)
                self.set_draw_color(203, 213, 225)
                self.line(15, self.get_y(), 195, self.get_y())
                self.ln(5)

            def footer(self):
                self.set_y(-12)
                self.set_draw_color(226, 232, 240)
                self.line(15, self.get_y(), 195, self.get_y())
                self.set_font("helvetica", "I", 7.5)
                self.set_text_color(148, 163, 184)
                self.cell(0, 8, f"Pagina {self.page_no()} - Dictamen Juridico Oficial SKEL 360", border=0, align="C")

        pdf = JuridicoPDF()
        pdf.set_margins(15, 20, 15)
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        # Título
        pdf.set_font("helvetica", "B", 13)
        pdf.set_text_color(30, 58, 138)
        pdf.set_x(15)
        pdf.multi_cell(180, 6, txt=clean_latin_pdf(f"DICTAMEN JURIDICO: {titulo.upper()}"), align="C")
        pdf.ln(2)

        # Ficha de Radicación
        with pdf.table(col_widths=(60, 60, 60), borders_layout="ALL", line_height=5) as t_meta:
            r0 = t_meta.row()
            r0.cell(clean_latin_pdf(f"Radicado: {codigo_caso}"), style=FontFace(family='helvetica', emphasis='BOLD', color=(30, 41, 59), fill_color=(241, 245, 249)))
            r0.cell(clean_latin_pdf(f"Fecha: {datetime.datetime.now().strftime('%d/%m/%Y')}"), style=FontFace(family='helvetica', emphasis='BOLD', color=(30, 41, 59), fill_color=(241, 245, 249)))
            r0.cell(clean_latin_pdf(f"Asunto: {asunto_tipo}"), style=FontFace(family='helvetica', emphasis='BOLD', color=(30, 41, 59), fill_color=(241, 245, 249)))

            r1 = t_meta.row()
            r1.cell(clean_latin_pdf("Perito: Posdoctor Leyes"), style=FontFace(family='helvetica', color=(71, 85, 105), fill_color=(248, 250, 252)))
            r1.cell(clean_latin_pdf("Instancia: Asesor Juridico"), style=FontFace(family='helvetica', color=(71, 85, 105), fill_color=(248, 250, 252)))
            r1.cell(clean_latin_pdf("Eficacia: Vinculante"), style=FontFace(family='helvetica', color=(71, 85, 105), fill_color=(248, 250, 252)))
        pdf.ln(5)

        # Parsear dictamen
        for raw_line in dictamen.split('\n'):
            line = raw_line.strip()
            if not line:
                pdf.ln(3)
                continue
            pdf.set_x(15)
            if line.startswith('# '):
                pdf.ln(3)
                pdf.set_font("helvetica", "B", 11.5)
                pdf.set_text_color(30, 58, 138)
                pdf.multi_cell(180, 5.5, txt=clean_latin_pdf(line[2:].replace('**', '')))
                pdf.ln(1)
            elif line.startswith('## '):
                pdf.ln(2.5)
                pdf.set_font("helvetica", "B", 10)
                pdf.set_text_color(49, 46, 129)
                pdf.multi_cell(180, 5, txt=clean_latin_pdf(line[3:].replace('**', '')))
                pdf.ln(1)
            elif line.startswith('### '):
                pdf.ln(2)
                pdf.set_font("helvetica", "B", 9)
                pdf.set_text_color(30, 41, 59)
                pdf.multi_cell(180, 4.5, txt=clean_latin_pdf(line[4:].replace('**', '')))
                pdf.ln(1)
            elif line.startswith('- ') or line.startswith('* '):
                pdf.set_font("helvetica", size=8.5)
                pdf.set_text_color(51, 65, 85)
                pdf.set_x(18)
                pdf.multi_cell(174, 4.2, txt=clean_latin_pdf("* " + line[2:].replace('**', '')))
                pdf.ln(0.8)
            else:
                pdf.set_font("helvetica", size=8.5)
                pdf.set_text_color(51, 65, 85)
                pdf.multi_cell(180, 4.5, txt=clean_latin_pdf(line.replace('**', '')))
                pdf.ln(1.2)

        pdf_bytes = pdf.output()
        if isinstance(pdf_bytes, str):
            pdf_bytes = pdf_bytes.encode('latin-1')

        io_stream = io.BytesIO(pdf_bytes)
        filename = f"Concepto_Juridico_{codigo_caso}_{datetime.datetime.now().strftime('%Y%m%d')}.pdf"
        return send_file(io_stream, as_attachment=True, download_name=filename, mimetype="application/pdf")

    except Exception as e:
        print(f"[Asesor Jurídico PDF Export Error] {e}")
        return str(e), 500
