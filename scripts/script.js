function wtf() {
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