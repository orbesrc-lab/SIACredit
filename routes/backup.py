from flask import Blueprint, jsonify, request, send_file, Response, render_template
from utils.auth import require_permission
from utils.db import supabase
import io
import csv
import traceback
import urllib.request as _ureq
import re

backup_bp = Blueprint('backup', __name__)

def _safe_filename(name):
    if not name: return 'archivo'
    return re.sub(r'[^\w\-]', '_', str(name))[:100]

def _fetch_file_bytes(url):
    try:
        req = _ureq.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with _ureq.urlopen(req, timeout=10) as response:
            return response.read()
    except:
        return None

# BACKUP MODULE

try:
    import pyzipper
except ImportError:
    pyzipper = None
import contextlib

@contextlib.contextmanager
def create_zip_context(buf, password=None):
    if pyzipper and password:
        zf = pyzipper.AESZipFile(buf, 'w', compression=pyzipper.ZIP_DEFLATED, encryption=pyzipper.WZ_AES)
        zf.setpassword(password.encode('utf-8'))
    else:
        zf = create_zip_context(buf, password)
    try:
        yield zf
    finally:
        zf.close()

def verify_backup_security(user_id, password, inst_id, action_type):
    from werkzeug.security import check_password_hash
    if not user_id or not password:
        return False, "Se requiere contrasea de administrador."
        
    res = supabase.table('users').select('email, password_hash').eq('id', user_id).execute()
    if not res.data:
        return False, "Usuario no encontrado."
        
    user = res.data[0]
    email = user.get('email')
    phash = user.get('password_hash')
    
    is_valid = check_password_hash(phash, password) if phash else False
    status = 'SUCCESS' if is_valid else 'DENIED'
    
    try:
        supabase.table('security_backup_logs').insert({
            'user_id': user_id,
            'user_email': email,
            'inst_id': int(inst_id) if inst_id else None,
            'action_type': action_type,
            'status': status
        }).execute()
    except Exception as e:
        print("Error logging security:", e)
        
    return is_valid, ("Acceso denegado. Contrasea incorrecta." if not is_valid else "")

# ══════════════════════════════════════════════════════════════════
import zipfile, csv, io, urllib.request as _ureq, traceback

@backup_bp.route('/backup')
def backup_page():
    return render_template('backup.html')

@backup_bp.route('/api/backup/stats', methods=['GET'])
@require_permission('herramientas')
def backup_stats():
    try:
        inst_id = request.args.get('inst_id', 1, type=int)
        kwargs = {}
        if inst_id:
            kwargs['inst_id'] = inst_id

        def cnt(table, **kw):
            try:
                q = supabase.table(table).select('id', count='exact')
                for k, v in kw.items():
                    q = q.eq(k, v)
                return q.execute().count or 0
            except Exception:
                return 0

        if inst_id:
            ev = cnt('evidences', inst_id=inst_id)
            fa = cnt('factors', inst_id=inst_id)
            us = cnt('users', inst_id=inst_id)
            ac = cnt('planning_activities')   # no inst_id col - approximate
        else:
            ev = cnt('evidences')
            fa = cnt('factors')
            us = cnt('users')
            ac = cnt('planning_activities')

        # Informes are stored in statistics table
        try:
            inf_q = supabase.table('statistics').select('id', count='exact')
            if inst_id:
                inf_q = inf_q.eq('inst_id', inst_id)
            inf = inf_q.execute().count or 0
        except Exception:
            inf = 0

        return jsonify({"evidencias": ev, "factores": fa, "usuarios": us,
                        "informes": inf, "actividades": ac})
    except Exception as e:
        return jsonify({"evidencias": 0, "factores": 0, "usuarios": 0,
                        "informes": 0, "actividades": 0})


def _safe_filename(s):
    """Remove/replace chars not safe for filesystem paths."""
    import re
    s = str(s or 'sin_nombre')
    s = re.sub(r'[^\w\s\-\.]', '_', s, flags=re.UNICODE)
    return s[:80].strip()


