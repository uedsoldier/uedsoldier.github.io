import json
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
import shutil
import time
import minify_html
import rjsmin
import rcssmin

# =========================
# Paths
# =========================
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / 'templates'
STATIC_SRC = BASE_DIR / 'static'
DIST_DIR = BASE_DIR / 'dist'
STATIC_DST = DIST_DIR / 'static'
DATA_FILE = BASE_DIR / 'data' / 'portfolio.json'

# Load data
with open(DATA_FILE, 'r', encoding='utf-8') as f:
    portfolio_data = json.load(f)

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
# =========================
templates = {
    'index.html': {
        'title': f"Portfolio | {portfolio_data['languages']['es']['name']}",
        'data': portfolio_data,
    },
}

# =========================
# Prepare dist/
# =========================
if DIST_DIR.exists():
    shutil.rmtree(DIST_DIR)
DIST_DIR.mkdir(exist_ok=True)

# =========================
# Render & Minify HTML
# =========================
for output_name, context in templates.items():
    template = env.get_template(output_name)
    html_content = template.render(**context)
    
    minified_html = minify_html.minify(
        html_content,
        minify_js=True,
        minify_css=True,
        remove_processing_instructions=True
    )
    
    out_path = DIST_DIR / output_name
    out_path.write_text(minified_html, encoding='utf-8')
    print(f'✔ Rendered and Minified {out_path}')

# =========================
# Collect & Minify Static Files
# =========================
# Reemplazamos shutil.copytree por un proceso selectivo
STATIC_DST.mkdir(parents=True, exist_ok=True)

for file_path in STATIC_SRC.rglob('*'):
    if file_path.is_file():
        # Calculamos la ruta de destino manteniendo la estructura
        relative_path = file_path.relative_to(STATIC_SRC)
        target_path = STATIC_DST / relative_path
        target_path.parent.mkdir(parents=True, exist_ok=True)

        if file_path.suffix == '.js':
            # Minificación de JavaScript
            js_content = file_path.read_text(encoding='utf-8')
            target_path.write_text(rjsmin.jsmin(js_content), encoding='utf-8')
            print(f'✔ Minified JS: {relative_path}')
            
        elif file_path.suffix == '.css':
            # Minificación de CSS
            css_content = file_path.read_text(encoding='utf-8')
            target_path.write_text(rcssmin.cssmin(css_content), encoding='utf-8')
            print(f'✔ Minified CSS: {relative_path}')
            
        else:
            # Otros archivos (SVG, imágenes, etc.) se copian tal cual
            shutil.copy2(file_path, target_path)
            print(f'✔ Copied: {relative_path}')

print('\n✅ Build completed successfully with full minification')