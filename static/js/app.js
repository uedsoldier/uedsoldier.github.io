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
    const content = siteData.languages[lang];
    if (!content) return; // Protección si el idioma no existe

    // Uso de Optional Chaining (?.) para evitar que el script truene si falta un ID
    if (ui.name) ui.name.textContent = content.name;
    if (ui.label) ui.label.textContent = content.label;
    if (ui.navProjects) ui.navProjects.textContent = content.nav.projects;
    if (ui.navSkills) ui.navSkills.textContent = content.nav.skills;
    if (ui.skillsTitle) ui.skillsTitle.textContent = content.nav.skills;
    if (ui.langLabel) ui.langLabel.textContent = (lang === 'es') ? 'EN' : 'ES';

    // Renderizado de Proyectos con validación
    if (ui.projectsGrid && content.projects) {
        ui.projectsGrid.innerHTML = content.projects.map(proj => `
            <article class="card">
                <h3>${proj.title}</h3>
                </article>
        `).join('');
    }

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