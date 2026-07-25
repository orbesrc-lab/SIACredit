css_addition = """

/* ===== LIGHT THEME (SKEL GLOBAL) ===== */
body.light-theme {
  --dark: #f8fafc;           /* Fondo principal blanco/gris muy claro */
  --dark2: #ffffff;          /* Fondo alterno blanco */
  --dark3: #f1f5f9;          /* Tarjetas gris claro */
  --white: #0f172a;          /* Texto principal oscuro */
  --muted: #475569;          /* Texto secundario gris oscuro */
  --border: rgba(37,99,235,0.15);
  --border-glow: rgba(37,99,235,0.25);
}

/* Ajustes específicos para Light Theme */
body.light-theme .navbar {
  background: rgba(255, 255, 255, 0.96);
  border-bottom: 1px solid var(--border);
}

body.light-theme .nav-links a {
  color: #334155;
}
body.light-theme .nav-links a:hover {
  color: var(--accent);
}

body.light-theme .nav-logo {
  color: #0f172a;
}

body.light-theme .hero-bg {
  /* Hacemos que el hero tenga una superposición más clara si usan la imagen de fondo */
  opacity: 0.1;
}
body.light-theme .hero-overlay {
  background: linear-gradient(to bottom, rgba(248,250,252,0.6) 0%, rgba(248,250,252,1) 100%);
}

body.light-theme .stat-card, body.light-theme .service-card, body.light-theme .module-card, body.light-theme .review-card {
  box-shadow: 0 4px 15px rgba(0,0,0,0.05);
}

body.light-theme .btn-outline {
  color: var(--accent);
  border-color: var(--accent);
}

body.light-theme .accordion-header {
  background: #ffffff;
}

body.light-theme .footer {
  background: #ffffff;
  border-top: 1px solid var(--border);
}
"""

with open(r"c:\SIAC\static\landing.css", "a", encoding="utf-8") as f:
    f.write(css_addition)

print("Light theme appended successfully.")
