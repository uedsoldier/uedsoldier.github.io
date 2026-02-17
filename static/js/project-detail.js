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
    document.getElementById('p-category').textContent = project.category;
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
    const hwLabel = labels.hw || 'HW';
    const fwLabel = labels.fw || 'FW';
    const busLabel = labels.bus || 'BUS';
    const hwStr = (ts.hardware && ts.hardware.length) ? ts.hardware.join(' + ') : 'N/A';
    const fwStr = (ts.firmware && ts.firmware.length) ? ts.firmware.join(', ') : 'N/A';
    const busStr = (ts.protocols && ts.protocols.length) ? ts.protocols.join(' | ') : 'N/A';
    document.getElementById('p-stack').innerHTML = `
        <div class="spec-item"><strong>${hwLabel}:</strong> ${hwStr}</div>
        <div class="spec-item"><strong>${fwLabel}:</strong> ${fwStr}</div>
        <div class="spec-item"><strong>${busLabel}:</strong> ${busStr}</div>
    `;
});