def _fetch_file_bytes(url):
    """Download a file URL. Returns bytes or None."""
    try:
        req = _ureq.Request(url, headers={'User-Agent': 'SIACredit-Backup/1.0'})
        with _ureq.urlopen(req, timeout=20) as r:
            return r.read()
    except Exception:
        return None


def _build_full_zip(inst_id, scope, modules, year, program_id, password=None):
    """Build the complete backup ZIP in memory and return bytes."""
    buf = io.BytesIO()
    with create_zip_context(buf, password) as zf:
        year_label = str(year) if year else 'todos_los_anos'

        # ── README ───────────────────────────────────────────────
        readme = (
            "BACKUP SIAC\n"
            f"Institución ID: {inst_id}\n"
            f"Alcance: {scope}\n"
            f"Año filtrado: {year_label}\n"
            f"Módulos: {', '.join(modules)}\n"
            f"Fecha de generación: {__import__('datetime').datetime.now().isoformat()}\n\n"
            "Estructura del ZIP:\n"
            "  backup_SIAC/\n"
            "    README.txt\n"
            "    datos/  (CSV de cada módulo)\n"
            "    evidencias/  (año/factor/caracteristica/aspecto/)\n"
        )
        zf.writestr("backup_SIAC/README.txt", readme)

        # ── DATOS CSV ────────────────────────────────────────────
        module_map = {
            'evaluaciones': ('evaluations', ['id','inst_id','program_id','created_at','status','score','comments']),
            'usuarios': ('users', ['id','name','email','role','inst_id','program_id']),
            'planes_mejora': ('planes_mejora', ['id','inst_id','description','status','created_at']),
        }

        for mod in modules:
            if mod in module_map:
                table, cols = module_map[mod]
                try:
                    q = supabase.table(table).select(','.join(cols))
                    if inst_id:
                        q = q.eq('inst_id', inst_id)
                    rows = q.execute().data or []
                    csv_buf = io.StringIO()
                    writer = csv.DictWriter(csv_buf, fieldnames=cols, extrasaction='ignore')
                    writer.writeheader()
                    writer.writerows(rows)
                    zf.writestr(f"backup_SIAC/datos/{mod}.csv", csv_buf.getvalue())
                except Exception as ex:
                    zf.writestr(f"backup_SIAC/datos/{mod}_error.txt", str(ex))

        # ── EVIDENCIAS con archivos ──────────────────────────────
        if 'evidencias' in modules:
            try:
                # Load hierarchy: factors -> characteristics -> aspects -> evidences
                fq = supabase.table('factors').select('*,characteristics(*,aspects(*))')
                if inst_id:
                    fq = fq.eq('inst_id', inst_id)
                if program_id:
                    fq = fq.eq('program_id', int(program_id))
                factors = fq.execute().data or []

                # Build aspect_id -> path map
                aspect_path = {}
                for f in factors:
                    fn = _safe_filename(f.get('name') or f.get('title') or f.get('text') or f.get('id'))
                    for c in (f.get('characteristics') or []):
                        cn = _safe_filename(c.get('name') or c.get('title') or c.get('text') or c.get('id'))
                        for a in (c.get('aspects') or []):
                            an = _safe_filename((a.get('text') or a.get('name') or a.get('title') or str(a.get('id')))[:50])
                            aspect_path[str(a['id'])] = f"{year_label}/{fn}/{cn}/{an}"

                # Fetch evidences
                eq = supabase.table('evidences').select('*')
                if inst_id:
                    eq = eq.eq('inst_id', inst_id)
                if program_id:
                    eq = eq.eq('program_id', int(program_id))
                evs = eq.execute().data or []

                csv_rows = []
                for ev in evs:
                    asp_path = aspect_path.get(str(ev.get('aspect_id') or ''), year_label + '/sin_clasificar')
                    base = f"backup_SIAC/evidencias/{asp_path}/"
                    # metadata file
                    meta = "\n".join([f"{k}: {v}" for k, v in ev.items() if k != 'file_url'])
                    ev_name = _safe_filename(ev.get('title') or ev.get('id') or 'evidencia')
                    zf.writestr(base + ev_name + "_info.txt", meta)
                    # download actual file if URL present
                    url = ev.get('file_url') or ev.get('url') or ''
                    if url:
                        fbytes = _fetch_file_bytes(url)
                        if fbytes:
                            ext = url.split('?')[0].rsplit('.', 1)[-1] if '.' in url else 'bin'
                            zf.writestr(base + ev_name + '.' + ext, fbytes)
                    csv_rows.append(ev)

                # CSV de evidencias
                if csv_rows:
                    csv_buf = io.StringIO()
                    keys = list(csv_rows[0].keys())
                    writer = csv.DictWriter(csv_buf, fieldnames=keys, extrasaction='ignore')
                    writer.writeheader(); writer.writerows(csv_rows)
                    zf.writestr("backup_SIAC/datos/evidencias.csv", csv_buf.getvalue())
            except Exception as ex:
                zf.writestr("backup_SIAC/evidencias/error.txt", traceback.format_exc())

        # ── PLANIFICACION ────────────────────────────────────────
        if 'planificacion' in modules:
            try:
                import json
                plan_tables = {
                    'ejes': 'planning_axes',
                    'estrategias': 'planning_strategies',
                    'objetivos_generales': 'planning_general_objectives',
                    'objetivos_especificos': 'planning_specific_objectives',
                    'actividades': 'planning_activities',
                }
                for name, table in plan_tables.items():
                    rows = supabase.table(table).select('*').execute().data or []
                    if rows:
                        csv_buf = io.StringIO()
                        writer = csv.DictWriter(csv_buf, fieldnames=list(rows[0].keys()), extrasaction='ignore')
                        writer.writeheader(); writer.writerows(rows)
                        zf.writestr(f"backup_SIAC/datos/planificacion_{name}.csv", csv_buf.getvalue())
                        
                # Also download evidences for activities
                stats_res = supabase.table('statistics').select('*').like('table_id', 'PLANNING_ACT_EVID_%').execute().data or []
                for s in stats_res:
                    act_id = s['table_id'].replace('PLANNING_ACT_EVID_', '')
                    try:
                        evs = json.loads(s['data_json']) if isinstance(s['data_json'], str) else s['data_json']
                        if isinstance(evs, list):
                            for i, ev in enumerate(evs):
                                url = ev.get('public_url') or ev.get('url') or ''
                                if url:
                                    fbytes = _fetch_file_bytes(url)
                                    if fbytes:
                                        ev_name = _safe_filename(ev.get('name') or f"evidencia_{i}")
                                        ext = url.split('?')[0].rsplit('.', 1)[-1] if '.' in url else 'bin'
                                        if ext == 'bin' and ev_name:
                                            ext = ev_name.split('.')[-1] if '.' in ev_name else 'bin'
                                        base = f"backup_SIAC/Planificacion_Evidencias/Actividad_{act_id}/"
                                        zf.writestr(base + ev_name + '.' + ext, fbytes)
                                        # Write metadata text
                                        meta = f"Actividad ID: {act_id}\nSubido por: {ev.get('uploader')}\nFecha: {ev.get('date')}\nArchivo original: {ev.get('name')}"
                                        zf.writestr(base + ev_name + "_info.txt", meta)
                    except Exception as ev_err:
                        zf.writestr(f"backup_SIAC/Planificacion_Evidencias/Actividad_{act_id}/error.txt", str(ev_err))
            except Exception as ex:
                zf.writestr("backup_SIAC/datos/planificacion_error.txt", str(ex))

        # ── DOFA ─────────────────────────────────────────────────
        if 'dofa' in modules:
            try:
                strats = supabase.table('planning_strategies').select('*').execute().data or []
                if strats:
                    csv_buf = io.StringIO()
                    writer = csv.DictWriter(csv_buf, fieldnames=list(strats[0].keys()), extrasaction='ignore')
                    writer.writeheader(); writer.writerows(strats)
                    zf.writestr("backup_SIAC/datos/dofa_estrategias.csv", csv_buf.getvalue())
            except Exception as ex:
                zf.writestr("backup_SIAC/datos/dofa_error.txt", str(ex))

    buf.seek(0)
    return buf.read()


