from jinja2 import Environment, FileSystemLoader
from pathlib import Path
import shutil
import time

# =========================
# Paths
# =========================
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / 'templates'
STATIC_SRC = BASE_DIR / 'static'
DIST_DIR = BASE_DIR / 'dist'
STATIC_DST = DIST_DIR / 'static'

# =========================
# Jinja environment
# =========================
env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=True,
)

# =========================
# Static helper (web path)
# =========================
BUILD_TS = int(time.time())

def static(path: str) -> str:
    return f'/static/{path}?v={BUILD_TS}'

env.globals['static'] = static

# =========================
# Templates to render
# output_name -> context
# =========================
templates = {
    'index.html': {
        'title': 'Resume',
        'link': 'https://google.com',
    },
    # ejemplo extra:
    # 'about.html': {'title': 'About'},
}

# =========================
# Prepare dist/
# =========================
DIST_DIR.mkdir(exist_ok=True)

# =========================
# Render templates
# =========================
for output_name, context in templates.items():
    template = env.get_template(output_name)
    html = template.render(**context)
    out_path = DIST_DIR / output_name
    out_path.write_text(html, encoding='utf-8')
    print(f'✔ Rendered {out_path}')

# =========================
# Collect static files
# =========================
if STATIC_DST.exists():
    shutil.rmtree(STATIC_DST)

shutil.copytree(STATIC_SRC, STATIC_DST)
print(f'✔ Static files copied to {STATIC_DST}')

print('\n✅ Build completed successfully')