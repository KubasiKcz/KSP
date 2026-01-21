// ==================================================================
// HEADER SECTION
// ==================================================================

// Title Changer
const title_messages = [
    "Jak nebýt panicem", 
    "Seznamka pro osamělé školáky", 
    "Pilulky na zvětšení penisu", 
    "A CO JAKO?!", 
    "Dont leave me :(", 
    "Pullnětě někdo Beneše PLS", 
    "Prestižní poznámky pro prestižní školu", 
    ":3",
    "dvojtecka tri",
    "kdy prezentace na tvy🤓☝️ STFUUUUUUUUUU",
    "BOŽO OPRAV TO",
    "Pocem bby, dělej mi mindžu",
    "Nekřesťanské toto",
    "Víme o vás všechno - Cookies",
    "Fortnite a Valorant skin changer",
    "Fort-night"
];

let titleTimeoutId = null;
let titleChanged = false;
let currentSectionTitle = "ＫＳＰ"; 

const rnd = (arr) => arr[Math.floor(Math.random() * arr.length)];

document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        titleTimeoutId = setTimeout(() => {
            document.title = rnd(title_messages);
            titleChanged = true;
        }, 3000);
        
    } else {
        if (titleTimeoutId) {
            clearTimeout(titleTimeoutId);
            titleTimeoutId = null;
        }

        if (titleChanged) {
            document.title = "Nic jsi neviděl :3";
            titleChanged = false;
            
            setTimeout(() => {
                document.title = currentSectionTitle;
            }, 800);
        }
    }
});

//Logo
window.handleLogoClick = function() {
    if (currentPath.length > 0) {
        window.history.back();
    } else {
        window.location.reload();
    }
};

// ==================================================================
// BODY SECTION (MAIN CONTENT)
// ==================================================================

window.fullData = [];
let currentPath = [];

document.addEventListener("DOMContentLoaded", () => {
    window.addEventListener("popstate", (event) => {
        if (event.state && event.state.path) {
            currentPath = event.state.path;
        } else {
            currentPath = [];
        }
        renderCurrentView();
    });

    fetchData();
});

async function fetchData() {
    try {
        const response = await fetch('./data/data.json');
        if (!response.ok) throw new Error('Chyba sítě');
        window.fullData = await response.json();

        if (history.state && history.state.path) {
            currentPath = history.state.path;
        } else {
            history.replaceState({ path: [] }, "");
        }

        renderCurrentView();
    } catch (error) {
    }
}

function renderCurrentView() {
    let dataToRender = window.fullData;
    let valid = true;

    for (let index of currentPath) {
        if (dataToRender[index] && dataToRender[index].children) {
            dataToRender = dataToRender[index].children;
        } else {
            valid = false;
            break;
        }
    }

    if (!valid) {
        currentPath = [];
        dataToRender = window.fullData;
        history.replaceState({ path: [] }, "");
    }

    renderContent(dataToRender);
}

function renderContent(data) {
    const container = document.getElementById('dynamic-content');
    if (!container) return;
    container.innerHTML = '';

    const hasGroups = data.some(item => item.type === 'group');

    if (hasGroups) {
        data.forEach((group, index) => {
            if (group.type === 'group') {
                const title = document.createElement('h2');
                title.innerText = group.name;
                title.className = 'section-title';
                container.appendChild(title);

                const grid = document.createElement('div');
                grid.className = 'box-container';
                renderGridItems(group.children, grid, index);
                container.appendChild(grid);
            } else {
                const grid = document.createElement('div');
                grid.className = 'box-container';
                renderGridItems([group], grid, index);
                container.appendChild(grid);
            }
        });
    } else {
        const grid = document.createElement('div');
        grid.className = 'box-container';
        renderGridItems(data, grid, null);
        container.appendChild(grid);
    }
}

