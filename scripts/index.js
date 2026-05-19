// ==================================================================
// HEADER SECTION
// ==================================================================

// Title Changer
const title_messages = [
    "Jak nebýt panicem", 
    "Seznamka pro osamělé školáky", 
    "Pilulky na zvětšení svého údu", 
    "A CO JAKO?!", 
    "Dont leave me :(", 
    "Pullnětě někdo Beneše PLS", 
    "Prestižní poznámky pro prestižní školu", 
    ":3",
    "dvojtecka tri",
    "kdy prezentace na tvy🤓☝️ STFUUUUUUUUUU",
    "BOŽO OPRAV TO",
    "Pocem bby, dělej tu mindžu",
    "Nekřesťanské toto",
    "Fortnite a Valorant skin changer",
    "D̸̨̢͔̘̳̱̊̔͜͝Ȩ̸̛̱̭̭͂̀̂́̐̀̔͒͝M̷̖̬̩̱̹̯͔̅Ő̵͙̠̝̹͖̉͑N̴̨̬̗̣͇̳̈́̚͜ ̶̡̡̞̝̪̗̮͙͎̈́̄́̑͑́͘͜͝S̴̳̙̪̙̭͈͇̭̣̿͐̀̔͐̈́̈́̅͗̚U̶̢̡̮̝͕͖̍̈̓̓́̕̕M̸̨̺͚̥͎͐͛̏͊͌̀̕̕M̶̨͕͉̰̞̙̔̊̄̈́͑̄͘͝͝O̸̡̝͉̻̪̐̀̔̇̉͂̓̔̂͠N̸̻̯̜̑̿̌̐͛̾̈́͒̿͠È̶̗̩̳̳̘͚̥͇̎̀̏̍R̸̗̳̥̰̣̠̬̩̉̈́̑͌̐̂̊̈̏̚"
];

let titleTimeoutId = null;
let titleChanged = false;
let currentSectionTitle = "vočko"; 

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

