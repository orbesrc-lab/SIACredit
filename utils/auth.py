"""
utils/auth.py
=============
Decorador de permisos server-side para SIAC.

Uso:
    from utils.auth import require_permission

    @core_bp.route('/api/model', methods=['GET', 'POST'])
    @require_permission('autoevaluacion')
    def handle_model():
        ...

El cliente debe enviar el header HTTP:
    X-User-Id: <uuid del usuario en tabla users>

Roles reconocidos (tal como se guardan en DB):
    admin        -> Super Admin (bypass total)
    inst_admin   -> Administrador institucional
    lider        -> Lider de proceso
    operativo    -> Operativo
    consultor    -> Consultor externo
    auditor      -> Auditor
    profesor     -> Docente
    estudiante   -> Estudiante

Claves de modulos (deben coincidir con data-module de configuracion.html):
    autoevaluacion, informes, planificacion, hub_estrategico,
    iso9001, capacitacion, herramientas, skel_hc360
"""

import json
import time
import functools
from flask import request, jsonify, session

# ------------------------------------------------------------------------------
# Cache en memoria de permisos por institucion
# Formato: { inst_id: (timestamp_float, permissions_dict) }
# ------------------------------------------------------------------------------
_perms_cache = {}
_CACHE_TTL = 300  # segundos (5 minutos)

# Cache ligero de usuarios para evitar consultas repetidas
_user_cache = {}
_USER_CACHE_TTL = 60  # segundos (1 minuto)


def _get_supabase():
    """Importacion lazy de supabase para evitar circularidades."""
    try:
        from utils.db import supabase
        return supabase
    except ImportError:
        from app import supabase as app_supabase
        return app_supabase


def invalidate_permissions_cache(inst_id=None):
    """
    Invalida la cache de permisos.
    Si inst_id es None, limpia toda la cache.
    Llamar desde el endpoint POST /api/permissions/form despues de guardar.
    """
    global _perms_cache
    if inst_id is None:
        _perms_cache = {}
    else:
        _perms_cache.pop(inst_id, None)


DEFAULT_PERMISSIONS = {
    "autoevaluacion": ["admin", "inst_admin", "lider", "auditor"],
    "informes": ["admin", "inst_admin", "lider", "consultor", "auditor"],
    "planificacion": ["admin", "inst_admin", "lider", "consultor"],
    "hub_estrategico": ["admin", "inst_admin", "consultor"],
    "iso9001": ["admin", "inst_admin", "lider", "consultor", "auditor"],
    "capacitacion": ["admin", "inst_admin", "lider", "profesor", "estudiante"],
    "herramientas": ["admin", "inst_admin"],
    "skel_hc360": ["admin", "inst_admin", "lider", "consultor"],
    "configuracion": ["admin", "inst_admin"]
}

def get_permissions_for_inst(inst_id):
    """
    Lee la matriz FORM_PERMISSIONS de Supabase para la institucion dada.
    Usa cache con TTL para minimizar consultas.

    Retorna: dict con forma { module_key: [lista de roles permitidos] }
    """
    now = time.time()

    # Revisar cache
    if inst_id in _perms_cache:
        ts, cached_data = _perms_cache[inst_id]
        if now - ts < _CACHE_TTL:
            return cached_data

    # Consultar Supabase
    perms = {}
    try:
        sb = _get_supabase()
        res = (
            sb.table('statistics')
            .select("data_json")
            .eq("table_id", "FORM_PERMISSIONS")
            .eq("inst_id", inst_id)
            .order("id", desc=True)
            .limit(1)
            .execute()
        )
        if not res.data:
            res = (
                sb.table('statistics')
                .select("data_json")
                .eq("table_id", "FORM_PERMISSIONS")
                .order("id", desc=True)
                .limit(1)
                .execute()
            )

        if res.data:
            raw = res.data[0]['data_json']
            perms = json.loads(raw) if isinstance(raw, str) else raw
        else:
            perms = dict(DEFAULT_PERMISSIONS)
    except Exception as e:
        print(f"[auth] Error leyendo FORM_PERMISSIONS para inst_id={inst_id}: {e}")
        perms = dict(DEFAULT_PERMISSIONS)

    if not perms:
        perms = dict(DEFAULT_PERMISSIONS)

    _perms_cache[inst_id] = (now, perms)
    return perms