@backup_bp.route('/api/backup/generate', methods=['POST'])
@require_permission('herramientas')
def backup_generate():
    """Generate the full ZIP backup and stream it."""
    try:
        data = request.json or {}
        inst_id = data.get('inst_id', 1)
        user_id = data.get('user_id')
        password = data.get('password')
        is_valid, msg = verify_backup_security(user_id, password, inst_id, 'FULL_BACKUP')
        if not is_valid:
            return jsonify({'status': 'error', 'message': msg}), 403
        scope = data.get('scope', 'inst')
        modules = data.get('modules', [])
        year = data.get('year')
        program_id = data.get('program_id')

        if scope == 'super':
            inst_id = None  # All institutions

        zip_bytes = _build_full_zip(inst_id, scope, modules, year, program_id, password)
        ts = __import__('datetime').datetime.now().strftime('%Y%m%d_%H%M%S')
        fname = f"backup_SIAC_{ts}.zip"
        return Response(
            zip_bytes,
            mimetype='application/zip',
            headers={'Content-Disposition': f'attachment; filename="{fname}"'}
        )
    except Exception as e:
        print(f"Backup error: {e}\n{traceback.format_exc()}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@backup_bp.route('/api/backup/factor', methods=['POST'])
@require_permission('herramientas')
def backup_factor():
    """ZIP backup of a single factor."""
    try:
        data = request.json or {}
        inst_id = data.get('inst_id', 1)
        user_id = data.get('user_id')
        password = data.get('password')
        is_valid, msg = verify_backup_security(user_id, password, inst_id, 'FACTOR_BACKUP')
        if not is_valid:
            return jsonify({'status': 'error', 'message': msg}), 403
        factor_id = data.get('factor_id')
        caracteristica_id = data.get('caracteristica_id')
        year = data.get('year')

        buf = io.BytesIO()
        with create_zip_context(buf, password) as zf:
            # Load factor details
            fq = supabase.table('factors').select('*,characteristics(*,aspects(*))').eq('id', factor_id)
            factors = fq.execute().data or []
            if not factors:
                return jsonify({'status': 'error', 'message': 'Factor no encontrado'}), 404

            factor = factors[0]
            fname = _safe_filename(factor.get('name') or factor_id)
            zf.writestr(f"{fname}/README.txt",
                f"Factor: {factor.get('name')}\nID: {factor_id}\nAño: {year or 'todos'}\n")

            # Build aspect tree
            for c in (factor.get('characteristics') or []):
                if caracteristica_id and str(c['id']) != str(caracteristica_id):
                    continue
                cname = _safe_filename(c.get('name') or c.get('title') or c.get('text') or c['id'])
                for a in (c.get('aspects') or []):
                    aname = _safe_filename(a.get('text') or a.get('name') or a.get('title') or a['id'])
                    folder = f"{fname}/{cname}/{aname}/"

                    # Evidences for this aspect
                    eq = supabase.table('evidences').select('*').eq('aspect_id', a['id'])
                    evs = eq.execute().data or []
                    csv_rows = []
                    for ev in evs:
                        ev_title = _safe_filename(ev.get('title') or ev.get('id') or 'ev')
                        meta = "\n".join([f"{k}: {v}" for k, v in ev.items() if k != 'file_url'])
                        zf.writestr(folder + ev_title + "_info.txt", meta)
                        url = ev.get('file_url') or ev.get('url') or ''
                        if url:
                            fbytes = _fetch_file_bytes(url)
                            if fbytes:
                                ext = url.split('?')[0].rsplit('.', 1)[-1] if '.' in url else 'bin'
                                zf.writestr(folder + ev_title + '.' + ext, fbytes)
                        csv_rows.append(ev)

                    if csv_rows:
                        csv_buf = io.StringIO()
                        writer = csv.DictWriter(csv_buf, fieldnames=list(csv_rows[0].keys()), extrasaction='ignore')
                        writer.writeheader(); writer.writerows(csv_rows)
                        zf.writestr(f"{fname}/{cname}/{aname}/evidencias.csv", csv_buf.getvalue())

        buf.seek(0)
        return Response(buf.read(), mimetype='application/zip',
            headers={'Content-Disposition': f'attachment; filename="factor_{factor_id}_backup.zip"'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@backup_bp.route('/api/backup/evidencias', methods=['POST'])
@require_permission('herramientas')
def backup_evidencias():
    """ZIP of evidences organized in folders."""
    try:
        data = request.json or {}
        inst_id = data.get('inst_id', 1)
        user_id = data.get('user_id')
        password = data.get('password')
        is_valid, msg = verify_backup_security(user_id, password, inst_id, 'EVIDENCIAS_BACKUP')
        if not is_valid:
            return jsonify({'status': 'error', 'message': msg}), 403
        year = data.get('year')
        status_filter = data.get('status')
        factor_id = data.get('factor_id')

        # Load hierarchy
        fq = supabase.table('factors').select('*,characteristics(*,aspects(*))')
        if inst_id:
            fq = fq.eq('inst_id', inst_id)
        if factor_id:
            fq = fq.eq('id', int(factor_id))
        factors = fq.execute().data or []

        aspect_path = {}
        for f in factors:
            fn = _safe_filename(f.get('name') or f.get('title') or f.get('text') or f['id'])
            for c in (f.get('characteristics') or []):
                cn = _safe_filename(c.get('name') or c.get('title') or c.get('text') or c['id'])
                for a in (c.get('aspects') or []):
                    an = _safe_filename((a.get('text') or a.get('name') or a.get('title') or str(a['id']))[:50])
                    year_seg = str(year) if year else 'sin_año'
                    aspect_path[str(a['id'])] = f"{year_seg}/{fn}/{cn}/{an}"

        # Fetch evidences
        eq = supabase.table('evidences').select('*')
        if inst_id:
            eq = eq.eq('inst_id', inst_id)
        if status_filter:
            eq = eq.eq('status', status_filter)
        evs = eq.execute().data or []

        buf = io.BytesIO()
        with create_zip_context(buf, password) as zf:
            zf.writestr("evidencias/README.txt",
                f"Backup de Evidencias SIAC\nFiltros: año={year}, estado={status_filter}\n"
                f"Total: {len(evs)} evidencias\n")

            all_rows = []
            for ev in evs:
                path = aspect_path.get(str(ev.get('aspect_id') or ''), 'sin_clasificar')
                base = f"evidencias/{path}/"
                ev_name = _safe_filename(ev.get('title') or ev.get('id') or 'evidencia')
                meta = "\n".join([f"{k}: {v}" for k, v in ev.items()])
                zf.writestr(base + ev_name + "_info.txt", meta)
                url = ev.get('file_url') or ev.get('url') or ''
                if url:
                    fbytes = _fetch_file_bytes(url)
                    if fbytes:
                        ext = url.split('?')[0].rsplit('.', 1)[-1] if '.' in url else 'bin'
                        zf.writestr(base + ev_name + '.' + ext, fbytes)
                all_rows.append(ev)

            # Master CSV
            if all_rows:
                csv_buf = io.StringIO()
                writer = csv.DictWriter(csv_buf, fieldnames=list(all_rows[0].keys()), extrasaction='ignore')
                writer.writeheader(); writer.writerows(all_rows)
                zf.writestr("evidencias/indice_evidencias.csv", csv_buf.getvalue())

        buf.seek(0)
        return Response(buf.read(), mimetype='application/zip',
            headers={'Content-Disposition': 'attachment; filename="evidencias_backup.zip"'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@backup_bp.route('/api/backup/csv/<tipo>', methods=['POST'])
@require_permission('herramientas')
def backup_csv_single(tipo):
    """Export a single module as CSV."""
    try:
        data = request.json or {}
        inst_id = data.get('inst_id', 1)
        user_id = data.get('user_id')
        password = data.get('password')
        is_valid, msg = verify_backup_security(user_id, password, inst_id, 'CSV_MODULE_BACKUP')
        if not is_valid:
            return jsonify({'status': 'error', 'message': msg}), 403
        csv_map = {
            'evaluaciones_csv': ('evaluations', None),
            'evidencias_csv': ('evidences', None),
            'planificacion_csv': ('planning_activities', None),
            'usuarios_csv': ('users', None),
            'planes_csv': ('planes_mejora', None),
            'estadisticas_csv': ('statistics', None),
        }
        if tipo not in csv_map:
            return jsonify({'status': 'error', 'message': 'Tipo no válido'}), 400

        table, _ = csv_map[tipo]
        q = supabase.table(table).select('*')
        if inst_id and table not in ('planning_activities', 'planning_axes', 'planning_strategies'):
            q = q.eq('inst_id', inst_id)
        rows = q.execute().data or []

        if not rows:
            return Response("sin_datos\n", mimetype='text/csv',
                headers={'Content-Disposition': f'attachment; filename="{tipo}.csv"'})

        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=list(rows[0].keys()), extrasaction='ignore')
        writer.writeheader(); writer.writerows(rows)
        return Response(buf.getvalue(), mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename="{tipo}.csv"'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@backup_bp.route('/api/backup/csv/all', methods=['POST'])
@require_permission('herramientas')
def backup_csv_all():
    """ZIP of ALL tables as CSV files."""
    try:
        data = request.json or {}
        inst_id = data.get('inst_id', 1)
        user_id = data.get('user_id')
        password = data.get('password')
        is_valid, msg = verify_backup_security(user_id, password, inst_id, 'CSV_ALL_BACKUP')
        if not is_valid:
            return jsonify({'status': 'error', 'message': msg}), 403

        tables_inst = ['evaluations', 'evidences', 'factors', 'users', 'planes_mejora',
                       'statistics', 'notificaciones']
        tables_global = ['planning_axes', 'planning_strategies', 'planning_general_objectives',
                         'planning_specific_objectives', 'planning_activities']

        buf = io.BytesIO()
        with create_zip_context(buf, password) as zf:
            for table in tables_inst:
                try:
                    q = supabase.table(table).select('*')
                    if inst_id:
                        q = q.eq('inst_id', inst_id)
                    rows = q.execute().data or []
                    if rows:
                        csv_buf = io.StringIO()
                        writer = csv.DictWriter(csv_buf, fieldnames=list(rows[0].keys()), extrasaction='ignore')
                        writer.writeheader(); writer.writerows(rows)
                        zf.writestr(f"datos/{table}.csv", csv_buf.getvalue())
                except Exception as ex:
                    zf.writestr(f"datos/{table}_error.txt", str(ex))

            for table in tables_global:
                try:
                    rows = supabase.table(table).select('*').execute().data or []
                    if rows:
                        csv_buf = io.StringIO()
                        writer = csv.DictWriter(csv_buf, fieldnames=list(rows[0].keys()), extrasaction='ignore')
                        writer.writeheader(); writer.writerows(rows)
                        zf.writestr(f"datos/{table}.csv", csv_buf.getvalue())
                except Exception as ex:
                    zf.writestr(f"datos/{table}_error.txt", str(ex))

        buf.seek(0)
        ts = __import__('datetime').datetime.now().strftime('%Y%m%d_%H%M%S')
        return Response(buf.read(), mimetype='application/zip',
            headers={'Content-Disposition': f'attachment; filename="SIAC_CSVs_{ts}.zip"'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@backup_bp.route('/api/backup/logs', methods=['POST'])
@require_permission('herramientas')
def get_backup_logs():
    data = request.json or {}
    user_id = data.get('user_id')
    
    # Optional: Check if user is admin
    res_user = supabase.table('users').select('role').eq('id', user_id).execute()
    if not res_user.data or res_user.data[0].get('role') not in ('admin', 'inst_admin', 'super_admin'):
         return jsonify({'status': 'error', 'message': 'No autorizado'}), 403
         
    inst_id = data.get('inst_id')
    q = supabase.table('security_backup_logs').select('*').order('timestamp', desc=True).limit(50)
    if inst_id:
        q = q.eq('inst_id', inst_id)
    res = q.execute()
    return jsonify({'status': 'success', 'logs': res.data or []})
