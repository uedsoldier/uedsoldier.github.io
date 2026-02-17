import json
import re
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
TAGS_FILE = BASE_DIR / 'data' / 'tags.json'
CATEGORIES_FILE = BASE_DIR / 'data' / 'categories.json'

# Load data
with open(DATA_FILE, 'r', encoding='utf-8') as f:
    portfolio_data = json.load(f)

# Load tags/translations for generic labels
with open(TAGS_FILE, 'r', encoding='utf-8') as f:
    tags_data = json.load(f)

# Load categories mapping
with open(CATEGORIES_FILE, 'r', encoding='utf-8') as f:
    categories_data = json.load(f)

# Inject tags into portfolio_data so templates and client JS can access them
portfolio_data['tags'] = tags_data
portfolio_data['categories_map'] = categories_data

# =========================
# Jinja environment
# =========================
env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=True,
)

BUILD_TS = int(time.time())
def static(path: str) -> str:
    # Ruta relativa para GitHub Pages
    return f'static/{path}?v={BUILD_TS}'

env.globals['static'] = static
env.globals['tags'] = tags_data
env.globals['categories_map'] = categories_data

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    return re.sub(r'[-\s]+', '-', text).strip()

# =========================
# Prepare dist/
# =========================
if DIST_DIR.exists():
    shutil.rmtree(DIST_DIR)
DIST_DIR.mkdir(exist_ok=True)

# =========================
# 1. Render Project Detail Pages
# =========================
template_project = env.get_template('project.html')

for lang_code, content in portfolio_data['languages'].items():
    for project in content['projects']:
        project_slug = slugify(project['title'])
        filename = f"{project_slug}-{lang_code}.html"
        
        # Inyectamos la URL en el objeto para que el Index sepa a dónde linkear
        project['detail_url'] = filename 

        project_html = template_project.render(
            project_data=project,
            data=portfolio_data,
            current_lang=lang_code
        )

        min_project_html = minify_html.minify(
            project_html, minify_js=True, minify_css=True, remove_processing_instructions=True
        )
        
        (DIST_DIR / filename).write_text(min_project_html, encoding='utf-8')
        print(f'✔ Generated Project Detail: {filename}')

# =========================
# 2. Render Main Index
# =========================
template_index = env.get_template('index.html')
index_html = template_index.render(
    title=f"Portfolio | {portfolio_data['languages']['es']['name']}",
    data=portfolio_data
)

min_index_html = minify_html.minify(
    index_html, minify_js=True, minify_css=True, remove_processing_instructions=True
)

(DIST_DIR / 'index.html').write_text(min_index_html, encoding='utf-8')
print(f'✔ Rendered index.html')

# =========================
# 3. Static Files
# =========================
STATIC_DST.mkdir(parents=True, exist_ok=True)
for file_path in STATIC_SRC.rglob('*'):
    if file_path.is_file():
        relative_path = file_path.relative_to(STATIC_SRC)
        target_path = STATIC_DST / relative_path
        target_path.parent.mkdir(parents=True, exist_ok=True)

        if file_path.suffix == '.js':
            js_content = file_path.read_text(encoding='utf-8')
            target_path.write_text(rjsmin.jsmin(js_content), encoding='utf-8')
        elif file_path.suffix == '.css':
            css_content = file_path.read_text(encoding='utf-8')
            target_path.write_text(rcssmin.cssmin(css_content), encoding='utf-8')
        else:
            shutil.copy2(file_path, target_path)

print('\n✅ Build completed successfully.')