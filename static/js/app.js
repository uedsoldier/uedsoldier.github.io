document.addEventListener('DOMContentLoaded', () => {
    // 1. Obtener los datos del "Sensor" (El script JSON inyectado por Jinja)
    const dataElement = document.getElementById('site-data');
    if (!dataElement) return;

    const siteData = JSON.parse(dataElement.textContent);

    // 2. Definir el Estado Inicial
    let currentLang = siteData.config.default_lang || 'es';

    // 3. Referencias a los Nodos del DOM (Actuadores)
    const ui = {
        name: document.getElementById('ui-name'),
        label: document.getElementById('ui-label'),
        navProjects: document.getElementById('nav-projects'),
        navSkills: document.getElementById('nav-skills'),
        projectsGrid: document.getElementById('projects'),
        skillsTitle: document.getElementById('ui-skills-title'),
        skillsDisplay: document.getElementById('skills-display'),
        langBtn: document.getElementById('lang-btn'),
        langLabel: document.getElementById('lang-label')
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
        if (!content) return; // Protección si el idioma no existe
        console.log("Proyectos encontrados:", content.projects);
        // Uso de Optional Chaining (?.) para evitar que el script truene si falta un ID
        if (ui.name) ui.name.textContent = content.name;
        if (ui.label) ui.label.textContent = content.label;
        if (ui.navProjects) ui.navProjects.textContent = content.nav.projects;
        if (ui.navSkills) ui.navSkills.textContent = content.nav.skills;
        if (ui.skillsTitle) ui.skillsTitle.textContent = content.nav.skills;
        if (ui.langLabel) ui.langLabel.textContent = (lang === 'es') ? 'EN' : 'ES';

        // Renderizado de Proyectos con validación
        ui.projectsGrid.innerHTML = content.projects.map(proj => {
    // Validaciones preventivas para evitar que la card quede vacía
    const hw = proj.tech_stack?.hardware || [];
    const fw = proj.tech_stack?.firmware || [];
    const protocols = proj.tech_stack?.protocols || [];
    const highlights = proj.highlights || [];

    return `
        <article class="card">
            <div class="card-media">
                ${proj.video_url ? 
                    `<video src="${proj.video_url}" muted loop onmouseover="this.play()" onmouseout="this.pause()"></video>` : 
                    `<img src="${proj.images?.[0]?.img_path || 'static/img/placeholder.jpg'}" alt="${proj.title}" loading="lazy">`
                }
            </div>
            <div class="card-content">
                <div class="card-header">
                    <h3>${proj.title || "Proyecto sin título"}</h3>
                    <span class="tag">${proj.category || "General"}</span>
                </div>
                <p class="summary">${proj.summary || ""}</p>
                
                <div class="tech-specs">
                    <div class="spec-item"><strong>HW:</strong> ${hw.join(' + ') || 'N/A'}</div>
                    <div class="spec-item"><strong>FW:</strong> ${fw.join(', ') || 'N/A'}</div>
                    <div class="spec-item"><strong>BUS:</strong> ${protocols.join(' | ') || 'N/A'}</div>
                </div>

                <ul class="highlights">
                    ${highlights.map(h => `<li>${h}</li>`).join('')}
                </ul>
                
                <a href="${proj.url || '#'}" target="_blank" class="btn-git">Source Code</a>
            </div>
        </article>
    `;
}).join('');

        // Renderizado de Skills con validación
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
});