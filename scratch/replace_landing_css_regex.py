import os

path = r"c:\SIAC\static\landing.css"

with open(path, "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

# Normalize line endings
content_norm = content.replace("\r\n", "\n")

# Find the start of mobile-menu-overlay and the start of .hero
idx_start = content_norm.find(".mobile-menu-overlay {")
idx_end = content_norm.find(".hero {", idx_start)

if idx_start != -1 and idx_end != -1:
    print(f"Indices found: Start={idx_start}, End={idx_end}")
    
    # We want to replace from idx_start to idx_end
    # The replacement is our new mobile-menu-overlay and mobile styles for nav-links/nav-cta,
    # plus the .hamburger media query display if needed
    
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
.nav-cta .btn-gold { background: linear-gradient(135deg, var(--accent), var(--accent-deep)); color: #fff; width: 90%; max-width: 320px; margin: 0 auto; padding: 14px; font-size: 1.1rem; border-radius: 30px; text-align: center; box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3); border: none; }
.hamburger { display: block; }
.hamburger.active svg line:nth-child(1) { transform: translateY(6px) rotate(45deg); transform-origin: center; }
.hamburger.active svg line:nth-child(2) { opacity: 0; }
.hamburger.active svg line:nth-child(3) { transform: translateY(-6px) rotate(-45deg); transform-origin: center; }
"""
    new_content = content_norm[:idx_start] + replacement + content_norm[idx_end:]
    
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("SUCCESS: landing.css mobile overlay menu written successfully!")
else:
    print(f"ERROR: Could not find indices. Start={idx_start}, End={idx_end}")
