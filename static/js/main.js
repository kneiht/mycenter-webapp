// DB TOOL BAR HANDLING =========================================
// Get the filter list and initially hide it
var filterList = document.getElementById('filter-list');

// Show the filter list when the filter bar is clicked
document.getElementById('add-filter-button').addEventListener('click', function(event) {
    filterList.classList.remove('hidden');
    event.stopPropagation(); // Prevent the document click event from being triggered
});

// Show the filter list when the filter-phrase input is clicked
document.getElementById('filter-phrase').addEventListener('click', function(event) {
    // Check if the filter list has any child elements
    if (filterList.children.length !== 0) {
        filterList.classList.remove('hidden');
        event.stopPropagation(); // Prevent the document click event from being triggered
    }
});

// Hide the filter list when clicked outside of the filter bar or filter-phrase
document.addEventListener('click', function() {
    filterList.classList.add('hidden');
});

document.getElementById('add-filter-button').addEventListener('click', function() {
    // Get the selected field and filter phrase
    var field = document.getElementById('filter-field').value;
    var phrase = document.getElementById('filter-phrase').value;

    // Create a new filter tag
    var filterTag = document.createElement('span');
    filterTag.textContent = field + ': ' + phrase;
    filterTag.classList.add('bg-green-500', 'text-white', 'rounded-lg', 'px-2', 'py-1', 'mr-2'); // Add classes to the filter tag

    // Add a remove button to the filter tag
    var removeButton = document.createElement('button');
    removeButton.innerHTML = '&times;'; // Use the HTML entity for the multiplication symbol (×) as the "x" button
    removeButton.classList.add('ml-3'); // Add a class to the remove button
    removeButton.addEventListener('click', function(event) {
        // Stop the event from bubbling up to parent elements
        event.stopPropagation();

        // Remove the filter tag when the remove button is clicked
        filterTag.remove();
    });
    filterTag.appendChild(removeButton);

    // Add the filter tag to the filter list
    document.getElementById('filter-list').appendChild(filterTag);
});






    document.addEventListener('DOMContentLoaded', function() {
        var element = document.getElementById('modal-school');
        if (element) {
            // Retrieve the entire HTML of the element
            var htmlContent = element.outerHTML;
            // Save to local storage
            localStorage.setItem('modal-school', htmlContent);
            element.remove();
        }

        var element = document.getElementById('menu-context-school');
        if (element) {
            // Retrieve the entire HTML of the element
            var htmlContent = element.outerHTML;
            // Save to local storage
            localStorage.setItem('menu-context-school', htmlContent);
            element.remove();
        }
    });

    document.addEventListener('DOMContentLoaded', function() {
        var toggleButton = document.getElementById('toggle-inforbar');
        var infoBar = document.getElementById('inforbar');

        toggleButton.addEventListener('click', function() {
            // Check if the infoBar element exists
            if (infoBar) {
                // Toggle the 'hidden' class or any class that controls visibility
                infoBar.classList.toggle('hidden');
            }
        });
    });

    function adjustGridColumns() {
        const container = document.getElementById('display_cards');
        if (!container) return;

        const containerWidth = container.offsetWidth;
        console.log(containerWidth)
        // Remove all previous grid classes
        container.className = container.className.replace(/grid-cols-\d+/g, '');

        // Calculate the number of columns, ensuring at least 1 column
        var gridNum = Math.max(1, Math.round((containerWidth - 10) / 360));

        // Optionally, set a maximum number of columns
        const maxColumns = 5; // For example, a maximum of 5 columns
        gridNum = Math.min(gridNum, maxColumns);

        container.classList.add('grid-cols-' + gridNum); // Adjust number of columns as needed
        container.classList.remove("opacity-0")
        container.classList.add("opacity-100")
    }

    // Initial adjustment
    adjustGridColumns();
    window.addEventListener('resize', adjustGridColumns);

    // Call this in your sidebar toggle function
    // toggleSidebarFunction() { ... adjustGridColumns(); ... }


    document.addEventListener('DOMContentLoaded', function() {
        const toggleButton = document.getElementById('toggle-search');
        const dbToolBarTye2 = document.getElementById('dbtoolbar-type-2');
        const dbToolBarTye1 = document.getElementById('dbtoolbar-type-1');


        // Function to toggle the search bar
        function toggleSearchBar() {
            dbToolBarTye2.classList.remove('hidden');
            dbToolBarTye1.classList.add('hidden');
        }

        // Add event listener to the toggle button
        toggleButton.addEventListener('click', function() {
            toggleSearchBar();
        });

        // Function to check if click is outside the search bar
        function isClickOutside(event) {
            return !dbToolBarTye2.contains(event.target) && !toggleButton.contains(event.target);
        }

        // Add event listener to the document
        document.addEventListener('click', function(event) {
            if (isClickOutside(event) && !dbToolBarTye2.classList.contains('hidden')) {
                dbToolBarTye2.classList.add('hidden');
                dbToolBarTye1.classList.remove('hidden');
            }
        });
    });





