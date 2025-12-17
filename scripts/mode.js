function mode() { //! Dark mode [Božo]
    const root = document.documentElement;
    const img = document.querySelector("#dark_mode");

    root.classList.toggle("dark");

    const page = window.location.pathname.split('/').pop().split('.')[0];
    
    if (root.classList.contains("dark")) {
        localStorage.setItem("theme", "dark");
        if (page === "index") {
            img.src = "./graphics/icons/darkmode-switch.png";
        } else {
            img.src = "../graphics/icons/darkmode-switch.png";
        }
    } else {
        localStorage.setItem("theme", "light");
        if (page === "index") {
            img.src = "./graphics/icons/lightmode-switch.png";
        } else {
            img.src = "../graphics/icons/lightmode-switch.png";
        }
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const img = document.querySelector("#dark_mode");

    img.src = window.__darkModeImage;
});