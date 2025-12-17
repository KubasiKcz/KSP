//! Title Changer [Já :3]
const title_option = {
    csvPath: 'data.csv',
    originalTitle: document.title, // Uloží původní název stránky
    messages: [
        "ＫＳＰ - ICU 👀", 
        "ＫＳＰ - Seznamka", 
        "ＫＳＰ - Pilulky na zvětšení penisu", 
        "ＫＳＰ - A CO JAKO?!", 
        "ＫＳＰ - Dont leave me :(", 
        "ＫＳＰ - Pullnětě někdo Beneše PLS", 
        "ＫＳＰ - Prestižní poznámky pro prestižní školu", 
        "ＫＳＰ - :3", 
        "ＫＳＰ - kdy prezentace na tvy🤓☝️ STFUUUUUUUUUU",
        "ＫＳＰ - BOŽO OPRAV TO"
    ]
};

let titleTimeoutId = null;
let titleChanged = false;

const rnd = (arr) => arr[Math.floor(Math.random() * arr.length)];

document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        // Uživatel odešel
        titleTimeoutId = setTimeout(() => {
            document.title = rnd(title_option.messages);
            titleChanged = true;
        }, 3000);
    } else {
        // Uživatel se vrátil
        if (titleTimeoutId) {
            clearTimeout(titleTimeoutId);
            titleTimeoutId = null;
        }
        if (titleChanged) {
            document.title = "ＫＳＰ - Nic jsi neviděl :3";
            titleChanged = false;
            setTimeout(() => {
                document.title = title_option.originalTitle;
            }, 800);
        }
    }
});


//! WTF function [Já :3]
const WTFbtn = {
    msg: [
        "A jako co chceš dělat na indexu?!",
        "Pokračuj a možná něco spustíš ¯_(ツ)_¯",
        "Doufám, že tě to tu baví :3",
        "BAF VOLE! lekl?"
    ]
}
function wtf() {
    alert(rnd(WTFbtn.msg));
}


//! CSV Generace [Gemini]

// Dynamicky určí cestu k souborům podle toho, zda jsme v rootu nebo v podsložce
function getPath(relativePath) {
    const isIndex = window.location.pathname.endsWith('index.html') || 
                    window.location.pathname === '/' || 
                    window.location.pathname.endsWith('/');
    
    // Pokud jsme na indexu, cesta je přímá, jinak musíme o úroveň výš
    return isIndex ? `./${relativePath}` : `../${relativePath}`;
}

// Převede text z CSV do pole objektů (klíče jsou názvy sloupců z prvního řádku)
function parseCSV(csvText) {
    const lines = csvText.trim().split('\n');
    if (lines.length < 2) return []; // Ošetření prázdného souboru

    const headers = lines[0].split(',').map(h => h.trim());
    
    return lines.slice(1).map(line => {
        const values = line.split(',');
        return headers.reduce((obj, header, i) => {
            obj[header] = values[i]?.trim() || '';
            return obj;
        }, {});
    });
}

// Rozřadí data do objektu podle kategorií
function groupByCategory(data) {
    const grouped = {};
    data.forEach(item => {
        const category = item.category?.trim() || 'Ostatní';
        if (!grouped[category]) grouped[category] = [];
        grouped[category].push(item);
    });
    return grouped;
}

//? Vytvoří HTML strukturu pro jednu kartu (box)
function renderItem(item) {
    const a = document.createElement('a');
    a.href = item.link;

    let link = item.link;
    let format = "";

    for (let i = 2; i < link.length; i++) {
        if (link[i] === '.') {
            format = link.slice(i + 1);
            break;
        }
    }

    if (!(format === "html")) {
        a.target = "_blank";
    }

    const box = document.createElement('div');
    box.classList.add('box');

    // Hlavní obrázek - automaticky opraví cestu
    const img = document.createElement('img');
    img.src = item.image.startsWith('./') 
        ? item.image.replace('./', getPath('')) 
        : getPath(item.image);
    img.alt = item.title;
    box.appendChild(img);

    // Ikona typu (pokud existuje a není 'None')
    if (item.type && item.type !== 'None') {
        const typeIcon = document.createElement('img');
        typeIcon.src = getPath(`graphics/type/${item.type}.png`);
        typeIcon.alt = item.type;
        typeIcon.classList.add('icon');
        box.appendChild(typeIcon);
    }

    a.appendChild(box);

    // Titulek pod obrázkem
    const p = document.createElement('p');
    p.textContent = item.title;
    p.classList.add('subject-title');
    a.appendChild(p);

    return a;
}

// Vykreslí všechny kategorie a jejich položky do kontejneru
function renderContent(container, groupedData, isIndex) {
    if (!container) return;
    container.innerHTML = ''; // Vyčištění kontejneru před vykreslením

    Object.keys(groupedData).forEach(category => {
        const items = groupedData[category];

        // Vykreslení nadpisu kategorie (pokud to nejsou "Ostatní")
        if (category !== 'Ostatní') {
            const header = document.createElement(isIndex ? 'h3' : 'h2');
            header.textContent = category;
            container.appendChild(header);
        }

        // Vytvoření mřížky pro karty
        const boxContainer = document.createElement('div');
        boxContainer.className = 'box-container';
        
        items.forEach(item => {
            boxContainer.appendChild(renderItem(item));
        });
        
        container.appendChild(boxContainer);
    });
}

/**
 * HLAVNÍ SPOUŠTĚČ
 */

document.addEventListener('DOMContentLoaded', async () => {
    const container = document.getElementById('dynamic-content');
    
    // Získání názvu aktuální stránky bez přípony (např. "index" nebo "portfolio")
    const path = window.location.pathname;
    const pageName = path.split('/').pop().split('.')[0] || 'index';
    const isIndex = pageName === 'index';

    try {
        // 1. Načtení CSV souboru
        const response = await fetch(getPath('data.csv'));
        if (!response.ok) throw new Error(`Nelze načíst CSV: ${response.status}`);
        
        const csvText = await response.text();
        
        // 2. Zpracování dat
        const allData = parseCSV(csvText);
        
        // 3. Filtrace dat pouze pro aktuální stránku
        const pageData = allData.filter(item => item.page === pageName);
        
        // 4. Seskupení a vykreslení
        const groupedData = groupByCategory(pageData);
        renderContent(container, groupedData, isIndex);
        
    } catch (error) {
        console.error('Chyba při inicializaci stránky:', error);
    }
});