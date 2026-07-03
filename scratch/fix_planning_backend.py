import re

def fix_app_py():
    with open('c:\\SIAC\\app.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # Fix /api/planning/tree
    old_tree = "        inst_id = request.args.get('inst_id')\n        if not inst_id:\n            return jsonify({'status': 'error', 'message': 'inst_id is required'})"
    new_tree = "        inst_id = request.args.get('inst_id')\n        try:\n            inst_id = int(inst_id)\n        except (ValueError, TypeError):\n            inst_id = 1\n        if not inst_id:\n            return jsonify({'status': 'error', 'message': 'inst_id is required'})"
    content = content.replace(old_tree, new_tree)

    # Fix /api/planning/users
    old_users = "        inst_id = request.args.get('inst_id')\n        if not inst_id:\n            return jsonify({'status': 'error', 'message': 'inst_id required'})"
    new_users = "        inst_id = request.args.get('inst_id')\n        try:\n            inst_id = int(inst_id)\n        except (ValueError, TypeError):\n            inst_id = 1\n        if not inst_id:\n            return jsonify({'status': 'error', 'message': 'inst_id required'})"
    content = content.replace(old_users, new_users)

    # Fix /api/planning/node
    old_node = "        inst_id = data.get('inst_id')\n        parent_id = data.get('parent_id')\n        \n        if not node_type or not inst_id or not parent_id:"
    new_node = "        inst_id = data.get('inst_id')\n        try:\n            inst_id = int(inst_id)\n        except (ValueError, TypeError):\n            inst_id = 1\n        parent_id = data.get('parent_id')\n        \n        if not node_type or not inst_id or not parent_id:"
    content = content.replace(old_node, new_node)

    # Fix /api/planning/suggest
    old_suggest = "        target_id = data.get('target_id')\n        inst_id = data.get('inst_id')\n        \n        if not req_type or not target_id:"
    new_suggest = "        target_id = data.get('target_id')\n        inst_id = data.get('inst_id')\n        try:\n            inst_id = int(inst_id)\n        except (ValueError, TypeError):\n            inst_id = 1\n        \n        if not req_type or not target_id:"
    content = content.replace(old_suggest, new_suggest)

    with open('c:\\SIAC\\app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Fixed app.py planning endpoints")

if __name__ == '__main__':
    fix_app_py()
