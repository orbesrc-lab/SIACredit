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
                archivos_texto_combinado.append(f"=== EVIDENCIA ADJUNTA: {fn} ===\n{snippet}\n")

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

Emita el Concepto Jurídico Vinculante formal, exhaustivo y contundente, con barrido normativo riguroso, desvirtuación de normas derogadas y propuesta articulada aplicable."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        # Llamada a IA
        response_text = call_ai(messages, max_tokens=3500, temperature=0.3, inst_id=inst_id)

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
                target["dictamen"] = response_text
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
            "archivos_procesados": len(archivos_data)
        })

    except Exception as e:
        print(f"[Asesor Jurídico Error] {e}")
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
    """Exporta el concepto jurídico formal maquetado a Word (.docx)."""
    try:
        inst_id = request.form.get('inst_id', get_active_inst_id(), type=int)
        caso_id = request.form.get('caso_id', '')
        titulo = request.form.get('titulo', 'Concepto Jurídico Especializado')
        dictamen = request.form.get('dictamen', '')
        asunto_tipo = request.form.get('asunto_tipo', 'Concepto Jurídico')
        codigo_caso = request.form.get('codigo_caso', 'CASO-JUR')

        doc = docx.Document()
        for section in doc.sections:
            section.top_margin = Inches(1)
            section.bottom_margin = Inches(1)
            section.left_margin = Inches(1)
            section.right_margin = Inches(1)

        # Encabezado institucional
        hdr_p = doc.add_paragraph()
        hdr_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r1 = hdr_p.add_run("SKEL 360 · DIRECCIÓN JURÍDICA Y REGULATORIA\n")
        r1.font.bold = True
        r1.font.size = Pt(12)
        r1.font.color.rgb = RGBColor(30, 58, 138)  # Navy

        r2 = hdr_p.add_run("CONSULTORÍA JURÍDICA ESPECIALIZADA EN EDUCACIÓN SUPERIOR\n")
        r2.font.bold = True
        r2.font.size = Pt(9.5)
        r2.font.color.rgb = RGBColor(71, 85, 105)

        r3 = hdr_p.add_run("Régimen Ley 30 de 1992 · Ley 749 de 2002 · Decreto 2038 · Dec. 1075 / 1330 / 0529 · Acuerdo 01 CESU 2025")
        r3.font.italic = True
        r3.font.size = Pt(8.5)
        r3.font.color.rgb = RGBColor(100, 116, 139)
        hdr_p.paragraph_format.space_after = Pt(14)

        # Título
        title_p = doc.add_paragraph()
        title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        tr = title_p.add_run(f"DICTAMEN JURÍDICO VINCULANTE: {titulo.upper()}")
        tr.font.bold = True
        tr.font.size = Pt(14)
        tr.font.color.rgb = RGBColor(30, 58, 138)
        title_p.paragraph_format.space_after = Pt(8)

        # Ficha Técnica de Radicación
        meta_table = doc.add_table(rows=2, cols=3)
        meta_table.style = 'Table Grid'
        meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        cells_r0 = [
            f"Radicado: {codigo_caso}",
            f"Fecha: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}",
            f"Asunto: {asunto_tipo}"
        ]
        cells_r1 = [
            "Perito: Posdoctor en Derecho Educativo",
            "Instancia: Dirección Jurídica SKEL",
            "Eficacia: Concepto Técnico-Legal Vinculante"
        ]
        for c_idx, val in enumerate(cells_r0):
            c = meta_table.cell(0, c_idx)
            set_docx_cell_bg(c, 'F1F5F9')
            p = c.paragraphs[0]
            r = p.add_run(val)
            r.font.size = Pt(8.5)
            r.font.bold = True
            r.font.color.rgb = RGBColor(30, 41, 59)

        for c_idx, val in enumerate(cells_r1):
            c = meta_table.cell(1, c_idx)
            set_docx_cell_bg(c, 'F8FAFC')
            p = c.paragraphs[0]
            r = p.add_run(val)
            r.font.size = Pt(8.5)
            r.font.color.rgb = RGBColor(71, 85, 105)

        doc.add_paragraph().paragraph_format.space_after = Pt(12)

        # Parsear Markdown de respuesta
        for line in dictamen.split('\n'):
            line_str = line.strip()
            if not line_str:
                doc.add_paragraph()
                continue
            if line_str.startswith('# '):
                p = doc.add_paragraph()
                p.paragraph_format.space_before = Pt(14)
                p.paragraph_format.space_after = Pt(6)
                r = p.add_run(line_str[2:].replace('**', ''))
                r.font.size = Pt(13)
                r.font.bold = True
                r.font.color.rgb = RGBColor(30, 58, 138)
            elif line_str.startswith('## '):
                p = doc.add_paragraph()
                p.paragraph_format.space_before = Pt(10)
                p.paragraph_format.space_after = Pt(4)
                r = p.add_run(line_str[3:].replace('**', ''))
                r.font.size = Pt(11.5)
                r.font.bold = True
                r.font.color.rgb = RGBColor(49, 46, 129)
            elif line_str.startswith('### '):
                p = doc.add_paragraph()
                p.paragraph_format.space_before = Pt(8)
                p.paragraph_format.space_after = Pt(3)
                r = p.add_run(line_str[4:].replace('**', ''))
                r.font.size = Pt(10.5)
                r.font.bold = True
                r.font.color.rgb = RGBColor(30, 41, 59)
            elif line_str.startswith('- ') or line_str.startswith('* '):
                p = doc.add_paragraph(style='List Bullet')
                p.paragraph_format.space_after = Pt(3)
                parts = line_str[2:].split('**')
                for i, part in enumerate(parts):
                    if not part: continue
                    r = p.add_run(part)
                    r.font.size = Pt(10)
                    if i % 2 == 1:
                        r.font.bold = True
            elif line_str.startswith('|') and '|' in line_str[1:]:
                # Fila de tabla
                p = doc.add_paragraph()
                p.paragraph_format.space_after = Pt(2)
                r = p.add_run(line_str)
                r.font.name = 'Consolas'
                r.font.size = Pt(8.5)
            else:
                p = doc.add_paragraph()
                p.paragraph_format.line_spacing = 1.15
                p.paragraph_format.space_after = Pt(6)
                parts = line_str.split('**')
                for i, part in enumerate(parts):
                    if not part: continue
                    r = p.add_run(part)
                    r.font.size = Pt(10)
                    if i % 2 == 1:
                        r.font.bold = True

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
