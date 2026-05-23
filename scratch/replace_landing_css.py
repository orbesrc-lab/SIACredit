import os

path = r"c:\SIAC\static\landing.css"

with open(path, "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

target = """.mobile-menu-overlay {
position: fixed; inset: 0; background: rgba(0,0,0,0.75);
backdrop-filter: blur(4px); z-index: 1000;
opacity: 0; pointer-events: none; transition: opacity 0.3s;
}
.mobile-menu-overlay.active { opacity: 1; pointer-events: auto; }

@media (max-width: 768px) {
.nav-inner { padding: 0 20px; }
.nav-links {
position: fixed; top: 0; right: -100%; width: 80%; height: 100vh;
background: var(--dark2); border-left: 1px solid var(--border);
flex-direction: column; padding: 100px 40px; gap: 30px;
transition: right 0.4s cubic-bezier(0.4, 0, 0.2, 1);
z-index: 1050; box-shadow: -10px 0 30px rgba(0,0,0,0.5);
}
.nav-links.active { right: 0; }
.nav-links a { font-size: 1.2rem; }
.nav-cta {
position: fixed; bottom: 0; right: -100%; width: 80%;
padding: 30px 40px; background: var(--dark2);
border-top: 1px solid var(--border);
flex-direction: column; gap: 15px;
transition: right 0.4s cubic-bezier(0.4, 0, 0.2, 1);
z-index: 1050;
}
.nav-cta.active { right: 0; }
.nav-cta .btn-outline, .nav-cta .btn-gold { width: 100%; text-align: center; }"""

replacement = """.mobile-menu-overlay {
position: fixed; inset: 0; background: rgba(0,0,0,0.65);
backdrop-filter: blur(8px); z-index: 1000;
opacity: 0; pointer-events: none; transition: opacity 0.3s;
}
.mobile-menu-overlay.active { opacity: 1; pointer-events: auto; }

@media (max-width: 768px) {
.nav-inner { padding: 0 20px; }
.nav-links {
position: fixed; top: 0; right: -100%; width: 100%; height: 100vh;
background: rgba(2, 8, 24, 0.98); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
flex-direction: column; justify-content: center; align-items: center; padding: 40px; gap: 25px;
transition: right 0.45s cubic-bezier(0.16, 1, 0.3, 1);
z-index: 1050;
}
.nav-links.active { right: 0; }
.nav-links a { font-size: 1.5rem; font-weight: 600; color: var(--white); transition: all 0.3s ease; }
.nav-links a:hover { color: var(--accent-light); transform: scale(1.05); }
.nav-cta {
position: fixed; bottom: -100%; left: 0; width: 100%;
padding: 30px 40px; background: transparent; border-top: none;
display: flex; flex-direction: column; gap: 15px;
transition: bottom 0.45s cubic-bezier(0.16, 1, 0.3, 1);
z-index: 1060;
}
.nav-cta.active { bottom: 30px; right: 0; }
.nav-cta .btn-outline { border-color: var(--accent-light); color: var(--white); background: rgba(37, 99, 235, 0.1); width: 90%; max-width: 320px; margin: 0 auto; padding: 14px; font-size: 1.1rem; border-radius: 30px; text-align: center; }
.nav-cta .btn-gold { background: linear-gradient(135deg, var(--accent), var(--accent-deep)); color: #fff; width: 90%; max-width: 320px; margin: 0 auto; padding: 14px; font-size: 1.1rem; border-radius: 30px; text-align: center; box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3); border: none; }"""

# Clean line endings to ensure perfect match
clean_content = content.replace("\r\n", "\n")
clean_target = target.replace("\r\n", "\n")
clean_replacement = replacement.replace("\r\n", "\n")

if clean_target in clean_content:
    new_content = clean_content.replace(clean_target, clean_replacement)
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("SUCCESS: landing.css updated successfully!")
else:
    # Try fuzzy match or character cleanups
    print("ERROR: Target string not found exactly. Checking spacing...")
    # Let's do a more robust substring matching or display a diagnostic.
    print(f"Content length: {len(clean_content)}")
    print(f"Target length: {len(clean_target)}")
