let sidebarOpen = false;

function toggleSidebar() {
    const sidebar = document.querySelector('.main-sidebar');
    const container = document.querySelector('.container');
    const toggleButton = document.querySelector('.toggle-sidebar');

    if (sidebarOpen) {
        sidebar.style.width = '0';
        container.style.filter = 'none';
        toggleButton.innerHTML = '☰';
    } else {
        container.style.filter = 'blur(3px)';
        sidebar.style.width = '270px';
        toggleButton.innerHTML = '✖';
    }

    sidebarOpen = !sidebarOpen;

    toggleButton.classList.toggle('opened', sidebarOpen);
}

