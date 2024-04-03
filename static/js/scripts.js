
document.addEventListener('DOMContentLoaded', (event) => {
    const currentYear = new Date().getFullYear();
    document.querySelector('.footer .text-muted').textContent = `© ${currentYear} Zhao Lin Wu et Keven Jude Antenor. All rights reserved.`;
});
