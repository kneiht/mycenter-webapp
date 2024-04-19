// CHANGE URL FOR SPA =========================================
function changeUrl(newUrl) {
    // Create a new state object (it can be anything, or even null)
    var stateObj = { foo: "bar" };
    // Use history.pushState to change the URL
    history.pushState(stateObj, "page title", newUrl);
}

// CSRF TOKEN =========================================
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');





// THEME CHANGE =========================================
up.compiler('body', function(element) {
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


// RESPONSIVE ELEMENTS ON RESIZE =========================================
up.compiler('#display_cards', function(element) {
    // Function to adjust the number of grid columns
    function adjustGridColumns() {
        const container = document.getElementById('display_cards');
        if (!container) return;

        const containerWidth = container.offsetWidth;
        // Remove all previous grid classes
        container.className = container.className.replace(/grid-cols-\d+/g, '');

        // Calculate the number of columns, ensuring at least 1 column
        var gridNum = Math.max(1, Math.round((containerWidth - 10) / 360));

        // Optionally, set a maximum number of columns
        const maxColumns = 10; // For example, a maximum of 5 columns
        gridNum = Math.min(gridNum, maxColumns);

        container.classList.add('grid-cols-' + gridNum); // Adjust number of columns as needed
        // Display the display_cards container after the grid has been adjusted for the first time  
        container.classList.remove("opacity-0")
        container.classList.add("opacity-100")
    }
    // Call this in your sidebar toggle function
    // toggleSidebarFunction() { ... adjustGridColumns(); ... }

    // Initial adjustment
    adjustGridColumns();
    window.addEventListener('resize', adjustGridColumns);
});



// MODAL HANDLING =========================================
up.compiler('.modal', function(element) {
    let modal = element;
    let cancelButton = modal.querySelector('#cancel');
    let okButton = modal.querySelector('#ok');
    if (cancelButton) {
        cancelButton.addEventListener('click', function() {
            element.remove();
        });
    }
    if (okButton) {
        okButton.addEventListener('click', function() {
            element.remove();
        });
    }
});



// CARD DROPDOWN MENU =========================================
// this code must be placed before the dropdown menu code
up.compiler('.card', function(element) {
    const card = element;
    const menuButton = element.querySelector('.menu-button');
    if (menuButton) {
        menuButton.addEventListener('click', function() {
            var menuCardContext = document.getElementById('menu-card-context');
            if (menuCardContext) {
                let recordId = card.getAttribute('record-id');

                // Update the URL for the edit link
                let recordEdit = document.getElementById('record-edit');
                if (recordEdit) {
                    let href = window.location.pathname
                    href = href + '/' + recordId + '/?get=form';
                    href = href.replace('//', '/');
                    recordEdit.setAttribute('href', href);
                }

                // Update the URL for the tuition payment link
                let payTuition = document.getElementById('pay_tuition');
                if (payTuition) {
                    let href = window.location.pathname
                    href = href + '/' + recordId + '/pay-tuition/?get=form';
                    href = href.replace('//', '/');
                    payTuition.setAttribute('href', href);
                }

                // Update the URL for attendance link
                let attendanceCalendar = document.getElementById('attendance-calendar');
                if (attendanceCalendar) {
                    href = window.location.pathname;
                    href = href + '/' + recordId + '/attendance-calendar/'
                    href = href.replace('//', '/');
                    attendanceCalendar.setAttribute('href', href);
                }
            }
            if (menuCardContext && !card.contains(menuCardContext)) {
                // Move #menu-card-context to be after the clicked element
                // Check if menuCardContext exists before trying to move it
                    menuButton.insertAdjacentElement('afterend', menuCardContext);
                    menuCardContext.classList.add('hidden');
            }

        });
    }
});

// DROPDOWN MENUS =========================================
up.compiler('.menu', function(element) {
    // Function to show a menu
    function showHideMenu(menu, action) {
        var dropdownMenu = menu.querySelector('.dropdown-menu');
        if (dropdownMenu) {
            if (action === 'show') {
                dropdownMenu.classList.remove('hidden');
            }
            else if (action === 'hide') {
                dropdownMenu.classList.add('hidden');
            }
            else if (action === 'toggle') {
                dropdownMenu.classList.toggle('hidden');
            }
        }
    }
    // Attach click event listeners to menu buttons
    element.querySelector('.menu-button').addEventListener('click', function() {
            showHideMenu(element, 'toggle')
    });

    // Hide menus when clicking outside of them
    document.addEventListener('click', function(event) {
        if (!element.contains(event.target)) {
            showHideMenu(element, 'hide')
        }
    })

});



// NAVIGATION BAR ITEMS =========================================
up.compiler('#nav_bar', function(element) {

    function activeMenuItem(item) {
        // Remove specific classes from all <a> elements within #nav_bar_left
        document.querySelectorAll('#nav_bar_left a').forEach(link => {
            link.classList.remove('border');
            link.classList.remove('bg-gray-200');
            link.classList.remove('border-gray-300');
            link.classList.remove('dark:bg-gray-800');
            link.classList.remove('dark:border-gray-700');
        });

        // Add classes to the clicked element (referred to as 'item')
        item.classList.add('bg-gray-200');
        item.classList.add('border');
        item.classList.add('border-gray-300');
        item.classList.add('dark:bg-gray-800');
        item.classList.add('dark:border-gray-700');
    }

    // Add event listener to each navigation item
    document.querySelectorAll('#nav_bar_left a').forEach(item => {
        item.addEventListener('click', function() {
            activeMenuItem(item);
        });
    });
});


function formatDropdownItem(dropdown) {
    const items = dropdown.children;
    for (let i = 0; i < items.length; i++) {
        const item = items[i];
 
        if (i === 0) {
            // First item
            item.classList.add('menu-item', 'menu-border', 'rounded-t-xl');
            if (items.length === 1) {
                item.classList.add('rounded-b-xl');
            }
        } else if (i === items.length - 1) {
            // Last item
            item.classList.add('menu-item', 'rounded-b-xl');
        } else {
            // Middle items
            item.classList.add('menu-item', 'menu-border');
        }
    }
}
// FORMAT DROPDOWN-MENU =========================================
up.compiler('.dropdown-menu', function(element) {
    const dropdown = element;
    formatDropdownItem(dropdown);
 });


// RESPONSIVE NAV BAR =========================================
up.compiler('#nav_bar', function(element) {
    const navbar = element;
    const navMenu = document.getElementById('nav_menu');
    const moreMenu = document.getElementById('nav_menu_more'); // Ensure this is the correct container within nav_menu_more
    const moreMenuDropdown = navbar.querySelector('.dropdown-menu'); // Ensure this is the correct container within nav_menu_more
    const menuSchool = document.getElementById('menu-school');
    const spaceAtLeast = 100; // Minimum space required to keep an item on the navbar
    
    // Function to calculate the space left on the navbar
    function calculateSpaceLeft() {
        const navbarWidth = navbar.offsetWidth; // Get the navbar's total width
        let totalItemsWidth = 0;
        const items = navbar.children; // Get all child elements (links) in the navbar
    
        for (let item of items) {
            totalItemsWidth += item.offsetWidth; // Sum up the width of each item
            totalItemsWidth += parseInt(window.getComputedStyle(item).marginRight, 10); // Add marginRight to the total
        }
        let spaceLeft = navbarWidth - totalItemsWidth; // Calculate the space left
        return spaceLeft;
    }

    function moveItemToMoreMenu() {
        // Check if there are at least two children to ensure the "More" menu isn't moved
        if (navMenu.children.length > 1) {
            const secondLastChild = navMenu.children[navMenu.children.length - 2];
            moreMenuDropdown.insertBefore(secondLastChild, moreMenuDropdown.firstChild); // Move the second-last nav item into the More menu
            
        }
    }
    
    function calculateSpaceWithItem(item) {
        const spaceLeft = calculateSpaceLeft();
        const itemWidth = item.offsetWidth + parseInt(window.getComputedStyle(item).marginRight, 10);
        return spaceLeft - itemWidth; // Calculate space left after adding the item
    }
    
    function restoreItemFromMoreMenu() {
        if (moreMenuDropdown.children.length > 0) {
            const firstMoreMenuItem = moreMenuDropdown.children[0];
            // Pre-calculate space with the item that will be restored
            const spaceLeftWithItem = calculateSpaceWithItem(firstMoreMenuItem);
    
            // Only move the item back if there's enough space
            if (spaceLeftWithItem >= 0) {
                navMenu.insertBefore(firstMoreMenuItem, navMenu.children[navMenu.children.length - 1]); // Insert before the More menu
            }
        }
    }
    

    function adjustNavbarItems() {
        let spaceLeft = calculateSpaceLeft();
        //console.log('Space left:', spaceLeft, 'px');
        
        // Attempt to restore items from the More menu if there's enough space
        // Check if there's an item to restore and if the space with the item would be sufficient
        while (moreMenuDropdown.children.length > 0 && spaceLeft >= spaceAtLeast) {
            const firstMoreMenuItem = moreMenuDropdown.children[0]; // Get the first item from More menu for calculation
            const spaceLeftWithItem = calculateSpaceWithItem(firstMoreMenuItem); // Calculate space if the item were restored
            //console.log('Space left with item:', spaceLeftWithItem, 'px');
            // Only restore the item if there's enough space for it
            if (spaceLeftWithItem >= 0) {
                restoreItemFromMoreMenu();
                spaceLeft = calculateSpaceLeft(); // Recalculate space left after restoring an item
            } else {
                break; // If not enough space for this item, stop trying to restore more
            }
        }

        // Continuously move items to the More menu if there's not enough space
        while (spaceLeft < spaceAtLeast && navMenu.children.length > 1) { // Ensure at least 2 children to keep the More menu
            //console.log('Space left on navbar:', spaceLeft, 'px');
            moveItemToMoreMenu();
            spaceLeft = calculateSpaceLeft(); // Recalculate space left after moving an item
        }

        // If the spaceLeft is less than 40px, change width of the menu-schools
        if (navbar.offsetWidth < 800) {
            //remove  width style from the menu-school
            menuSchool.style.width = 'auto';
            // Move the menu-school after nav_bar in the parent
            navbar.parentNode.insertBefore(menuSchool, navbar.nextSibling);
        }
        else {
            //restore the width style of the menu-school
            menuSchool.style.width = '400px';
            // Move the menu-school after nav_bar_left
            const narBarLeft = navbar.querySelector('#nav_bar_left')
            navbar.insertBefore(menuSchool, narBarLeft.nextSibling);

            
            
        }

        // If nav_menu_more is empty, hide the More menu
        if (moreMenuDropdown.children.length === 0) {
            moreMenu.classList.add('hidden');
        } else {
            moreMenu.classList.remove('hidden');
        }
    }
    

    // Initial adjustment
    if (menuSchool) { 
        // document loaded
        window.addEventListener('load', adjustNavbarItems);
        window.addEventListener('resize', adjustNavbarItems);
    }
    navbar.classList.remove("opacity-0")
    navbar.classList.add("opacity-100")

});





// FILTER  BAR =========================================
// Hide search bar when clicking ouside

document.addEventListener('click', function(event) {
    const searchControl = document.getElementById('search-control')
    const toolBar = document.getElementById('db-tool-bar')
    if (!toolBar.contains(event.target) && searchControl) {
        document.getElementById('filter-list').classList.add('hidden');
        document.getElementById('search-bar').classList.add('max-sm:hidden');
        document.getElementById('toggle-search').classList.remove('hidden');
        document.getElementById('sort-button').classList.remove('hidden');
        document.getElementById('right-controls').classList.remove('hidden');
    }
});



up.compiler('#db-tool-bar', function(element) {
    const toolBar = element
    const searchControl = document.getElementById('search-control')
    if (!searchControl) {
        return;
    }
    // Toggle search bar visibility on small screens
    document.getElementById('toggle-search').addEventListener('click', function() {
        document.getElementById('filter-list').classList.remove('hidden');
        document.getElementById('search-bar').classList.remove('max-sm:hidden');
        document.getElementById('toggle-search').classList.add('hidden');
        document.getElementById('sort-button').classList.add('hidden');
        document.getElementById('right-controls').classList.add('hidden');
    });
    
    // Toggle information bar visibility
    document.getElementById('toggle-infor-bar').addEventListener('click', function() {
        const infoBar = document.getElementById('infor-bar');
        if (infoBar) {
            infoBar.classList.toggle('hidden');
        }
    });

    // Show filter list when clicking to filter input
    document.getElementById('filter-input').addEventListener('click', function() {
        document.getElementById('filter-list').classList.remove('hidden');
    });

    document.getElementById('filter-select').addEventListener('change', function() {
        const filterSelectValue = this.value;
        document.getElementById('filter-input').setAttribute('name', filterSelectValue);
    });

    // Add filter button functionality
    document.getElementById('add-filter-button').addEventListener('click', function() {
        const filterInput = document.getElementById('filter-input');
        const filterList = document.getElementById('filter-list');
        const filterSelect = document.getElementById('filter-select');
        const filterValue = filterInput.value.trim();
        const filterField = filterSelect.value;

        if (filterValue !== '') {
            const filterTag = document.createElement('span');
            filterTag.className = 'filter-tag bg-green-500 text-white rounded-lg px-2 py-1 mr-2 hover:bg-red-600 cursor-pointer';
            filterTag.textContent = `${filterField}:${filterValue}`;
            filterTag.addEventListener('click', function() {
                filterList.removeChild(filterTag);
            });

            const hiddenInput = document.createElement('input');
            hiddenInput.type = 'hidden';
            hiddenInput.value = filterValue;
            hiddenInput.name = filterField;

            filterTag.appendChild(hiddenInput);
            filterList.appendChild(filterTag);
            filterList.classList.remove('hidden');

            filterInput.value = ''; // Clear the input after adding the tag
        }
    });

    // Clear all filter tags only
    document.getElementById('clear-filter-button').addEventListener('click', function() {
        const filterTags = document.querySelectorAll('#filter-list .filter-tag');
        filterTags.forEach(filterTag => {
            filterTag.remove();
        });
    });
});



// ATTENDANCANCE FORM =========================================
up.compiler('#id_use_price_per_hour_from_class', function(element) {
    const usePricePerHourFromClass = element;
    const pricePerHour = document.getElementById('id_price_per_hour');
    // if usePricePerHourFromClass is checked, disable pricePerHour else enable
    togglePricePerHour();
    usePricePerHourFromClass.addEventListener('change', function() {
        togglePricePerHour();
    });

    function togglePricePerHour() {
        if (usePricePerHourFromClass.checked) {
            pricePerHour.disabled = true
        } else {
            pricePerHour.disabled = false;
        }
    }
});


up.compiler('.modal', function(element) {
    // when the url has "attendance-calendar" in the url, reload when the button ok is pressed
    document.getElementById('ok').addEventListener('click', function() {
        if (window.location.href.includes('attendance-calendar')) {
            up.reload('#display_attendance_calendar')
        }
    });
});
