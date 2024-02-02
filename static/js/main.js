class CardStyler {
    constructor() {
        // Splitting the class names into an array for easier manipulation
        this.rewardClasses = 'reward bg-yellow-300 dark:bg-yellow-700';
        this.presentAttendanceClasses = 'present bg-green-300 dark:bg-green-700';
        this.absentAttendanceClasses = 'absent bg-red-300 dark:bg-red-700';
        this.lateAttendanceClasses = 'late bg-blue-300 dark:bg-blue-700';
        this.leftEarlyAttendanceClasses = 'left-early bg-purple-300 dark:bg-purple-700';
        this.attendanceClassesSet = this.presentAttendanceClasses + ' ' + 
                                    this.absentAttendanceClasses + ' ' + 
                                    this.lateAttendanceClasses + ' ' + 
                                    this.leftEarlyAttendanceClasses;
        
    }
    toggleCard(card) {toggleClass(card, this.rewardClasses);}
    selectCard(card) {addClass(card, this.rewardClasses);}
    deselectCard(card) {removeClass(card, this.rewardClasses);}
    clearAttendanceClasses(card) {removeClass(card, this.attendanceClassesSet);}
    circleAttendanceState(card) {
        // Get the current class name
        let currentClass = card.classList;
        if (currentClass.contains('present')) {
            removeClass(card, this.presentAttendanceClasses);
            addClass(card, this.absentAttendanceClasses);
        }
        else if (currentClass.contains('absent')) {
            removeClass(card, this.absentAttendanceClasses);
            addClass(card, this.lateAttendanceClasses);
        }
        else if (currentClass.contains('late')) {
            removeClass(card, this.lateAttendanceClasses);
            addClass(card, this.leftEarlyAttendanceClasses);
        }
        else if (currentClass.contains('left-early')) {
            removeClass(card, this.leftEarlyAttendanceClasses);
            addClass(card, this.presentAttendanceClasses);
        }
        else {
            addClass(card, this.presentAttendanceClasses);
        }
    }
}



// CHECK ATTTENDANCE STUDENTS =========================================
document.addEventListener('DOMContentLoaded', function() {

    function sendAttendance() {
        // Correcting the typo in the selector from 'current-school-infor' to 'current-school-info'
        let schoolId = document.querySelector('#current-school-infor').getAttribute('school-id');
    
        // A helper function to collect student IDs based on attendance status
        function collectStudentIds(status) {
            return Array.from(document.querySelectorAll(`#display_cards .${status}`))
                        .map(card => card.getAttribute('record-id'))
                        .join('-');
        }
    
        // Collecting student IDs for each attendance status
        let present_students = collectStudentIds('present');
        let absent_students = collectStudentIds('absent');
        let late_students = collectStudentIds('late');
        let left_early_students = collectStudentIds('left-early');
    
        // Building the URL with template literals
        let url = `/attendances/class/?school_id=${schoolId}&present=${present_students}&absent=${absent_students}&late=${late_students}&left_early=${left_early_students}`;
    
        // Assuming HTMX is correctly set up in your project
        htmx.ajax('POST', url, {swap: 'afterbegin'});
    }
    
    let confirmAttendanceButton = document.querySelector('#button-confirm-attendance');
    confirmAttendanceButton.addEventListener('click', function() {
        sendAttendance();

    });

    const cardStyler = new CardStyler();
    let attendanceControls = document.querySelector('#attendance-controls');
    let attendanceButton = document.querySelector('#attendance-button');
    // Set the attendance controls to inactive when first loaded
    attendanceControls.setAttribute('active', 'false');
    attendanceButton.addEventListener('click', function() {
        if (attendanceControls.getAttribute('active') === 'false') {
            attendanceControls.setAttribute('active', 'true');
            attendanceControls.classList.remove('hidden');
        }
        else {
            document.querySelectorAll('#display_cards .card').forEach(card => {
                cardStyler.clearAttendanceClasses(card);
            });
            attendanceControls.setAttribute('active', 'false');
            attendanceControls.classList.add('hidden');
        }
    });
    document.querySelectorAll('#display_cards .card').forEach(card => {
        card.addEventListener('click', function() {
            if (attendanceControls.getAttribute('active') === 'true') {
                cardStyler.circleAttendanceState(card);
            }
        })
    });

});



