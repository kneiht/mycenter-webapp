// CHANGE URL FOR SPA =========================================
function changeUrl(newUrl) {
    // Create a new state object (it can be anything, or even null)
    var stateObj = { foo: "bar" };
    // Use history.pushState to change the URL
    history.pushState(stateObj, "page title", newUrl);
}


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



// CHANNGE QUICK SETTINGS POSITION ON RESIZE =========================================
up.compiler('#quick-settings', function(element) {
    // Get a reference to the quick-settings element
    var quickSettings = element;

    function changePosition() {
        console.log('changePosition');
        // Measure the #nav-bar element
        var navBar = document.querySelector('#nav_bar');
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



// CARD STYLES =========================================
class CardStyler {
    constructor() {
        // Splitting the class names into an array for easier manipulation
        this.rewardClasses = 'reward bg-yellow-300 dark:bg-yellow-700';
        this.presentAttendanceClasses = 'present bg-green-300 dark:bg-green-700';
        this.absentAttendanceClasses = 'absent bg-red-300 dark:bg-red-700';
        this.lateAttendanceClasses = 'late bg-blue-300 dark:bg-blue-700';
        this.leftEarlyAttendanceClasses = 'left-early bg-purple-300 dark:bg-purple-700';
        this.notCheckedAttendanceClasses = 'not-checked bg-gray-300 dark:bg-gray-700';
        this.attendanceClassesSet = this.presentAttendanceClasses + ' ' + 
                                    this.absentAttendanceClasses + ' ' + 
                                    this.lateAttendanceClasses + ' ' + 
                                    this.leftEarlyAttendanceClasses + ' ' +
                                    this.netCheckedAttendanceClasses;
        
    }
    toggleCard(card) {toggleClass(card, this.rewardClasses);}
    selectCard(card) {addClass(card, this.rewardClasses);}
    deselectCard(card) {removeClass(card, this.rewardClasses);}
    clearAttendanceClasses(card) {removeClass(card, this.attendanceClassesSet);}

    applyStatus(card, status) {
        this.clearAttendanceClasses(card);
        if (status === 'present') {
            addClass(card, this.presentAttendanceClasses);
        }
        else if (status === 'absent') {
            addClass(card, this.absentAttendanceClasses);
        }
        else if (status === 'late') {
            addClass(card, this.lateAttendanceClasses);
        }
        else if (status === 'left-early') {
            addClass(card, this.leftEarlyAttendanceClasses);
        }
        else {
            addClass(card, this.notCheckedAttendanceClasses);
        }
    }

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
            this.clearAttendanceClasses(card);
            addClass(card, this.presentAttendanceClasses);
        }
    }
}



// CHECK ATTTENDANCE STUDENTS =========================================
document.addEventListener('DOMContentLoaded', function() {
    // Function to fetch attendance data
    async function fetchAndApplyAttendanceData(classId, checkDate) {
        try {
            const response = await fetch(`/attendances/by-class/?class_id=${classId}&check_date=${checkDate}`);
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            const data = await response.json();
            if (data.status === 'success') {
                console.log('got data:', data.attendance_data);
                applyAttendanceStyles(data.attendance_data);
            } else {
                console.error('Failed to fetch data:', data.message);
            }
        } catch (error) {
            console.error('Error fetching attendance data:', error);
        }
    }

    // Function to apply attendance styles
    function applyAttendanceStyles(attendanceData) {
        const cardStyler = new CardStyler();
        console.log('attendanceData:', attendanceData);
        attendanceData.forEach(student => {
            let card = document.querySelector(`#record_${student.id}`);
            console.log(`#record_${student.student_id}`);
            if (card) {
                cardStyler.clearAttendanceClasses(card);
                if (student.status) {
                    cardStyler.applyStatus(card, student.status);
                }
            }
        });
    }


    function sendAttendance() {
        // Correcting the typo in the selector from 'current-school-infor' to 'current-school-info'
        let schoolId = document.querySelector('#current-school-infor').getAttribute('school-id');
        let classId = document.querySelector('#class-infor').getAttribute('class-id');
        let checkDate = document.querySelector('#attendance-check-date').value;

        console.log('schoolId:', schoolId, 'classId:', classId, 'checkDate:', checkDate);
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
    
        // Creating FormData object to send data
        let formData = {
            'check_date': checkDate,
            'school_id':schoolId,
            'class_id':classId,
            'present': present_students,
            'absent': absent_students,
            'late': late_students,
            'left_early': left_early_students
        };
        console.log('formData:', formData);
        // Sending the request with FormData using HTMX
        htmx.ajax('POST', '/attendances/class/', {
            values: formData,
            swap: 'afterbegin'
        });
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
            // Fetch attendance data
            let classId = document.querySelector('#class-infor').getAttribute('class-id');
            let checkDate = document.querySelector('#attendance-check-date').value;
            
            if (checkDate === '') {
                checkDate = new Date().toISOString().split('T')[0];
            }
            console.log('classId:', classId, 'checkDate:', checkDate);
            fetchAndApplyAttendanceData(classId, checkDate);

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
up.compiler('#nav_bar', function(element) {
    function activeMenuItem(item) {
        console.log('activeMenuItem');
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

        // Get the school-id attribute from #current-school-info
        const schoolId = document.querySelector('#current-school-info').getAttribute('school-id');

        // Construct the URL
        const url = '/school/' + schoolId;

        // Function to change the URL (assuming changeUrl is defined elsewhere)
        changeUrl(url);
    }

    // Add event listener to each navigation item
    document.querySelectorAll('#nav_bar_left a').forEach(item => {
        item.addEventListener('click', function() {
            activeMenuItem(item);
        });
    });
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
    element.querySelector('#cancel').addEventListener('click', function() {
        element.remove();
    });
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
                let recordEdit = document.getElementById('record-edit');
                let href = recordEdit.getAttribute('href');
                // Remove the number from the URL
                let parts = href.replace('/?get=form','').split('/');
                parts.pop();
                href = parts.join('/');

                href = href + '/' + recordId + '/?get=form';
                console.log('href:', href);
                recordEdit.setAttribute('href', href);
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