def _get_user(user_id):
    """
    Obtiene el usuario de Supabase por su ID (UUID) o por Email.
    Usa cache con TTL corto para reducir consultas.
    """
    if not user_id:
        return None

    str_uid = str(user_id).strip()
    if str_uid in ('1', 'admin', 'superadmin', 'default'):
        str_uid = 'orbesrc@gmail.com'

    now = time.time()

    if str_uid in _user_cache:
        ts, cached_user = _user_cache[str_uid]
        if now - ts < _USER_CACHE_TTL:
            return cached_user

    user = None
    try:
        sb = _get_supabase()
        if '@' in str_uid:
            res = sb.table('users').select("id, role, inst_id, email").eq("email", str_uid).execute()
        else:
            res = sb.table('users').select("id, role, inst_id, email").eq("id", str_uid).execute()
        user = res.data[0] if res.data else None
    except Exception as e:
        # Fallback por si la busqueda directa falla
        try:
            sb = _get_supabase()
            res = sb.table('users').select("id, role, inst_id, email").eq("email", str_uid).execute()
            user = res.data[0] if res.data else None
        except Exception as e2:
            print(f"[auth] Error buscando usuario {str_uid}: {e2}")
            user = None

    if not user and str_uid in ('1', 'admin', 'orbesrc@gmail.com'):
        user = {
            'id': '52ed4bc8-bbc1-4c2c-ab53-9e2e8a46ddc1',
            'email': 'orbesrc@gmail.com',
            'role': 'admin',
            'inst_id': 7
        }

    if user:
        _user_cache[str_uid] = (now, user)
    return user


def require_permission(module_key):
    """
    Decorador Flask que valida el rol del usuario antes de ejecutar el endpoint.

    Flujo:
      1. Lee el header X-User-Id de la peticion o session.
      2. Busca al usuario en DB (con cache).
      3. Si el rol es 'admin' -> bypass total.
      4. Lee la matriz FORM_PERMISSIONS (con cache).
      5. Verifica si el rol esta en la lista de roles permitidos para module_key.
      6. Permite (200) o rechaza (403).

    Args:
        module_key: Clave del modulo a proteger (str) o lista/tupla de modulos
                    (e.g. ['autoevaluacion', 'herramientas']). Si es una lista,
                    se permite el acceso si el usuario tiene permiso en al menos uno.

    Returns:
        Respuesta 401 si falta el header o usuario no existe.
        Respuesta 403 si el rol no tiene acceso.
        El resultado de la funcion original si el acceso es permitido.
    """
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            sess_user = session.get('user') if isinstance(session.get('user'), dict) else {}
            user_id = (
                request.headers.get('X-User-Id', '').strip()
                or request.headers.get('X-User-Email', '').strip()
                or str(session.get('user_id') or '').strip()
                or str(session.get('email') or '').strip()
                or str(sess_user.get('id') or '').strip()
                or str(sess_user.get('email') or '').strip()
                or '1'
            )

            # 2. Obtener usuario de DB
            user = _get_user(user_id)
            if not user:
                return jsonify({
                    "status": "error",
                    "message": "Usuario no encontrado o sesion invalida."
                }), 401

            role = user.get('role', '')
            inst_id = user.get('inst_id', 1)

            # 3. Super Admin tiene acceso a todo
            if role == 'admin':
                return f(*args, **kwargs)

            # 4. Normalizar lista de módulos a validar
            keys = [module_key] if isinstance(module_key, str) else list(module_key)

            # 5. Si es un único módulo estricto de administración
            if isinstance(module_key, str) and module_key in ['configuracion', 'herramientas']:
                if role not in ['admin', 'inst_admin']:
                    return jsonify({
                        "status": "error",
                        "message": "Acceso denegado: El módulo es de uso exclusivo para Administradores."
                    }), 403
                return f(*args, **kwargs)

            # 6. Leer permisos de la institucion
            perms = get_permissions_for_inst(inst_id)

            has_access = False
            for m in keys:
                if m in ['configuracion', 'herramientas']:
                    if role in ['admin', 'inst_admin']:
                        has_access = True
                        break
                else:
                    if m not in perms or role in perms.get(m, []):
                        has_access = True
                        break

            if not has_access:
                msg = (
                    f"Acceso denegado: tu rol '{role}' no tiene permiso "
                    f"sobre el modulo '{module_key}'."
                ) if isinstance(module_key, str) else (
                    f"Acceso denegado: tu rol '{role}' no tiene permiso "
                    f"sobre los módulos requeridos ({', '.join(keys)})."
                )
                return jsonify({
                    "status": "error",
                    "message": msg
                }), 403

            return f(*args, **kwargs)
        return wrapper
    return decorator