function renderGridItems(items, container, groupIndex) {
    items.forEach((item, localIndex) => {
        
        // Wrapper
        const wrapper = document.createElement('div');
        wrapper.className = 'item-wrapper';
        
        // Box
        let box;
        if (item.type === 'folder' || item.type === 'group') {
            box = document.createElement('div');
            box.onclick = () => {
                const newPath = [...currentPath];
                if (groupIndex !== null) newPath.push(groupIndex);
                newPath.push(localIndex);
                currentPath = newPath;
                history.pushState({ path: currentPath }, "");
                renderCurrentView();
            };
        } else {
            box = document.createElement('a');
            box.href = item.url || '#';
            if (item.type === 'link' && item.url && item.url.startsWith('http')) {
                box.target = "_blank";
            }
        }
        
        box.className = 'box'; 

        // --- BOX BACKGROUND (BODY) ---
        if (item.image) {
            const bgImg = document.createElement('img');
            bgImg.src = item.image;
            bgImg.alt = item.name;
            bgImg.className = 'box-bg'; 
            bgImg.onerror = function() {
                this.style.display = 'none';
                const icon = document.createElement('img');
                icon.src = './graphics/icons/folder.png'; 
                icon.style.width = "64px";
                icon.style.height = "64px";
                icon.style.opacity = "0.5";
                box.appendChild(icon);
            }
            box.appendChild(bgImg);
        }

        // --- ICONS (BODY) ---

        // Type Icon
        if (item.icon) {
            const typeIcon = document.createElement('img');
            typeIcon.src = `./graphics/type/${item.icon}.png`;
            typeIcon.className = 'badge-icon icon-type'; 
            
            typeIcon.onerror = function() { 
                this.style.display = 'none'; 
            };
            
            box.appendChild(typeIcon);
        }
        // Source Icon
        if (item.source) {
            const infoIcon = document.createElement('img');
            infoIcon.src = `./graphics/source/${item.source}.png`; 
            infoIcon.className = 'badge-icon icon-info'; 
            let tooltipLines = [];
            if (item.source) tooltipLines.push(`Zdroj: ${item.source}`);
            if (item.ai) tooltipLines.push(`AI: ${item.ai}`)            
            infoIcon.title = tooltipLines.join("\n");
            infoIcon.onerror = function() {
                this.style.display = 'none';
            };
            box.appendChild(infoIcon);
        }

        wrapper.appendChild(box);

        // Text pod boxem
        const titleP = document.createElement('p');
        titleP.innerText = item.name;
        titleP.className = 'box-title'; 
        
        wrapper.appendChild(titleP);
        container.appendChild(wrapper);
    });
}

// ==================================================================
// FOOTER SECTION
// ==================================================================

function github_redirect() {
    window.open("https://github.com/kubasikcz/ksp", "_blank");
}

function help() {
    const modal = document.getElementById('help');
    if (modal) {
        modal.classList.add('help-modal');

        const closeBtn = modal.querySelector('button');
        if (closeBtn) {
            closeBtn.onclick = () => {
                modal.classList.remove('help-modal');
            };
        }
    }
}

function closeHelp() {
    const modal = document.getElementById('help');
    if (modal) {
        modal.classList.remove('help-modal');
    }
}

function changelog() {
    const modal = document.getElementById('version');
    if (modal) {
        modal.classList.add('version-modal');

        const closeBtn = modal.querySelector('button');
        if (closeBtn) {
            closeBtn.onclick = () => {
                modal.classList.remove('version-modal');
            };
        }
    }
}

async function loadVersionData() {
    try {
        const response = await fetch('./data/version.json');
        if (!response.ok) return;

        const data = await response.json();

        const footerVer = document.getElementById('ver_nmr');
        if (footerVer && data.length > 0) {
            footerVer.innerText = "" + data[0].version;
        }

        const modalContainer = document.getElementById('version');
        if (!modalContainer) return;

        const table = modalContainer.querySelector('table');
        if (table) {
            table.innerHTML = `
                <thead>
                    <tr>
                        <th>Verze</th>
                        <th>Datum</th>
                        <th>Změny</th>
                    </tr>
                </thead>
                <tbody>
                </tbody>
            `;

            const tbody = table.querySelector('tbody');

            data.forEach(item => {
                let changesContent = "";
                if (Array.isArray(item.changes)) {
                    item.changes.forEach(line => {
                        changesContent += line + "<br>";
                    });
                } else {
                    changesContent = item.changes;
                }

                const badgeContent = item.badge ? `<br><span style="font-size: 0.8em; opacity: 0.8;">${item.badge}</span>` : "";

                const row = document.createElement('tr');
                row.innerHTML = `
                    <td style="font-weight: bold; white-space: nowrap; vertical-align: top;">
                        ${item.version}
                        ${badgeContent}
                    </td>
                    <td style="white-space: nowrap; vertical-align: top;">${item.date}</td>
                    <td style="vertical-align: top;">${changesContent}</td>
                `;
                tbody.appendChild(row);
            });
        }

    } catch (error) {
        const footerVer = document.getElementById('ver_nmr');
        if (footerVer) footerVer.innerText = "Err";
    }
}

document.addEventListener("DOMContentLoaded", () => {
    loadVersionData();

    if (!localStorage.getItem('hasVisited')) {
        help();
        localStorage.setItem('hasVisited', 'true');
    }

    document.addEventListener('keydown', (e) => {
        if (e.key === "Escape") {
            const versionModal = document.getElementById('version');
            const helpModal = document.getElementById('help');
            if (versionModal) versionModal.classList.remove('version-modal');
            if (helpModal) helpModal.classList.remove('help-modal');
        }
    });
});