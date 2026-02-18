import json
import re
import unicodedata
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
import shutil
import time
import minify_html
import rjsmin
import rcssmin
from typing import Optional

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


def ascii_slug(text):
    """Genera un slug ASCII (sin acentos) a partir de `text`."""
    nfkd = unicodedata.normalize('NFKD', text)
    only_ascii = nfkd.encode('ascii', 'ignore').decode('ascii')
    s = only_ascii.lower()
    s = re.sub(r'[^\w\s-]', '', s)
    return re.sub(r'[-\s]+', '-', s).strip()


def resolve_static_media(project_slug: str, media_path: str, project_id: Optional[str] = None) -> str:
    """Resuelve una ruta de media (imagen/video) intentando, en orden:
    1) conservar `static/...` si el archivo existe,
    2) `static/img/<project_slug>/<basename>` si existe,
    3) `static/<media_path>` si existe relativo a `static/`,
    4) `static/img/<basename>` si existe,
    5) devolver la ruta original como último recurso.
    Esto permite organizar imágenes por proyecto sin romper rutas existentes.
    """
    if not media_path:
        return media_path

    # Si ya apunta a static/ y existe, mantenerla
    if media_path.startswith('static/'):
        if (BASE_DIR / media_path).exists():
            return media_path

    basename = Path(media_path).name

    # Si se pasó un project_id, comprobar primero `static/img/<id>/` (carpeta corta)
    if project_id:
        candidate_id = STATIC_SRC / 'img' / str(project_id) / basename
        if candidate_id.exists():
            return f'static/img/{project_id}/{basename}'

    # Comprueba también una versión ASCII del slug (sin acentos)
    ascii_proj = ascii_slug(project_slug)

    # 1) static/img/<project_slug>/<basename>
    candidate = STATIC_SRC / 'img' / project_slug / basename
    if candidate.exists():
        return f'static/img/{project_slug}/{basename}'

    # 1b) static/img/<ascii_project_slug>/<basename>
    candidate_ascii = STATIC_SRC / 'img' / ascii_proj / basename
    if candidate_ascii.exists():
        return f'static/img/{ascii_proj}/{basename}'

    # 2) static/<media_path> (si media_path era relativo dentro de static)
    candidate2 = STATIC_SRC / Path(media_path)
    if candidate2.exists():
        return f'static/{Path(media_path).as_posix()}'

    # 3) static/img/<basename>
    candidate3 = STATIC_SRC / 'img' / basename
    if candidate3.exists():
        return f'static/img/{basename}'

    # Fallback: devolver la ruta original (puede ser URL externa u otra ruta)
    return media_path


def validate_and_normalize_project(project: dict, lang_code: str):
    """Validaciones sencillas y normalizaciones sobre cada proyecto.
    Añade `slug` si falta, advierte si faltan campos importantes y devuelve el objeto.
    """
    # title es obligatorio
    if not project.get('title'):
        print(f"⚠ Missing title for project (lang={lang_code}): {project}")

    # id recomendado
    if 'id' not in project:
        print(f"⚠ Project missing 'id' (lang={lang_code}, title={project.get('title')}). Consider adding a stable numeric id.")

    # slug
    if not project.get('slug'):
        if project.get('title'):
            project['slug'] = slugify(project['title'])
            print(f"→ Auto-generated slug for '{project.get('title')}': {project['slug']}")
        else:
            project['slug'] = 'untitled'

    # summary
    if not project.get('summary'):
        print(f"⚠ Project '{project.get('title')}' has no 'summary' (lang={lang_code}). Add a 1-line TL;DR.")

    # Ensure images is a list
    if 'images' not in project or not isinstance(project.get('images'), list):
        project['images'] = []

    # Ensure tech is a list
    if 'tech' in project and not isinstance(project.get('tech'), list):
        project['tech'] = [project.get('tech')]

    return project

# =========================
# Prepare dist/
# =========================
if DIST_DIR.exists():
    shutil.rmtree(DIST_DIR)
DIST_DIR.mkdir(exist_ok=True)
projects_dir = DIST_DIR / 'projects'
projects_dir.mkdir(parents=True, exist_ok=True)

# Collect a lightweight index for client-side search/filters
index_list = []

