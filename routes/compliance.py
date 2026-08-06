from flask import Blueprint, jsonify, request
from utils.db import supabase
from utils.auth import require_permission
from datetime import datetime
import calendar

compliance_bp = Blueprint('compliance', __name__)

MONTHS_ES = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']

def compute_compliance_stats(inst_id, program_id=None):
    """
    Dynamically computes compliance metrics from the database for a given institution.
    Optionally filters by program_id.
    """
    # 1. Fetch all factors for this institution (optionally filtered by program)
    factors_q = supabase.table('factors').select('id, name, program_id').eq('inst_id', inst_id)
    if program_id:
        factors_q = factors_q.eq('program_id', program_id)
    factors = factors_q.execute().data
    f_ids = [f['id'] for f in factors]

    if not f_ids:
        return _empty_stats()

    # 2. Fetch all characteristics belonging to those factors
    chars = supabase.table('characteristics').select('id, factor_id').in_('factor_id', f_ids).execute().data
    c_ids = [c['id'] for c in chars]

    if not c_ids:
        return _empty_stats()

    # 3. Fetch all aspects (requisitos) belonging to those characteristics
    aspects = supabase.table('aspects').select('id, char_id').in_('char_id', c_ids).execute().data
    a_ids = [a['id'] for a in aspects]

    # 4. Fetch all evidences for this institution
    ev_q = supabase.table('evidences').select('id, aspect_id, status, created_at').eq('inst_id', inst_id)
    if program_id:
        ev_q = ev_q.eq('program_id', program_id)
    evidences = ev_q.execute().data

    # Build aspect-to-evidences map
    aspect_ev_map = {}
    for ev in evidences:
        a_id = ev['aspect_id']
        if a_id not in aspect_ev_map:
            aspect_ev_map[a_id] = []
        aspect_ev_map[a_id].append(ev)

    # 5. Classify aspects
    fulfilled = 0
    in_progress = 0
    not_fulfilled = 0

    for a in aspects:
        evs = aspect_ev_map.get(a['id'], [])
        if not evs:
            not_fulfilled += 1
        elif any(ev['status'] in ['aprobado', 'aprobada'] for ev in evs):
            fulfilled += 1
        else:
            in_progress += 1

    total = len(aspects)
    global_pct = round((fulfilled / total) * 100, 1) if total else 0.0

    # 6. Compute per-factor compliance (maps to "por normativa" sections)
    # Group factors by their name/number as a proxy for normativa sections
    factor_stats = []
    COLORS = ['#10b981', '#3b82f6', '#8b5cf6', '#f97316', '#ef4444', '#06b6d4', '#f59e0b']

    for i, factor in enumerate(factors[:7]):  # limit to first 7 factors for display
        fid = factor['id']
        # Get chars for this factor
        f_char_ids = [c['id'] for c in chars if c['factor_id'] == fid]
        if not f_char_ids:
            continue
        # Get aspects for those chars
        f_aspects = [a for a in aspects if a['char_id'] in f_char_ids]
        if not f_aspects:
            continue

        f_fulfilled = 0
        f_total = len(f_aspects)
        for a in f_aspects:
            evs = aspect_ev_map.get(a['id'], [])
            if any(ev['status'] in ['aprobado', 'aprobada'] for ev in evs):
                f_fulfilled += 1

        f_pct = round((f_fulfilled / f_total) * 100) if f_total else 0
        factor_stats.append({
            "name": f"Factor {factor.get('number', i+1)}: {factor.get('name', 'Sin nombre')[:50]}",
            "percentage": f_pct,
            "color": COLORS[i % len(COLORS)]
        })

    # 7. Monthly trend of evidence uploads (last 8 months)
    monthly_counts = {}
    for ev in evidences:
        ts = ev.get('created_at', '')
        if ts and len(ts) >= 7:
            month_key = ts[:7]  # 'YYYY-MM'
            monthly_counts[month_key] = monthly_counts.get(month_key, 0) + 1

    # Build last 8 months labels & data
    now = datetime.utcnow()
    trend_labels = []
    trend_data = []
    for offset in range(7, -1, -1):
        month_num = now.month - offset
        year = now.year
        while month_num <= 0:
            month_num += 12
            year -= 1
        key = f"{year}-{month_num:02d}"
        trend_labels.append(MONTHS_ES[month_num - 1])
        trend_data.append(monthly_counts.get(key, 0))

    # 8. Build alerts from aspects with pending evidences only
    alerts = []
    pending_aspects = [a['id'] for a in aspects if any(
        ev['status'] == 'pendiente' for ev in aspect_ev_map.get(a['id'], [])
    )]
    if pending_aspects:
        alerts.append({
            "title": "Evidencias pendientes de revisión",
            "detail": f"{len(pending_aspects)} aspecto(s) tienen evidencias en estado pendiente",
            "type": "Pendiente",
            "status_class": "warning"
        })

    empty_aspects_count = not_fulfilled
    if empty_aspects_count > 0:
        alerts.append({
            "title": "Aspectos sin evidencia",
            "detail": f"{empty_aspects_count} de {total} requisito(s) no tienen evidencia cargada",
            "type": "Crítico",
            "status_class": "critical"
        })

    if global_pct < 50:
        alerts.append({
            "title": "Cumplimiento global bajo",
            "detail": f"El porcentaje de cumplimiento global es {global_pct}% — se requiere atención",
            "type": "Advertencia",
            "status_class": "pending"
        })

    return {
        "cumplimiento_global": global_pct,
        "requisitos_aplicables": total,
        "requisitos_cumplidos": fulfilled,
        "requisitos_en_proceso": in_progress,
        "requisitos_no_cumplidos": not_fulfilled,
        "cumplimiento_por_normativa": factor_stats,
        "evidencias_totales": len(evidences),
        "evidencias_tendencia": {
            "labels": trend_labels,
            "data": trend_data
        },
        "alertas": alerts
    }


def _empty_stats():
    return {
        "cumplimiento_global": 0,
        "requisitos_aplicables": 0,
        "requisitos_cumplidos": 0,
        "requisitos_en_proceso": 0,
        "requisitos_no_cumplidos": 0,
        "cumplimiento_por_normativa": [],
        "evidencias_totales": 0,
        "evidencias_tendencia": {"labels": [], "data": []},
        "alertas": [{"title": "Sin datos", "detail": "No se encontraron factores ni evidencias para esta institución", "type": "Info", "status_class": "warning"}]
    }


@compliance_bp.route('/api/compliance/stats', methods=['GET'])
@require_permission('autoevaluacion')
def get_compliance_stats():
    try:
        inst_id = request.args.get('inst_id', type=int)
        program_id = request.args.get('program_id', type=int)

        if not inst_id:
            # Try to get from user session via token
            return jsonify({"status": "error", "message": "inst_id is required"}), 400

        data = compute_compliance_stats(inst_id, program_id)
        return jsonify({"status": "success", "data": data})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@compliance_bp.route('/api/compliance/programs', methods=['GET'])
@require_permission('autoevaluacion')
def get_compliance_programs():
    """Returns list of programs for a given institution, for the program filter selector."""
    try:
        inst_id = request.args.get('inst_id', type=int)
        if not inst_id:
            return jsonify({"status": "error", "message": "inst_id is required"}), 400

        programs = supabase.table('programs').select('id, name').eq('inst_id', inst_id).execute().data
        return jsonify({"status": "success", "programs": programs})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