// Zpět na index
window.handleLogoClick = function() {
    if (currentPath.length > 0) {
        currentPath = [];
        history.pushState({ path: currentPath }, "");
        renderCurrentView();
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
        const response = await fetch('./database/data.json');
        if (!response.ok) throw new Error('Chyba sítě');
        const rawData = await response.json();
        
        // --- PREPROCESSOR: Dynamické cesty ---
        function preprocessData(nodes, yearShort = null, subjectShort = null) {
            nodes.forEach(node => {
                let currentYear = yearShort;
                let currentSubject = subjectShort;
                
                // Určení ročníku a předmětu podle short zkratek v jsonu
                if (node.type === 'folder' && !yearShort) {
                    currentYear = node.short || null;
                } else if ((node.type === 'folder' || node.type === 'group') && yearShort && !subjectShort && node.short) {
                    currentSubject = node.short;
                    
                    if (!node.image) {
                        node.image = `./graphics/subjects/${currentYear}/${currentSubject}.png`;
                    }
                }

                // Generování relativních path pro PDF materiály a thumbnails
                if (node.type === 'link' && node.file) {
                    if (!node.url && currentYear && currentSubject) {
                        node.url = `./materials/${currentYear}/${currentSubject}/${node.file}`;
                    }
                    if (!node.image && currentYear && currentSubject) {
                        const parts = node.file.split('.');
                        const fileNameWithoutExt = parts.length > 1 ? parts.slice(0, -1).join('.') : node.file;
                        node.image = `./graphics/subjects/${currentYear}/${currentSubject}/${fileNameWithoutExt}.png`;
                    }
                }
                
                // Rekurzivní zpracování children
                if (node.children) {
                    preprocessData(node.children, currentYear, currentSubject);
                }
            });
        }
        preprocessData(rawData);
        window.fullData = rawData;
        // -----------------------------------

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
    
    const breadcrumbs = [{ name: "Domů", path: [] }];
    let tempPath = [];

    for (let index of currentPath) {
        tempPath.push(index);
        if (dataToRender[index] && dataToRender[index].children) {
            if (dataToRender[index].type !== 'group') {
                breadcrumbs.push({ 
                    name: dataToRender[index].name, 
                    path: [...tempPath] 
                });
            }
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
        breadcrumbs.length = 1;
    }

    const breadcrumbsDiv = document.getElementById('breadcrumbs');
    if (breadcrumbsDiv) {
        breadcrumbsDiv.innerHTML = '';
        breadcrumbs.forEach((crumb, i) => {
            const span = document.createElement('span');
            span.innerText = crumb.name;
            
            if (i < breadcrumbs.length - 1) {
                span.className = 'crumb-link';
                span.onclick = () => {
                    currentPath = crumb.path;
                    history.pushState({ path: currentPath }, "");
                    renderCurrentView();
                };
            } else {
                span.className = 'crumb-active';
            }
            
            breadcrumbsDiv.appendChild(span);
            
            if (i < breadcrumbs.length - 1) {
                const sep = document.createElement('span');
                sep.innerText = '>';
                sep.className = 'crumb-separator';
                breadcrumbsDiv.appendChild(sep);
            }
        });
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
        
        // Hlavní wrapper element pro položku
        const wrapper = document.createElement('div');
        wrapper.className = 'item-wrapper';
        
        // Box link pro kliknutí (složka, skupina nebo přímý odkaz)
        let box;
        if (item.type === 'folder' || item.type === 'group') {
            box = document.createElement('a');
            box.href = '#vocko';
            box.onclick = (scrl) => {
                scroll(scrl);
                if (item.__absPath) {
                    currentPath = item.__absPath;
                } else {
                    const newPath = [...currentPath];
                    if (groupIndex !== null) newPath.push(groupIndex);
                    newPath.push(localIndex);
                    currentPath = newPath;
                }
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
                this.src = './graphics/placeholder.png';
            }
            box.appendChild(bgImg);
        }

        // --- ICONS (BODY) ---

        // Type Icon (pdf, word, pptx...)
        if (item.icon) {
            const typeIcon = document.createElement('img');
            typeIcon.src = `./graphics/type/${item.icon}.png`;
            typeIcon.className = 'badge-icon icon-type'; 
            
            typeIcon.onerror = function() { 
                this.src = './graphics/placeholder.png'; 
            };
            
            box.appendChild(typeIcon);
        }
        // Source Icon (Beneš, z netu...) s tooltiplem
        if (item.source) {
            const infoIcon = document.createElement('img');
            infoIcon.src = `./graphics/source/${item.source}.png`; 
            infoIcon.className = 'badge-icon icon-info'; 
            let tooltipLines = [];
            if (item.source) tooltipLines.push(`Zdroj: ${item.source}`);
            if (item.ai) tooltipLines.push(`AI: ${item.ai}`)            
            infoIcon.title = tooltipLines.join("\n");
            infoIcon.onerror = function() {
                this.src = './graphics/placeholder.png';
            };
            box.appendChild(infoIcon);
        }

        wrapper.appendChild(box);

        // Název materiálu zobrazený pod boxem
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

window.openModal = function(id) {
    const modal = document.getElementById(id);
    const overlay = document.getElementById('modal-overlay');
    if (modal && overlay) {
        overlay.classList.add('show');
        modal.classList.add('show-modal');
    }
}

window.closeModal = function(id) {
    const modal = document.getElementById(id);
    const overlay = document.getElementById('modal-overlay');
    if (modal && overlay) {
        modal.classList.remove('show-modal');
        // Pokud není otevřený žádný jiný modal, skryje se i overlay
        if (!document.querySelector('.modal.show-modal')) {
            overlay.classList.remove('show');
        }
    }
}

window.help = () => openModal('help');
window.changelog = () => openModal('version');

async function loadVersionData() {
    try {
        const response = await fetch('./database/version.json');
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
                // --- Generování obsahu změn ---
                let changesContent = "";
                if (Array.isArray(item.changes)) {
                    let inList = false;
                    item.changes.forEach(line => {
                        if (line.startsWith("- ")) {
                            if (!inList) { changesContent += `<ul class="cl-list">`; inList = true; }
                            changesContent += `<li>${line.slice(2)}</li>`;
                        } else {
                            if (inList) { changesContent += `</ul>`; inList = false; }
                            changesContent += `<span class="cl-header">${line}</span>`;
                        }
                    });
                    if (inList) changesContent += `</ul>`;
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

    // Boot screen animace při úplně první návštěvě (first visit)
    const bootScreen = document.getElementById('boot-screen');
    const isFirstVisit = !localStorage.getItem('hasVisitedV3');
    
    if (isFirstVisit && bootScreen) {
        bootScreen.style.display = 'flex';
        const bootEye = document.getElementById('boot-eye');
        setTimeout(() => {
            if (bootEye) bootEye.classList.add('open');
        }, 100);
        setTimeout(() => {
            if (bootEye) bootEye.classList.add('centered');
            setTimeout(() => {
                if (bootEye) {
                    bootEye.classList.remove('open');
                }
                bootScreen.style.opacity = '0';
                bootScreen.style.transition = 'opacity 0.8s ease';
                setTimeout(() => {
                    bootScreen.style.display = 'none';
                    openModal('help');
                }, 800);
            }, 400);
        }, 1800);
        localStorage.setItem('hasVisitedV3', 'true');
    }

    // Zavírání modals pomocí esc, či kliknutí jinam
    document.addEventListener('keydown', (e) => {
        if (e.key === "Escape") {
            document.querySelectorAll('.modal.show-modal').forEach(m => closeModal(m.id));
        }
    });

    const overlay = document.getElementById('modal-overlay');
    if (overlay) {
        overlay.addEventListener('click', () => {
            document.querySelectorAll('.modal.show-modal').forEach(m => closeModal(m.id));
        });
    }

    // Vyhledávač
    const searchBar = document.getElementById('bar');
    if (searchBar) {
        searchBar.placeholder = "Hledat...";
        searchBar.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase();
            if (query.trim() === "") {
                renderCurrentView();
                return;
            }
            
            const results = [];
            
            function removeDiacritics(str) {
                return str.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
            }
            
            function fuzzyScore(query, text) {
                const q = removeDiacritics(query.toLowerCase());
                const t = removeDiacritics(text.toLowerCase());
                
                if (t === q) return 10000;
                if (t.includes(q)) return 1000 + (t.length - t.indexOf(q));
                
                let i = 0, j = 0;
                let consecutive = 0;
                let score = 0;
                while (i < q.length && j < t.length) {
                    if (q[i] === t[j]) {
                        score += 10 + (consecutive * 5);
                        consecutive++;
                        i++;
                    } else {
                        consecutive = 0;
                    }
                    j++;
                }
                return i === q.length ? score : 0;
            }

            function searchTree(items, currentPathArr) {
                items.forEach((item, index) => {
                    const newPath = [...currentPathArr, index];
                    
                    if (item.type !== 'group' && item.type !== 'folder') {
                        const nameScore = fuzzyScore(query, item.name);
                        const tagsScore = fuzzyScore(query, item.tags || "");
                        const score = Math.max(nameScore, tagsScore);
                        if (score > 0) {
                            results.push({...item, __absPath: newPath, __score: score});
                        }
                    }

                    if (item.children) {
                        searchTree(item.children, newPath);
                    }
                });
            }
            searchTree(window.fullData, []);
            
            results.sort((a, b) => b.__score - a.__score);
            
            const container = document.getElementById('dynamic-content');
            if (container) {
                container.innerHTML = '';
                const title = document.createElement('h2');
                title.innerText = `Výsledky hledání`;
                title.className = 'section-title';
                container.appendChild(title);

                const grid = document.createElement('div');
                grid.className = 'box-container';
                renderGridItems(results, grid, null);
                container.appendChild(grid);
            }
        });
    }

    // Odesílání žádostí o nahrání
    const uploadForm = document.getElementById('upload-form');
    if (uploadForm) {
        uploadForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const status = document.getElementById('upload-status');
            
            // Honeypot check proti spambotům
            if (document.getElementById('user-website').value !== "") {
                status.innerText = "Chyba sítě. Zkuste to později.";
                status.style.color = "red";
                return; // Detekován bot
            }

            // Cooldown check (limit 5 odeslání za hodinu v localStorage)
            const now = Date.now();
            let uploads = JSON.parse(localStorage.getItem('uploadTimestamps') || '[]');
            uploads = uploads.filter(t => now - t < 3600000); // Filtrování timestampů za poslední hodinu

            if (uploads.length >= 5) {
                status.innerText = "Dosáhli jste limitu (5 žádostí za hodinu). Zkuste to později.";
                status.style.color = "red";
                return;
            }

            const action = document.getElementById('up-action').value;
            let embedColor = 2326507; // Default Blue (výchozí modrá)
            if (action === "UPLOAD") embedColor = 5763719; // Green (zelená)
            if (action === "EDIT") embedColor = 16776960; // Yellow (žlutá)
            if (action === "REMOVE") embedColor = 15548997; // Red (červená)

            const authorName = document.getElementById('up-author').value || "Anonym";
            const authorIcon = document.getElementById('up-pfp').value;

            const embed = {
                title: action,
                color: embedColor,
                author: {
                    name: authorName,
                    icon_url: authorIcon ? authorIcon : undefined
                },
                description: `**Název materiálu:** ${document.getElementById('up-title').value}\n` +
                             `**Odkaz na materiál:** ${document.getElementById('up-link').value}\n\n` +
                             `**Poznámka:**\n${document.getElementById('up-note').value || 'Žádná poznámka'}`
            };

            try {
                status.innerText = "Odesílám...";
                status.style.color = "var(--text-color)";
                const url = atob("aHR0cHM6Ly9kaXNjb3JkLmNvbS9hcGkvd2ViaG9vaHMvMTUwNTk3NzgzMTI4MzQ5NTAwMy9GZXdneDJNbzNNZ05IdkhSMndMRHd5d1NtVGRiQjRJY1hMSnpoQ1NQczl3dXhlRURZT1ZfLXZFaGpvVzRvcEppWFhV");
                
                await fetch(url, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ content: "<@677124005718654986>", embeds: [embed] })
                });
                status.innerText = "Úspěšně odesláno! Děkujeme.";
                status.style.color = "green";
                
                uploads.push(now);
                localStorage.setItem('uploadTimestamps', JSON.stringify(uploads));
                localStorage.removeItem('lastUploadTime');
                
                uploadForm.reset();
                setTimeout(() => closeModal('upload'), 2500);
            } catch (err) {
                status.innerText = "Nastala chyba při odesílání.";
                status.style.color = "red";
            }
        });
    }
});function wtf() {
    if (window.handleLogoClick) {
        window.handleLogoClick();
    } else {
        window.location.reload();
    }
}

function scroll(event) {
    event.preventDefault();
    const top = document.getElementById("vocko");
    if (top) {
        top.scrollIntoView({ behavior: "instant", block: "start"})
    }
}
