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
from flask import request, jsonify

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


def get_permissions_for_inst(inst_id):
    """
    Lee la matriz FORM_PERMISSIONS de Supabase para la institucion dada.
    Usa cache con TTL para minimizar consultas.

    Retorna: dict con forma { module_key: [lista de roles permitidos] }
    Ejemplo: { "autoevaluacion": ["inst_admin", "lider", "consultor", "auditor"] }
    """
    now = time.time()

    # Revisar cache
    if inst_id in _perms_cache:
        ts, cached_data = _perms_cache[inst_id]
        if now - ts < _CACHE_TTL:
            return cached_data

    # Consultar Supabase
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
        if res.data:
            raw = res.data[0]['data_json']
            perms = json.loads(raw) if isinstance(raw, str) else raw
        else:
            perms = {}
    except Exception as e:
        print(f"[auth] Error leyendo FORM_PERMISSIONS para inst_id={inst_id}: {e}")
        perms = {}

    _perms_cache[inst_id] = (now, perms)
    return perms


def _get_user(user_id):
    """
    Obtiene el usuario de Supabase por su ID.
    Usa cache con TTL corto para reducir consultas.
    """
    now = time.time()

    if user_id in _user_cache:
        ts, cached_user = _user_cache[user_id]
        if now - ts < _USER_CACHE_TTL:
            return cached_user

    try:
        sb = _get_supabase()
        res = sb.table('users').select("id, role, inst_id").eq("id", user_id).execute()
        user = res.data[0] if res.data else None
    except Exception as e:
        print(f"[auth] Error buscando usuario {user_id}: {e}")
        user = None

    if user:
        _user_cache[user_id] = (now, user)
    return user


def require_permission(module_key):
    """
    Decorador Flask que valida el rol del usuario antes de ejecutar el endpoint.

    Flujo:
      1. Lee el header X-User-Id de la peticion.
      2. Busca al usuario en DB (con cache).
      3. Si el rol es 'admin' -> bypass total.
      4. Lee la matriz FORM_PERMISSIONS (con cache).
      5. Verifica si el rol esta en la lista de roles permitidos para module_key.
      6. Permite (200) o rechaza (403).

    Args:
        module_key: Clave del modulo a proteger, e.g. 'skel_hc360', 'autoevaluacion'.

    Returns:
        Respuesta 401 si falta el header.
        Respuesta 403 si el rol no tiene acceso.
        El resultado de la funcion original si el acceso es permitido.
    """
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            user_id = request.headers.get('X-User-Id', '').strip()

            # 1. Verificar que viene identificado
            if not user_id:
                return jsonify({
                    "status": "error",
                    "message": "No autenticado. Se requiere el header X-User-Id."
                }), 401

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

            # 4. El módulo de configuración y herramientas gerenciales son de uso exclusivo para Administradores (admin e inst_admin)
            if module_key in ['configuracion', 'herramientas']:
                if role not in ['admin', 'inst_admin']:
                    return jsonify({
                        "status": "error",
                        "message": f"Acceso denegado: El módulo es de uso exclusivo para Administradores."
                    }), 403
                return f(*args, **kwargs)

            # 5. Leer permisos de la institucion
            perms = get_permissions_for_inst(inst_id)

            # 5. Si el modulo no tiene configuracion de permisos, permitir por defecto
            #    (evita bloquear en instalaciones nuevas sin permisos configurados)
            if module_key not in perms:
                return f(*args, **kwargs)

            # 6. Verificar rol
            allowed_roles = perms.get(module_key, [])
            if role not in allowed_roles:
                return jsonify({
                    "status": "error",
                    "message": (
                        f"Acceso denegado: tu rol '{role}' no tiene permiso "
                        f"sobre el modulo '{module_key}'."
                    )
                }), 403

            return f(*args, **kwargs)
        return wrapper
    return decorator
