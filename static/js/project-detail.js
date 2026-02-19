document.addEventListener('DOMContentLoaded', () => {
    // Prefer inline `#project-data` JSON (embedded at build time). Fall back to fetching `window.projectJsonUrl`.
    const projectDataEl = document.getElementById('project-data');
    if (projectDataEl && projectDataEl.textContent && projectDataEl.textContent.trim().length > 0) {
        try {
            const project = JSON.parse(projectDataEl.textContent);
            renderProject(project);
        } catch (e) {
            console.error('Failed to parse inline project-data JSON:', e);
        }
        return;
    }

    const jsonUrl = window.projectJsonUrl;
    if (!jsonUrl) return;

    fetch(jsonUrl).then(r => {
        if (!r.ok) throw new Error('Failed to load project JSON: ' + r.status);
        return r.json();
    }).then(project => {
        renderProject(project);
    }).catch(err => {
        console.error(err);
    });

    function renderProject(project) {
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
        document.getElementById('p-repo').href = project.repo_url || project.url || '#';

        // Role and date
        const roleEl = document.getElementById('p-role');
        if (roleEl) {
            const r = project.role || project.roles || [];
            roleEl.textContent = Array.isArray(r) ? r.join(' · ') : (r || '');
            roleEl.style.display = r && (Array.isArray(r) ? r.length > 0 : true) ? '' : 'none';
        }
        const dateEl = document.getElementById('p-date');
        if (dateEl) {
            dateEl.textContent = project.date || '';
            dateEl.style.display = project.date ? '' : 'none';
        }

        // Problem / Solution / Impact
        const problemEl = document.getElementById('p-problem-text');
        if (problemEl) problemEl.textContent = project.problem || '';
        const solutionEl = document.getElementById('p-solution-text');
        if (solutionEl) solutionEl.textContent = project.solution || '';
        const impactEl = document.getElementById('p-impact-text');
        if (impactEl) impactEl.textContent = project.impact || '';

        // Localizar texto del título de especificaciones si existe (renderizado por Jinja también)
        const techTitleEl = document.getElementById('p-tech-title');
        if (techTitleEl && labels.technical_specifications) techTitleEl.textContent = labels.technical_specifications;

    // Galería de imágenes grandes + presentación (video o imagen)
    const gallery = document.getElementById('p-gallery');
    if (gallery) {
        const isVideoUrl = (u) => !!(u && /\.(mp4|webm|ogg)(\?|$)/i.test(u));
        const isImageUrl = (u) => !!(u && /\.(jpe?g|png|gif|webp|svg)(\?|$)/i.test(u));

        const placeholderSvg = '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="675"><rect width="100%" height="100%" fill="#f3f4f6"/><text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="#9ca3af" font-family="Arial, sans-serif" font-size="36">No media available</text></svg>';
        const placeholder = 'data:image/svg+xml;utf8,' + encodeURIComponent(placeholderSvg);

        const items = [];

        // presentación: puede ser video o imagen vía `project.video_url`
        if (project.video_url) {
            if (isVideoUrl(project.video_url)) {
                items.push(`<figure class="detail-item"><video src="${project.video_url}" controls class="img-expanded" onerror="this.outerHTML='<img src=\"${placeholder}\" class=\"img-expanded\"/>'"></video><figcaption class="media-overlay">${project.title}</figcaption></figure>`);
            } else if (isImageUrl(project.video_url)) {
                items.push(`<figure class="detail-item"><img src="${project.video_url}" alt="${project.title}" class="img-expanded" onerror="this.onerror=null;this.src='${placeholder}';"><figcaption class="media-overlay">${project.title}</figcaption></figure>`);
            }
        }

        // resto de imágenes
        if (Array.isArray(project.images)) {
            project.images.forEach(img => {
                if (img && img.img_path) {
                    const caption = img.caption || project.title || '';
                    items.push(`<figure class="detail-item"><img src="${img.img_path}" alt="${caption}" class="img-expanded" onerror="this.onerror=null;this.src='${placeholder}';"><figcaption class="media-overlay">${caption}</figcaption></figure>`);
                }
            });
        }

        // Si no hay items válidos, renderizar placeholder
        if (items.length === 0) {
            items.push(`<figure class="detail-item"><img src="${placeholder}" alt="No media" class="img-expanded"><figcaption class="media-overlay">${project.title}</figcaption></figure>`);
        }

        gallery.innerHTML = items.join('');
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

        // Metrics (key: value) — render under tech specs if present
        const metricsEl = document.getElementById('p-metrics');
        if (metricsEl) {
            const metrics = project.metrics || {};
            const metricsEntries = Object.entries(metrics || {});
            if (metricsEntries.length > 0) {
                const metricsHtml = metricsEntries.map(([k,v]) => {
                    const label = k.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
                    return `<div class="metric-item"><strong>${label}:</strong> ${v}</div>`;
                }).join('');
                metricsEl.innerHTML = `<h4>${labels.metrics || 'Metrics'}</h4>${metricsHtml}`;
            } else {
                metricsEl.innerHTML = '';
            }
        }

        // Demo link and case study
        const demoEl = document.getElementById('p-demo');
        if (demoEl) {
            if (project.demo_url) { demoEl.href = project.demo_url; demoEl.style.display = ''; }
            else { demoEl.style.display = 'none'; }
        }
        const caseEl = document.getElementById('p-case');
        if (caseEl) {
            if (project.case_study_pdf) { caseEl.href = project.case_study_pdf; caseEl.style.display = ''; }
            else { caseEl.style.display = 'none'; }
        }

        // Architecture (image or inline SVG)
        const archEl = document.getElementById('p-architecture');
        if (archEl) {
            archEl.innerHTML = '';
            const arch = project.architecture || '';
            if (arch) {
                if (/\.(svg)(\?|$)/i.test(arch)) {
                    // inline the svg if local file exists by using an <img> (no fetch here)
                    archEl.innerHTML = `<img src="${arch}" alt="Architecture diagram" class="architecture-img">`;
                } else {
                    archEl.innerHTML = `<img src="${arch}" alt="Architecture diagram" class="architecture-img">`;
                }
            }
        }
    }
});