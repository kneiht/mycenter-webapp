
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

    // Use delication to make sure  new add element can be list
    document.body.addEventListener('click', function(event) {
        if (event.target.closest('#open-modal')) {
            var element = event.target.closest('#open-modal')
            var modalID = element.getAttribute('modal-id');
            //console.log(modalID);
            openLocalModal(modalID);
        }
    });

    function zopenLocalModal(modalID) {
        // Retrieve the HTML content from local storage
        var htmlContent = localStorage.getItem(modalID);
        if (htmlContent) {
            // Select the body element
            var body = document.body;
            // Insert the HTML content at the beginning of the body
            body.insertAdjacentHTML('afterbegin', htmlContent);
            // Remove the 'hidden' class to display the modal
            var modal = document.getElementById(modalID);
            // Rebind the element
            _hyperscript.processNode(modal)
            htmx.process(modal);
        }
    }

    // Remove all modals after a swap to make sure no modals are on the screen, 
    // if there are errors from the form, new modal will be called to appear
    document.body.addEventListener('htmx:beforeSwap', function(event) {
        var modals = document.querySelectorAll('.zmodal');
        modals.forEach(function(modal) {
            modal.remove();
        });
    });
});




// CONTEXT MENU BUTTONS =========================================
document.addEventListener('DOMContentLoaded', function() {
    // Use delication to make sure  new add element can be list

    document.body.addEventListener('click', function(event) {
        var editButton = event.target.closest('#record-edit');
        if (editButton) {
            var buttonEdit = event.target
            var recordID = buttonEdit.closest('.card').getAttribute('record-id');
     
            var url = '/schools/' + recordID + '/form';
            htmx.ajax('GET', url, {
                target: 'body', // The element to be updated with the response
                swap: 'afterbegin'        // How to swap the response into the target
            });
        }
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


