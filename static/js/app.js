document.addEventListener('DOMContentLoaded', () => {
    // 1. Obtener los datos del "Sensor" (El script JSON inyectado por Jinja)
    const dataElement = document.getElementById('site-data');
    if (!dataElement) return;

    const siteData = JSON.parse(dataElement.textContent);

    // 2. Definir el Estado Inicial
    let currentLang = siteData.config.default_language || siteData.config.default_lang || 'es';

    // 3. Referencias a los Nodos del DOM (Actuadores)
    const ui = {
        name: document.getElementById('ui-name'),
        label: document.getElementById('ui-label'),
        navProjects: document.getElementById('nav-projects'),
        navSkills: document.getElementById('nav-skills'),
        navEducation: document.getElementById('nav-education'),
        projectsTitle: document.getElementById('ui-projects-title'),
        projectsGrid: document.getElementById('projects'),
        skillsTitle: document.getElementById('ui-skills-title'),
        skillsDisplay: document.getElementById('skills-display'),
        educationTitle: document.getElementById('ui-education-title'),
        educationDisplay: document.getElementById('education-display'),
        langBtn: document.getElementById('lang-btn'),
        langLabel: document.getElementById('lang-label')
    };

    // Estado de filtros: categorías seleccionadas (keys)
    const selectedCategories = new Set();

    // Sección actualmente activa (projects | skills | education)
    let currentSection = 'projects';

    // Renderiza el listado de filtros de categoría dentro de la sidebar
    const renderCategoryFilters = (lang) => {
        const container = document.getElementById('category-filters');
        if (!container) return;
        const categoriesMap = siteData.categories_map || {};
        const keys = Object.keys(categoriesMap || {});
        if (keys.length === 0) {
            container.innerHTML = '';
            return;
        }

        // sort keys by localized label for stable order
        keys.sort((a,b) => {
            const la = (categoriesMap[a] && categoriesMap[a][lang]) || a;
            const lb = (categoriesMap[b] && categoriesMap[b][lang]) || b;
            try { return la.localeCompare(lb, lang); } catch (e) { return String(la).localeCompare(String(lb)); }
        });

        // helper: convert hex to rgb object
        const hexToRgb = (hex) => {
            if (!hex) return {r:119,g:119,b:119};
            let h = String(hex).replace('#','').trim();
            if (h.length === 3) h = h.split('').map(ch => ch+ch).join('');
            if (h.length !== 6) return {r:119,g:119,b:119};
            const r = parseInt(h.substr(0,2),16);
            const g = parseInt(h.substr(2,2),16);
            const b = parseInt(h.substr(4,2),16);
            return {r,g,b};
        };

        const items = keys.map(k => {
            const meta = categoriesMap[k] || {};
            const label = (meta && meta[lang]) || k;
            const hex = (meta && meta.color) || '#777777';
            const rgb = hexToRgb(hex);
            // translucent background and soft border for less aggressive look
            const bgRgba = `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, 0.10)`;
            const borderRgba = `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, 0.22)`;
            // use consistent app foreground color for label text to match theme
            const checked = selectedCategories.has(k) ? 'checked' : '';
            const style = `background-color:${bgRgba}; border:1px solid ${borderRgba}; color:var(--text-main);`;
            return `<li class="cat-filter-item"><label class="cat-filter" style="${style}"><input type="checkbox" data-cat="${k}" ${checked}> ${label}</label></li>`;
        });

        const titleLabel = (siteData.tags && siteData.tags[lang] && siteData.tags[lang].filters) || 'Filters';
        const clearLabel = (siteData.tags && siteData.tags[lang] && siteData.tags[lang].clear) || 'Clear';
        container.innerHTML = `<div class="filters-title">${titleLabel}</div><ul class="filters-list">${items.join('')}</ul><button id="clear-cat-filters" class="btn-small">${clearLabel}</button>`;

        // wire events and toggle selected class
        container.querySelectorAll('input[data-cat]').forEach(inp => {
            const labelEl = inp.closest('.cat-filter');
            if (labelEl) labelEl.classList.toggle('selected', inp.checked);
            inp.addEventListener('change', (e) => {
                const key = inp.getAttribute('data-cat');
                if (!key) return;
                if (inp.checked) {
                    selectedCategories.add(key);
                    if (labelEl) labelEl.classList.add('selected');
                } else {
                    selectedCategories.delete(key);
                    if (labelEl) labelEl.classList.remove('selected');
                }
                // re-render UI with filters applied
                updateUI(currentLang);
            });
        });
        const clearBtn = container.querySelector('#clear-cat-filters');
        if (clearBtn) clearBtn.addEventListener('click', () => { selectedCategories.clear(); renderCategoryFilters(currentLang); updateUI(currentLang); });
    };

    // 4. Función de Renderizado (Actualización del Sistema)
    const updateUI = (lang) => {
        
        // Aplicar clase de animación
        const container = document.querySelector('.data-view');
        if (container) {
            container.classList.remove('fade-in-effect');
            void container.offsetWidth; // "Reset" de la animación (Reflow)
            container.classList.add('fade-in-effect');
        }
        const content = siteData.languages[lang];
        // Helper: pick readable text color (black/white) for a given hex background
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
        if (!content) return; // Protección si el idioma no existe
        console.log("Proyectos encontrados:", content.projects);
        // Uso de Optional Chaining (?.) para evitar que el script truene si falta un ID
        if (ui.name) ui.name.textContent = content.name;
        if (ui.label) ui.label.textContent = content.label;
        if (ui.navProjects) ui.navProjects.textContent = content.nav.projects;
        if (ui.projectsTitle) ui.projectsTitle.textContent = content.nav.projects;
        if (ui.navSkills) ui.navSkills.textContent = content.nav.skills;
        if (ui.skillsTitle) ui.skillsTitle.textContent = content.nav.skills;
        if (ui.navEducation) ui.navEducation.textContent = content.nav.education || '';
        if (ui.educationTitle) ui.educationTitle.textContent = content.nav.education || '';
        if (ui.langLabel) ui.langLabel.textContent = (lang === 'es') ? 'EN' : 'ES';

        // Show/hide entire section containers depending on the active section
        const projectsSectionEl = document.getElementById('projects-section');
        const skillsSectionEl = document.getElementById('skills');
        const educationSectionEl = document.getElementById('education');
        if (projectsSectionEl) projectsSectionEl.style.display = (currentSection === 'projects') ? '' : 'none';
        if (skillsSectionEl) skillsSectionEl.style.display = (currentSection === 'skills') ? '' : 'none';
        if (educationSectionEl) educationSectionEl.style.display = (currentSection === 'education') ? '' : 'none';

        // Helper: detectar tipo de media por extensión
        const isVideoUrl = (u) => !!(u && /\.(mp4|webm|ogg)(\?|$)/i.test(u));
        const isImageUrl = (u) => !!(u && /\.(jpe?g|png|gif|webp|svg)(\?|$)/i.test(u));
        const placeholderSvg = '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="675"><rect width="100%" height="100%" fill="#f3f4f6"/><text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="#9ca3af" font-family="Arial, sans-serif" font-size="36">No media available</text></svg>';
        const placeholder = 'data:image/svg+xml;utf8,' + encodeURIComponent(placeholderSvg);

        // Renderizado de Proyectos con validación
        const detailsLabel = (siteData.tags && siteData.tags[lang] && siteData.tags[lang].view_details) || ((lang === 'es') ? 'Ver Detalles Técnicos' : 'View Technical Details');

        // Prepare filtered projects based on selectedCategories
        const allProjects = Array.isArray(content.projects) ? content.projects : [];
        const filteredProjects = (selectedCategories.size === 0) ? allProjects : allProjects.filter(p => {
            const cats = p.categories || [];
            return cats.some(c => selectedCategories.has(c));
        });

        // render category filters (localized) only when showing projects
        if (currentSection === 'projects') renderCategoryFilters(lang);

        if (currentSection === 'projects') {
            if (ui.projectsGrid) {
                const cardsHtml = filteredProjects.map(proj => {
    // Validaciones preventivas para evitar que la card quede vacía
    const highlights = proj.highlights || [];
    const ts = proj.tech_stack || {};
    const stackHtml = Object.entries(ts).map(([k, v]) => {
        const labelFromTech = siteData.tags && siteData.tags[lang] && siteData.tags[lang].tech_stack && siteData.tags[lang].tech_stack.keys && siteData.tags[lang].tech_stack.keys[k];
        const labelFlat = siteData.tags && siteData.tags[lang] && siteData.tags[lang][k];
        const label = labelFromTech || labelFlat || k.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
        const value = Array.isArray(v) ? v.join(' + ') : v;
        return `<div class="spec-item"><strong>${label}:</strong> ${value || 'N/A'}</div>`;
    }).join('');

    return `
        <article class="card">
            <div class="card-media">
                ${(() => {
                    const v = proj.video_url;
                    if (v) {
                        if (isVideoUrl(v)) return `<video src="${v}" muted loop onmouseover="this.play()" onmouseout="this.pause()" onerror="this.outerHTML='<img src=\\'${placeholder}\\' alt=\\'${proj.title}\\' loading=\\'lazy\\' />'"></video>`;
                        if (isImageUrl(v)) return `<img src="${v}" alt="${proj.title}" loading="lazy" onerror="this.onerror=null;this.src='${placeholder}';">`;
                    }
                    const firstImg = proj.images?.[0]?.img_path;
                    if (firstImg) return `<img src="${firstImg}" alt="${proj.title}" loading="lazy" onerror="this.onerror=null;this.src='${placeholder}';">`;
                    return `<img src="${placeholder}" alt="${proj.title}" loading="lazy">`;
                })()}
            </div>
            <div class="card-content">
                <div class="card-header">
                    <h3>${proj.title || "Proyecto sin título"}</h3>
                    ${Array.isArray(proj.categories) ? proj.categories.map(k => {
                        const catMeta = (siteData.categories_map && siteData.categories_map[k]) || null;
                        const label = (catMeta && catMeta[lang]) || k;
                        const bg = (catMeta && catMeta.color) || '#777777';
                        const txt = textColorForBg(bg);
                        return `<span class="tag" style="background-color:${bg}; color:${txt};">${label}</span>`;
                    }).join(' ') : ''}
                </div>
                <p class="summary">${proj.short_summary || proj.summary || ""}</p>
                
                <div class="tech-specs">
                    ${stackHtml}
                </div>

                <ul class="highlights">
                    ${highlights.map(h => `<li>${h}</li>`).join('')}
                </ul>
                
                <a href="${proj.detail_url}" class="btn-git">${detailsLabel}</a>
            </div>
        </article>
    `;
                }).join('');
                // render only the cards into the grid; the title element is separate in the template
                ui.projectsGrid.innerHTML = cardsHtml;
            }
        } else {
            if (ui.projectsGrid) ui.projectsGrid.innerHTML = '';
        }

        // Renderizado de Skills con validación (solo cuando la sección active es 'skills')
        if (currentSection === 'skills') {
            if (ui.skillsDisplay && content.skills) {
                ui.skillsDisplay.innerHTML = content.skills.map(group => `
            <div class="skill-group">
                <h4>${group.category}</h4>
                <div class="tags">
                    ${group.list.map(s => `<span class="tag-skill">${s}</span>`).join('')}
                </div>
            </div>
        `).join('');
            }
        } else {
            if (ui.skillsDisplay) ui.skillsDisplay.innerHTML = '';
        }

        // Render Education (solo cuando la sección active es 'education')
        if (currentSection === 'education') {
            if (ui.educationDisplay && content.education) {
                if (ui.educationTitle) ui.educationTitle.textContent = content.nav.education || '';
                ui.educationDisplay.innerHTML = content.education.map(edu => `
                <div class="education-item">
                    <div class="edu-header">
                        <h3>${edu.school || ''} <span class="edu-years">(${edu.start_year || ''} - ${edu.end_year || ''})</span></h3>
                    </div>
                    <div class="edu-degree">${edu.degree || ''}</div>
                    <div class="edu-location">${edu.location || ''}</div>
                    ${edu.thesis_title ? `<h4 class="thesis-title">${edu.thesis_title}</h4>` : ''}
                    ${edu.thesis_description ? `<p class="thesis-desc">${edu.thesis_description}</p>` : ''}
                    ${edu.url ? `<a href="${edu.url}" target="_blank">Ver trabajo</a>` : ''}
                </div>
            `).join('');
            }
        } else {
            if (ui.educationDisplay) ui.educationDisplay.innerHTML = '';
        }
    };

    // 5. Listener del Switch (Interrupción de Usuario)
    if (ui.langBtn) {
        ui.langBtn.addEventListener('click', () => {
            currentLang = (currentLang === 'es') ? 'en' : 'es';
            updateUI(currentLang);
        });
    }

    // 6. Ejecución Inicial
    updateUI(currentLang);

    // --- Sidebar active highlight ---
    const navAnchors = document.querySelectorAll('.tech-sidebar a.nav-link');
    const sectionIds = Array.from(document.querySelectorAll('main .data-view section[id]')).map(s => s.id);

    function setActiveById(id) {
        navAnchors.forEach(a => {
            const href = a.getAttribute('href') || '';
            if (href === `#${id}`) a.classList.add('active');
            else a.classList.remove('active');
        });
        // show filters only when viewing the projects section
        const filtersContainer = document.getElementById('category-filters');
        if (filtersContainer) {
            if (id === 'projects') filtersContainer.style.display = '';
            else filtersContainer.style.display = 'none';
        }
        // track current section and trigger UI update for that section
        currentSection = id;
        updateUI(currentLang);
    }

    // Click handlers to set active immediately when user clicks a nav link
    navAnchors.forEach(a => {
        a.addEventListener('click', (e) => {
            const href = a.getAttribute('href') || '';
            if (href.startsWith('#')) {
                const id = href.slice(1);
                setActiveById(id);
            }
        });
    });

    // IntersectionObserver to highlight based on section in viewport
    const observerOptions = { root: null, rootMargin: '0px 0px -45% 0px', threshold: 0 };
    const observer = new IntersectionObserver((entries) => {
        // pick the entry that is intersecting and has the largest intersectionRatio
        const visible = entries.filter(e => e.isIntersecting);
        if (visible.length > 0) {
            // sort by boundingClientRect area (proxy for visibility)
            visible.sort((a,b) => b.intersectionRatio - a.intersectionRatio);
            const id = visible[0].target.id;
            if (id) setActiveById(id);
        }
    }, observerOptions);

    sectionIds.forEach(id => {
        const el = document.getElementById(id);
        if (el) observer.observe(el);
    });

    // If page opened with a hash, mark the corresponding nav item active
    const initialHash = window.location.hash.slice(1);
    if (initialHash) setActiveById(initialHash);
    else setActiveById('projects');

    // Update active state when the URL hash changes (back/forward navigation)
    window.addEventListener('hashchange', () => {
        const id = window.location.hash.slice(1);
        if (id) setActiveById(id);
    });

    // Some browsers manipulate history without hashchange — listen popstate as well
    window.addEventListener('popstate', () => {
        const id = window.location.hash.slice(1);
        if (id) setActiveById(id);
    });

    // Highlight nav link when user focuses a link with keyboard (accessibility)
    document.addEventListener('focusin', (e) => {
        const target = e.target;
        const navLink = target.closest ? target.closest('.tech-sidebar a.nav-link') : null;
        if (navLink) {
            const href = navLink.getAttribute('href') || '';
            if (href.startsWith('#')) setActiveById(href.slice(1));
        }
    });
});