# =========================
# 1. Render Project Detail Pages
# =========================
template_project = env.get_template('project.html')

for lang_code, content in portfolio_data['languages'].items():
    for project in content['projects']:
        # Validate and normalize
        project = validate_and_normalize_project(project, lang_code)

        project_slug = project.get('slug') or slugify(project.get('title', 'untitled'))
        filename = f"{project_slug}-{lang_code}.html"
        
        # Inyectamos la URL en el objeto para que el Index sepa a dónde linkear
        project['detail_url'] = filename 

        # Resolver rutas de imágenes y videos: permitir `static/img/<project_slug>/...`
        # obtener project id si existe
        project_id = project.get('id')

        for img in project.get('images', []):
            if isinstance(img, dict) and img.get('img_path'):
                img['img_path'] = resolve_static_media(project_slug, img.get('img_path'), project_id)

        if project.get('video_url'):
            project['video_url'] = resolve_static_media(project_slug, project.get('video_url'), project_id)

        # Build a flattened keywords list from `tech` or from `tech_stack` values
        keywords = []
        if isinstance(project.get('tech'), list) and project.get('tech'):
            keywords.extend(project.get('tech'))
        ts = project.get('tech_stack') or {}
        if isinstance(ts, dict):
            for k, v in ts.items():
                if isinstance(v, list):
                    keywords.extend(v)
        # dedupe while preserving order
        seen = set()
        dedup = []
        for k in keywords:
            if k not in seen:
                seen.add(k)
                dedup.append(k)
        project['keywords'] = dedup

        project_html = template_project.render(
            project_data=project,
            data=portfolio_data,
            current_lang=lang_code
        )

        # Minify HTML but avoid removing processing instructions which some
        # validators rely on. This keeps files compact while preserving meta tags.
        try:
            min_project_html = minify_html.minify(
                project_html,
                minify_js=True,
                minify_css=True,
                remove_processing_instructions=False
            )
        except Exception:
            # If minifier fails for any reason, fall back to unminified HTML
            min_project_html = project_html

        (DIST_DIR / filename).write_text(min_project_html, encoding='utf-8')
        print(f'✔ Generated Project Detail: {filename}')

        # Export per-project JSON for client-side fetching
        try:
            pjson_path = projects_dir / f"{project_slug}-{lang_code}.json"
            pjson_path.write_text(json.dumps(project, ensure_ascii=False, indent=2), encoding='utf-8')
        except Exception as e:
            print(f"⚠ Failed to write project JSON for {project_slug}-{lang_code}: {e}")

        # Add to index list (lightweight)
        # produce a slightly richer index entry so the frontpage can show role/impact/preview
        index_entry = {
            'id': project.get('id'),
            'slug': project_slug,
            'title': project.get('title'),
            'summary': project.get('summary', ''),
            'short_summary': project.get('short_summary', ''),
            'role': project.get('role', []),
            'impact': project.get('impact', ''),
            'metrics': project.get('metrics', {}),
            'tech': project.get('tech', []) or project.get('tech_stack', {}),
            'detail_url': project.get('detail_url'),
            'repo_url': project.get('repo_url') or project.get('url'),
            'demo_url': project.get('demo_url', ''),
            'preview_image': (project.get('images') and project.get('images')[0] and project.get('images')[0].get('img_path')) or None,
            'categories': project.get('categories', []),
            'published': project.get('published', True),
            'lang': lang_code,
            'featured': project.get('featured', False),
            'weight': project.get('weight', 0)
        }
        index_list.append(index_entry)

# =========================
# 2. Render Main Index
# =========================
template_index = env.get_template('index.html')
index_html = template_index.render(
    title=f"Portfolio | {portfolio_data['languages']['es']['name']}",
    data=portfolio_data
)

(DIST_DIR / 'index.html').write_text(
    minify_html.minify(index_html, minify_js=True, minify_css=True, remove_processing_instructions=False),
    encoding='utf-8'
)
print(f'✔ Rendered index.html')
try:
    (DIST_DIR / 'index.json').write_text(json.dumps(index_list, ensure_ascii=False, indent=2), encoding='utf-8')
    print('✔ Wrote index.json')
except Exception as e:
    print(f"⚠ Failed to write index.json: {e}")

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