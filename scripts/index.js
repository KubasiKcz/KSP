//! Version pop-up modal [BLACKBOXAI]
function show() {
    const versionDiv = document.querySelector('main #version');
    if (versionDiv) {
        versionDiv.classList.add('version-modal');
        const closeBtn = versionDiv.querySelector('button');
        if (closeBtn) {
            closeBtn.onclick = () => {
                versionDiv.classList.remove('version-modal');
                closeBtn.onclick = null;
            };
        }
    }
}