document.addEventListener('DOMContentLoaded', () => {
    const dataElement = document.getElementById('project-data');
    if (!dataElement) return;
    const project = JSON.parse(dataElement.textContent);

    // Obtener etiquetas localizadas desde el `site-data` inyectado por Jinja
    let siteData = {};
    try {
        const siteEl = document.getElementById('site-data');
        siteData = siteEl ? JSON.parse(siteEl.textContent) : {};
    } catch (e) {
        siteData = {};
    }
    const currentLang = window.currentLang || (siteData.config && siteData.config.default_language) || 'es';
    const labels = (siteData.tags && siteData.tags[currentLang]) || {};

    document.getElementById('p-title').textContent = project.title;
    const pCategoryEl = document.getElementById('p-category');
    if (pCategoryEl) {
        const cats = project.categories || [];
        const textColorForBg = (hex) => {
            try {
                const c = (hex || '#777').replace('#','');
                const r = parseInt(c.substr(0,2),16);
                const g = parseInt(c.substr(2,2),16);
                const b = parseInt(c.substr(4,2),16);
                const yiq = (r*299 + g*587 + b*114) / 1000;
                return (yiq >= 128) ? '#000000' : '#FFFFFF';
            } catch (e) { return '#FFFFFF'; }
        };
        const resolvedHtml = (cats || []).map(k => {
            try {
                const meta = (siteData.categories_map && siteData.categories_map[k]) || null;
                const label = (meta && meta[currentLang]) || k;
                const bg = (meta && meta.color) || '#777777';
                const txt = textColorForBg(bg);
                return `<span class="tag" style="background-color:${bg}; color:${txt};">${label}</span>`;
            } catch (e) { return `<span class="tag">${k}</span>`; }
        }).join(' ');
        pCategoryEl.innerHTML = resolvedHtml;
    }
    document.getElementById('p-summary').textContent = project.summary;
    document.getElementById('p-repo').href = project.url || '#';

    // Localizar texto del título de especificaciones si existe (renderizado por Jinja también)
    const techTitleEl = document.getElementById('p-tech-title');
    if (techTitleEl && labels.technical_specifications) techTitleEl.textContent = labels.technical_specifications;

    // Galería de imágenes grandes
    const gallery = document.getElementById('p-gallery');
        if (gallery && project.images) {
        gallery.innerHTML = project.images.map(img => `
            <figure class="detail-item">
                <img src="${img.img_path}" alt="${img.caption}" class="img-expanded">
                <figcaption class="media-overlay">${img.caption}</figcaption>
            </figure>
        `).join('');
    }

    // Highlights y Tech Stack
    document.getElementById('p-highlights').innerHTML = (project.highlights || []).map(h => `<li>${h}</li>`).join('');
    const ts = project.tech_stack || {};
    const stackHtml = Object.entries(ts).map(([k, v]) => {
        const techKeys = siteData.tags && siteData.tags[currentLang] && siteData.tags[currentLang].tech_stack && siteData.tags[currentLang].tech_stack.keys;
        const labelFromTech = techKeys && techKeys[k];
        const rawLabel = (labels && labels[k]) || null;
        const label = labelFromTech || rawLabel || k.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
        const value = Array.isArray(v) ? v.join(' + ') : v;
        return `<div class="spec-item"><strong>${label}:</strong> ${value || 'N/A'}</div>`;
    }).join('');
    document.getElementById('p-stack').innerHTML = stackHtml || '<div class="spec-item">N/A</div>';
});