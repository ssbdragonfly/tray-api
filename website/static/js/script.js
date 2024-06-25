document.addEventListener('DOMContentLoaded', (event) => {
    const theme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', theme);

    const toggleButton = document.getElementById('theme-toggle');
    if (theme === 'dark') {
        toggleButton.classList.add('fa-sun');
        toggleButton.classList.remove('fa-moon');
    } else {
        toggleButton.classList.add('fa-moon');
        toggleButton.classList.remove('fa-sun');
    }

    console.log(`Current theme on load: ${theme}`);
});

function toggleTheme() {
    let currentTheme = document.documentElement.getAttribute('data-theme');
    let targetTheme = 'light';

    if (currentTheme === 'light') {
        targetTheme = 'dark';
    }

    document.documentElement.setAttribute('data-theme', targetTheme);
    localStorage.setItem('theme', targetTheme);

    const toggleButton = document.getElementById('theme-toggle');
    if (targetTheme === 'dark') {
        toggleButton.classList.add('fa-sun');
        toggleButton.classList.remove('fa-moon');
    } else {
        toggleButton.classList.add('fa-moon');
        toggleButton.classList.remove('fa-sun');
    }

    console.log(`Theme toggled to: ${targetTheme}`);
}
