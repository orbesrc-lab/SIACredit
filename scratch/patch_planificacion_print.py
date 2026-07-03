import re

with open(r'c:\SIAC\templates\planificacion.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add CSS
css_to_add = """
        @media print {
            body { background: white !important; }
            .sidebar, .topbar, .page-header, .axis-actions, .actions-row, .btn-toolbar, .btn-action, .axis-toggle, .strat-right i, .btn-gantt { display: none !important; }
            .main-content { margin-left: 0 !important; width: 100% !important; padding: 10px !important; }
            .lvl-axis-card, .lvl-strat-card, .lvl-gen-card, .lvl-act-card { border: 1px solid #ccc !important; box-shadow: none !important; break-inside: avoid; margin-bottom: 15px; }
            .tree-container { gap: 20px; }
            
            body.print-focus-mode .tree-container > .lvl-axis-card { display: none !important; }
            body.print-focus-mode .tree-container > .lvl-axis-card.print-focus-card, 
            body.print-focus-mode .tree-container > .lvl-axis-card.print-focus-parent { display: block !important; }

            body.print-focus-mode .strategies-grid > .lvl-strat-card { display: none !important; }
            body.print-focus-mode .strategies-grid > .lvl-strat-card.print-focus-card,
            body.print-focus-mode .strategies-grid > .lvl-strat-card.print-focus-parent { display: block !important; }
        }
"""
content = content.replace("</style>", css_to_add + "\n    </style>")

# 2. Add Global Print Button
btn_global_search = '<button class="btn-gantt" onclick="openGanttModal()">Ver Cronograma (Gantt)</button>'
btn_global_replace = """<div style="display:flex; gap:10px;">
                        <button class="btn-gantt" style="background: linear-gradient(135deg, #3b82f6, #2563eb);" onclick="imprimirPlaneacionGlobal()"><i class="fas fa-print"></i> Imprimir Planeación</button>
                        <button class="btn-gantt" onclick="openGanttModal()">Ver Cronograma (Gantt)</button>
                    </div>"""
content = content.replace(btn_global_search, btn_global_replace)

# 3. Add Axis Print Button
axis_btn_search = '<button class="btn-action btn-action-add" onclick="addNode(\'strategy\', ${axis.id})"><i class="fas fa-plus"></i> A\\u00f1adir Estrategia</button>'
axis_btn_replace = axis_btn_search + '\n                              <button class="btn-action btn-action-edit" onclick="imprimirElemento(\'${axisKey}\')"><i class="fas fa-print"></i> Imprimir Eje</button>'
content = content.replace(axis_btn_search, axis_btn_replace)
# Note: Since there are two renderTree functions, let's just do a string replace that catches the professional one.
# Wait, the string above has \u00f1 but the file has it literal or encoded?
# Let's use regex to be safe.
content = re.sub(r'(<button class="btn-action btn-action-add" onclick="addNode\(\'strategy\', \$\{axis\.id\}\)"><i class="fas fa-plus"></i>[^<]+</button>)',
                 r'\1\n                              <button class="btn-action btn-action-edit" onclick="imprimirElemento(\'${axisKey}\')"><i class="fas fa-print"></i> Imprimir Eje</button>',
                 content)


# 4. Add Strat Print Button
strat_btn_search = '<button class="btn-action btn-action-add" onclick="addNode(\'gen_obj\', ${st.id})"><i class="fas fa-plus"></i> Obj. General</button>'
strat_btn_replace = strat_btn_search + '\n                                <button class="btn-action btn-action-edit" onclick="imprimirElemento(\'${stKey}\')"><i class="fas fa-print"></i> Imprimir Estrategia</button>'
content = content.replace(strat_btn_search, strat_btn_replace)

# 5. Add JS functions
js_funcs = """
        function imprimirPlaneacionGlobal() {
            // Expand all first
            const closedBodies = document.querySelectorAll('.tree-container .axis-body:not(.open), .tree-container .strat-body:not(.open), .tree-container .gen-body:not(.open), .tree-container .act-body:not(.open)');
            const previouslyClosed = [];
            closedBodies.forEach(b => {
                b.classList.add('open');
                previouslyClosed.push(b);
            });
            
            setTimeout(() => {
                window.print();
                previouslyClosed.forEach(b => b.classList.remove('open'));
            }, 300);
        }

        function imprimirElemento(selectorKey) {
            const target = document.querySelector(`[data-node-key='${selectorKey}']`);
            if(!target) return;
            
            const card = target.parentElement;
            
            // add a temporary class 'print-focus-card' to the card and its parents
            card.classList.add('print-focus-card');
            let p = card.parentElement;
            while(p && p !== document.body) {
                p.classList.add('print-focus-parent');
                p = p.parentElement;
            }
            
            document.body.classList.add('print-focus-mode');
            
            // ensure all bodies inside card are open
            const closedBodies = card.querySelectorAll('.axis-body:not(.open), .strat-body:not(.open), .gen-body:not(.open), .act-body:not(.open)');
            const previouslyClosed = [];
            closedBodies.forEach(b => {
                b.classList.add('open');
                previouslyClosed.push(b);
            });
            
            // If the element itself is an axis or strategy, make sure its direct body is open
            const directBody = card.querySelector(':scope > .axis-body, :scope > .strat-body');
            if (directBody && !directBody.classList.contains('open')) {
                directBody.classList.add('open');
                previouslyClosed.push(directBody);
            }

            setTimeout(() => {
                window.print();
                document.body.classList.remove('print-focus-mode');
                card.classList.remove('print-focus-card');
                document.querySelectorAll('.print-focus-parent').forEach(el => el.classList.remove('print-focus-parent'));
                previouslyClosed.forEach(b => b.classList.remove('open'));
            }, 300);
        }
"""
content = content.replace("async function init() {", js_funcs + "\n        async function init() {")


with open(r'c:\SIAC\templates\planificacion.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Patch applied to planificacion.html")
