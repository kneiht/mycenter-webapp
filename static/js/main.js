
function onResize() {
    var onresize = document.getElementById('onresize-hs');
    onresize.click();
    adjustGridColumns();
}



function adjustGridColumns() {
    const container = document.getElementById('display_cards');
    if (!container) return;

    const containerWidth = container.offsetWidth;
    // Remove all previous grid classes
    container.className = container.className.replace(/grid-cols-\d+/g, '');

    // Calculate the number of columns, ensuring at least 1 column
    var gridNum = Math.max(1, Math.round((containerWidth - 10) / 360));

    // Optionally, set a maximum number of columns
    const maxColumns = 5; // For example, a maximum of 5 columns
    gridNum = Math.min(gridNum, maxColumns);

    container.classList.add('grid-cols-' + gridNum); // Adjust number of columns as needed
    // Display the display_cards container after the grid has been adjusted for the first time  
    container.classList.remove("opacity-0")
    container.classList.add("opacity-100")
}

// Initial adjustment
document.addEventListener('DOMContentLoaded', onResize)
window.addEventListener('resize', onResize);

// Call this in your sidebar toggle function
// toggleSidebarFunction() { ... adjustGridColumns(); ... }


// MODAL HANDLING =========================================
document.addEventListener('DOMContentLoaded', function() {

    // Remove all modals after a swap to make sure no modals are on the screen, 
    // if there are errors from the form, new modal will be called to appear
    document.body.addEventListener('htmx:beforeSwap', function(event) {
        var modals = document.querySelectorAll('.modal');
        modals.forEach(function(modal) {
            modal.remove();
        });
    });
});






// THEME CHANGE =========================================
document.addEventListener('DOMContentLoaded', () => {
    const themeToggles = document.querySelectorAll('#theme-toggle');
    const storedTheme = localStorage.getItem('theme'); 
    console.log(storedTheme);
    function updateTheme(isDark) {
        const sunIcon = document.getElementById('sun-icon');
        const moonIcon = document.getElementById('moon-icon');
        // Update theme class
        document.documentElement.classList.toggle('dark', isDark);
        localStorage.setItem('theme', isDark ? 'dark' : 'light');

        // Update icons for all sun and moon instances
        sunIcon.style.opacity = isDark ? '0' : '1';
        moonIcon.style.opacity = isDark ? '1' : '0';
    }

    // Event listener for each theme toggle
    themeToggles.forEach(toggle => {
        toggle.addEventListener('change', () => {
            updateTheme(toggle.checked);
        });
    });

    // Check for stored theme preference and apply it
    if (storedTheme) {
        const isDark = storedTheme === 'dark';
        updateTheme(isDark);
        themeToggles.forEach(toggle => {
            toggle.checked = isDark;
        });
    }
});