// MODAL HANDLING =========================================
document.addEventListener('DOMContentLoaded', function() {

    // Use delication to make sure  new add element can be list
    document.body.addEventListener('click', function(event) {
        if (event.target.closest('#cancel-modal')) {
            var element = event.target.closest('#cancel-modal')
            removeModal(element);
        } else if (event.target.closest('#open-modal')) {
            var element = event.target.closest('#open-modal')
            var modalID = element.getAttribute('modal-id');
            //console.log(modalID);
            openLocalModal(modalID);
        }
    });

    function removeModal(button) {
        var modal = button.closest('.modal');
        modal.remove();  // Removes the modal from the DOM
    }


    function openLocalModal(modalID) {
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
            htmx.process(document.body);
        }
    }


    // Remove all modals after a swap to make sure no modals are on the screen, 
    // if there are errors from the form, new modal will be called to appear
    document.body.addEventListener('htmx:beforeSwap', function(event) {
        var modals = document.querySelectorAll('.modal');
        modals.forEach(function(modal) {
            modal.remove();
        });
    });
});




// MENU HANDLING =========================================
document.addEventListener('DOMContentLoaded', function() {
    document.body.addEventListener('click', function(event) {
        var dropdownButton = event.target.closest('.dropdown-button');
        if (dropdownButton) {
            var menuID = dropdownButton.getAttribute('menu-id');
            var dropdownMenu = document.getElementById(menuID);
            if (!dropdownMenu) {
                dropdownMenu = localStorage.getItem(menuID);
                var parser = new DOMParser();
                var doc = parser.parseFromString(dropdownMenu, 'text/html');
                dropdownMenu = doc.body.firstChild;
            }
            if (dropdownMenu) {
                moveMenu(dropdownButton, dropdownMenu);
                toggleMenu(dropdownMenu);
            }
            event.preventDefault(); // Prevent default if it's a link or a button
        }
    });

    // Move menu under the button
    function moveMenu(button, menu) {
        // Check if the button's next sibling is not the menu
        if (!(button.nextElementSibling && button.nextElementSibling.classList.contains('dropdown-menu'))) {
            // Hide the menu when moving, so that the function toggleMenu can turn it back on
            button.insertAdjacentElement('afterend', menu);
            menu.classList.add('hidden');
        }
    }

    // Toggle menu visibility
    function toggleMenu(menu) {
        if (menu.classList.contains('hidden')) {
            closeAllDropdowns();
            menu.classList.remove('hidden');
        } else {
            menu.classList.add('hidden');
        }
    }

    // Close all dropdowns function
    function closeAllDropdowns() {
        document.querySelectorAll('.dropdown-menu').forEach(menu => {
            menu.classList.add('hidden');
        });
    }

    // Global click event to close dropdowns if clicked outside
    document.addEventListener('click', function(event) {
        let isClickInsideAnyDropdownButton = Array.from(document.querySelectorAll('.dropdown-button')).some(button => button.contains(event.target));
        let isClickInsideAnyDropdownMenu = Array.from(document.querySelectorAll('.dropdown-menu')).some(menu => menu.contains(event.target));

        if (!isClickInsideAnyDropdownButton && !isClickInsideAnyDropdownMenu) {
            closeAllDropdowns();
        }
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
            console.log(recordID)
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
    const themeToggles = document.querySelectorAll('.theme-toggle');
    const storedTheme = localStorage.getItem('theme');
    function updateTheme(isDark) {
        const sunIcons = document.getElementById('sun-icon');
        const moonIcons = document.getElementById('moon-icon');
        // Update theme class
        document.documentElement.classList.toggle('dark', isDark);
        localStorage.setItem('theme', isDark ? 'dark' : 'light');

        // Update icons for all sun and moon instances
        sunIcons.forEach(sunIcon => {
            sunIcon.style.opacity = isDark ? '0' : '1';
        });
        moonIcons.forEach(moonIcon => {
            moonIcon.style.opacity = isDark ? '1' : '0';
        });
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



// SIDEBAR CONTROL =============================
document.addEventListener('DOMContentLoaded', () => {
    // SIDEBAR APPEARANCE CONTROL =========================
    const sidebarToggle = document.getElementById('sidebar-toggle');
    sidebarToggle.addEventListener('change', () => {
        const burgerActive = document.getElementById('burger-inactive-icon');
        const burgerInactive = document.getElementById('burger-active-icon');
        const sidebar = document.getElementById('sidebarLayout'); // Ensure this is the correct ID for your sidebar

        if (burgerActive.style.opacity === '1') {
            sidebar.classList.remove("-left-72");
            sidebar.classList.add("left-0");
            burgerActive.style.opacity = '0';
            burgerInactive.style.opacity = '1';
        } else {
            sidebar.classList.add("-left-72");
            sidebar.classList.remove("left-0");
            burgerActive.style.opacity = '1';
            burgerInactive.style.opacity = '0';
        }
    });

    // SIDEBAR MENU TEXT APPEARANCE CONTROL =======================f
    // Initialize a variable for the timer
    var hoverTimer;

    // Function to add event listeners if on a large screen
    function addSidebarEventListeners() {
        var menuTexts = document.querySelectorAll('.menu-text');
        // Check if the screen is large (more than 640px in width)
        if (window.innerWidth >= 640) {
            // Set defaultt display for large screen
            menuTexts.forEach(function(menuText) {
                menuText.style.opacity = "0";
            });
            sidebar.style.maxWidth = "80px";

            // Add mouseover event listener to the sidebar
            sidebar.addEventListener('mouseover', function() {
                // Set a timer for 1 second
                hoverTimer = setTimeout(function() {
                    menuTexts.forEach(function(menuText) {
                        menuText.style.opacity = "0";
                        menuText.style.opacity = "1";
                    });
                    sidebar.style.maxWidth = "200px";
                }, 200); // 200 milliseconds
            });

            // Add mouseout event listener to the sidebar
            sidebar.addEventListener('mouseout', function() {
                // Clear the timer if mouseout occurs before the timer ends
                clearTimeout(hoverTimer);

                menuTexts.forEach(function(menuText) {
                    menuText.style.opacity = "1";
                    menuText.style.opacity = "0";
                });
                sidebar.style.maxWidth = "80px";
            });
        } else {
            // Set default display for small screen
            menuTexts.forEach(function(menuText) {
                menuText.style.opacity = "1";
            });
            sidebar.style.maxWidth = "200px";
        }
    }

    // Call the function to add event listeners
    addSidebarEventListeners();

    // Optional: Recheck screen size on window resize
    window.addEventListener('resize', addSidebarEventListeners);
});