// REWARD STUDENTS =========================================
document.addEventListener('DOMContentLoaded', function() {
    function selectStudents(selectorOrElement, action) {
        if (document.querySelector('#reward-controls').getAttribute("active") === "true") {
            if (typeof selectorOrElement === 'string') {
                cards = document.querySelectorAll(selectorOrElement);
            } else if (selectorOrElement instanceof Element) {
                cards = [selectorOrElement];
            }
            const cardStyler = new CardStyler();
            cards.forEach(card => {
                switch (action) {
                    case "toggle":
                        cardStyler.toggleCard(card);
                        break;
                    case "select":
                        cardStyler.selectCard(card);
                        break;
                    case "deselect":
                        cardStyler.deselectCard(card);
                        break;
                }
            });
        }
    }

    function reward(upOrDown) {
        // Assuming `schoolId` is available as a data attribute on an element with the ID `current-school-info`
        let schoolId = document.querySelector('#current-school-infor').getAttribute("school-id");
        
        // Getting the value of the stars input
        let rewardPoints = document.querySelector('#stars').value;
        
        if (upOrDown === 'down') {
            rewardPoints = rewardPoints * -1;
        }
        // A helper function to collect student IDs based on attendance status
        let students = Array.from(document.querySelectorAll(`#display_cards .reward`))
                        .map(card => card.getAttribute('record-id'))
                        .join('-');
        
        let url = `/students/reward/?school_id=${schoolId}&reward_points=${rewardPoints}&students=${students}`;
        
        // Using HTMX to make the POST request
        htmx.ajax('POST', url, {swap: 'afterbegin'});
    }

    let rewardControls = document.querySelector('#reward-controls');
    let attendanceButton = document.querySelector('#attendance-button');
    // Set the reward controls to active when first loaded, it then is conrolled by attendace check
    rewardControls.setAttribute('active', 'true');
    attendanceButton.addEventListener('click', function() {
        if (rewardControls.getAttribute('active') === 'false') {
            rewardControls.setAttribute('active', 'true');
            rewardControls.classList.remove('hidden');
        }
        else {
            selectStudents('#display_cards .card', "deselect");
            rewardControls.setAttribute('active', 'false');
            rewardControls.classList.add('hidden');
        }
    });

    // Add event listener to each card
    document.querySelectorAll('#display_cards .card').forEach(card => {
        card.addEventListener('click', function() {
            // Select the card
            selectStudents(card, "toggle");
        });
    });
    document.querySelector('#select-all').addEventListener('click', function() {
        // Select all cards
        selectStudents('#display_cards .card', "select");
    });
    document.querySelector('#deselect-all').addEventListener('click', function() {
        // Deselect all cards
        selectStudents('#display_cards .card', "deselect");
    });
    document.querySelector('#select-reverse').addEventListener('click', function() {
        // Select reserve cards
        selectStudents('#display_cards .card', "toggle");
    });

    document.querySelector('#wow').addEventListener('click', function() {
        // Reward the selected students
        reward('up');
    });
    document.querySelector('#oh-no').addEventListener('click', function() {
        // Un-reward the selected students
        reward('down');
    });

});





// NAVIGATION BAR ITEMS =========================================
document.addEventListener('DOMContentLoaded', function() {
    function activeMenuItem(item) {
        console.log('activeMenuItem');
        // Remove specific classes from all <a> elements within #nav-bar-left
        document.querySelectorAll('#nav-bar-left a').forEach(link => {
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

        // Get the school-id attribute from #current-school-info
        const schoolId = document.querySelector('#current-school-info').getAttribute('school-id');

        // Construct the URL
        const url = '/school/' + schoolId;

        // Function to change the URL (assuming changeUrl is defined elsewhere)
        changeUrl(url);
    }

    // Add event listener to each navigation item
    document.querySelectorAll('#nav-bar-left a').forEach(item => {
        item.addEventListener('click', function() {
            activeMenuItem(item);
        });
    });
});


// CHANGE URL FOR SPA =========================================
function changeUrl(newUrl) {
    // Create a new state object (it can be anything, or even null)
    var stateObj = { foo: "bar" };
    // Use history.pushState to change the URL
    history.pushState(stateObj, "page title", newUrl);
}




// RESPONSIVE ELEMENTS ON RESIZE =========================================
document.addEventListener('DOMContentLoaded', function() {
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




// ADD, REMOVE, TOGGLE, CLICK ELSEWHERE =========================================
function modifyClass(selectorOrElement, classNames, operation) {
    let elements;
    if (typeof selectorOrElement === 'string') {
        elements = document.querySelectorAll(selectorOrElement);
    } else if (selectorOrElement instanceof Element) {
        elements = [selectorOrElement];
    } else {
        // Handle cases where selectorOrElement is neither a string nor an Element
        console.error('selectorOrElement must be a string or an Element');
        return;
    }
    
    elements.forEach(element => {
        // Split string of class names into an array if classNames is a string
        if (typeof classNames === 'string') {
            classNames = classNames.split(' '); // This will create an array of class names
        }
    
        if (Array.isArray(classNames)) {
            switch (operation) {
                case 'add': element.classList.add(...classNames); break;
                case 'remove': element.classList.remove(...classNames); break;
                // Handle toggle for each class name individually for compatibility
                case 'toggle': classNames.forEach(className => element.classList.toggle(className)); break;
                default: console.error('Invalid operation');
            }
        }
    });
}
// Usage examples
function addClass(selectorOrElement, classNames) {
    modifyClass(selectorOrElement, classNames, 'add');
}
function removeClass(selectorOrElement, classNames) {
    modifyClass(selectorOrElement, classNames, 'remove');
}
function toggleClass(selectorOrElement, classNames) {
    modifyClass(selectorOrElement, classNames, 'toggle');
}

function setupClickElsewhereListener(element) {
    // This function now accepts an element to attach the click listener to
    document.addEventListener('click', function(event) {
        var menuSchool = document.getElementById('menu-school');
        // Check if the click is outside the passed element
        if (element && !element.contains(event.target)) {
            menuSchool.classList.add('hidden');
        }
    });
}



// DROPDOWN MENUS =========================================
document.addEventListener('DOMContentLoaded', function() {
    // Get all elements with class "menu"
    var menus = document.querySelectorAll('.menu');

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
    menus.forEach(function(menu) {
        var button = menu.querySelector('.menu-button');
        button.addEventListener('click', function() {
            showHideMenu(menu, 'toggle')
        });
    });

    // Hide menus when clicking outside of them
    document.addEventListener('click', function(event) {
        menus.forEach(function(menu) {
            if (!menu.contains(event.target)) {
                showHideMenu(menu, 'hide')
            }
        });
    });

});



// CHANNGE QUICK SETTINGS POSITION ON RESIZE =========================================
document.addEventListener('DOMContentLoaded', function() {
    // Get a reference to the quick-settings element
    var quickSettings = document.getElementById('quick-settings');

    function changePosition() {
        console.log('changePosition');
        // Measure the #nav-bar element
        var navBar = document.querySelector('#nav-bar');
        var navBarWidth = navBar.offsetWidth;

        // Get references to the elements
        var profileMenu = document.querySelector('#menu-profile');
        var profile = document.querySelector('#profile');
        var item1 = document.querySelector('#item-1');
        var item2 = document.querySelector('#item-2');

        // Check the width of #nav-bar and apply the logic accordingly
        if (navBarWidth > 639) {
            quickSettings.classList.remove('w-full');
            var parent = profile.parentNode;
            parent.insertBefore(quickSettings, profile);
            item2.classList.add('rounded-t-xl');
            item1.classList.add('hidden');
        } else {
            quickSettings.classList.add('w-full');
            item1.appendChild(quickSettings);
            item2.classList.remove('rounded-t-xl');
            item1.classList.remove('hidden');
        }

        // Remove the 'hidden' class from me
        quickSettings.classList.remove('hidden');
    }

    // Initial adjustment
    changePosition();
    window.addEventListener('resize', changePosition);
});