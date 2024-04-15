
// Sounds preloaded
var successSound = new Audio("/static/sound/success.mp3");
var failSound = new Audio("/static/sound/fail.mp3");




up.compiler('#modal', function(element) {
    let modal = element
    // if get data-message-type
    let messageType = modal.getAttribute('message-type');
    if (messageType!=="reward-up" && messageType!=="reward-down") {
        return;
    }

    function playSound(isSuccess) {
        if (isSuccess) {
            successSound.play();
        } else {
            failSound.play();
        }
    }

    if (messageType === "reward-up") {
        playSound(true);
        var successImagesList = document.getElementById('success-image-list').getElementsByTagName('img');
        var randomSuccessImage = successImagesList[Math.floor(Math.random() * successImagesList.length)];
        // replace the image with the random image by puttingn the image to card-image-container
        var cardImageContainer = modal.querySelector('.meme-container img');
        cardImageContainer.src = randomSuccessImage.src;
    } else if (messageType === "reward-down") {
        playSound(false);
        var failImagesList = document.getElementById('fail-image-list').getElementsByTagName('img');
        var randomFailImage = failImagesList[Math.floor(Math.random() * failImagesList.length)];
        var cardImageContainer = modal.querySelector('.meme-container img');
        cardImageContainer.src = randomFailImage.src;
    }

    setTimeout(() => {
        modal.querySelector('.modal').remove();
    }, 5000);
})





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





// CARD STYLES =========================================
class CardStyler {
    constructor() {
        // Splitting the class names into an array for easier manipulation
        this.shake = 'shake';
        this.rewardClasses = 'reward';
        this.presentAttendanceClasses = 'present';
        this.absentAttendanceClasses = 'absent';
        this.lateAttendanceClasses = 'late';
        this.leftEarlyAttendanceClasses = 'left-early';
        this.notCheckedAttendanceClasses = 'not-checked';
        this.grayoutedAttendanceClasses = 'grayouted';
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
    shakeOnCard(card) {addClass(card, this.shake);}
    shakeOffCard(card) {removeClass(card, this.shake);}
    applyGrayoutedClasses(card) {addClass(card, this.grayoutedAttendanceClasses);}
    clearGrayoutedClasses(card) {removeClass(card, this.grayoutedAttendanceClasses);}


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
up.compiler('#attendance-controls', function(element) {
    
    let checkDate = document.querySelector('#check_date');
    // check if there is check_date in params, if yes, set the value of checkDate to it
    let urlParams = new URLSearchParams(window.location.search);
    let check_date = urlParams.get('check_date');
    if (check_date) {
        checkDate.value = check_date;
    }
    else {
        checkDate.value = new Date().toISOString().slice(0, 10);
    }

    checkDate.addEventListener('change', function() {
        let url = window.location.href.split('?')[0] + `?check_date=${checkDate.value}`;
        up.render({url: url, method: 'get', target: ':main', history: 'true', })
    });
    
    // Function to fetch attendance data
    async function fetchAndApplyAttendanceData(classId, checkDate) {
        try {
            const url = window.location.href.split('?')[0] + `?get=attendance&check_date=${checkDate}`;
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            const data = await response.json();
            if (data.status === 'success') {
                //console.log('got data:', data.attendance_data);
                applyAttendanceStyles(data.attendance_data);
            } else {
                console.error('Failed to fetch data:', data.message);
            }
        } catch (error) {
            console.error('Error fetching attendance data:', error);
        }
    }


    function applyGrayoutedClasses() {
        const cardStyler = new CardStyler();
        // only card with class 'not-checked' and 'absent' will be grayouted

        document.querySelectorAll('#display_cards .card').forEach(card => {
            if (card.classList.contains('not-checked') || card.classList.contains('absent')) {
                cardStyler.applyGrayoutedClasses(card);
            }
        });
    }

    // Function to apply attendance styles
    function applyAttendanceStyles(attendanceData) {
        const cardStyler = new CardStyler();
        //console.log('attendanceData:', attendanceData);
        attendanceData.forEach(student => {
            let card = document.querySelector(`#record_${student.id}`);
            //console.log(`#record_${student.student_id}`);
            if (card) {
                cardStyler.clearAttendanceClasses(card);
                if (student.status) {
                    cardStyler.applyStatus(card, student.status);
                }
            }
        });
        // get the cards which are not in the attendance data
        const cardsInAttendanceData = new Set(attendanceData.map(student => student.id));
        document.querySelectorAll('#display_cards .card').forEach(card => {
            if (!cardsInAttendanceData.has(card.getAttribute('record-id'))) {
                cardStyler.clearAttendanceClasses(card);
                cardStyler.applyStatus(card, 'not-checked');
            }
        })
    }


    function sendAttendance() {
        // Correcting the typo in the selector from 'current-school-infor' to 'current-school-info'
        let classId = document.querySelector('#class-infor').getAttribute('class-id');
        let checkDate = document.querySelector('#check_date').value;
        let learningHours = document.querySelector('#learning_hours').value;
        //console.log('classId:', classId, 'checkDate:', checkDate);
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
            'present': present_students,
            'absent': absent_students,
            'late': late_students,
            'left_early': left_early_students,
            'learning_hours': learningHours,
        };
        //console.log('formData:', formData);
        const url = window.location.href.split('?')[0] + `?post=attendance&check_date=${checkDate}`;
        up.render({
            url: url,
            method: 'post',
            headers: {'X-CSRFToken': csrftoken,},
            params: formData,
            target: ':none',
        });
    }
    
    let confirmAttendanceButton = document.querySelector('#button-confirm-attendance');
    confirmAttendanceButton.addEventListener('click', function() {
        sendAttendance();
    });

    const cardStyler = new CardStyler();
    let attendanceControls = document.querySelector('#attendance-controls');
    let attendanceButton = document.querySelector('#attendance-button');
    let cancelAttendanceButton = document.querySelector('#button-cancel-attendance');
    // Set the attendance controls to inactive when first loaded
    attendanceControls.setAttribute('active', 'false');
    attendanceButton.addEventListener('click', function() {
        if (attendanceControls.getAttribute('active') === 'false') {
            attendanceControls.setAttribute('active', 'true');
            attendanceControls.classList.remove('hidden');
            // Fetch attendance data
            let classId = document.querySelector('#class-infor').getAttribute('class-id');
            let checkDate = document.querySelector('#check_date').value;
            
            if (checkDate === '') {
                checkDate = new Date().toISOString().split('T')[0];
            }
            //console.log('classId:', classId, 'checkDate:', checkDate);
            fetchAndApplyAttendanceData(classId, checkDate);
            document.querySelectorAll('#display_cards .card').forEach(card => {
                cardStyler.clearGrayoutedClasses(card);
            });

        }
        else {
            applyGrayoutedClasses();
            document.querySelectorAll('#display_cards .card').forEach(card => {
                cardStyler.clearAttendanceClasses(card);
            });
            attendanceControls.setAttribute('active', 'false');
            attendanceControls.classList.add('hidden');
        }
    });

    cancelAttendanceButton.addEventListener('click', function() {
        // perform pressing on attendance button to cancel attendance
        attendanceButton.click();
    });


    document.querySelector('#display_cards').addEventListener('click', function(event) {
        // Select card
        const card = event.target.closest('.card');
        if (attendanceControls.getAttribute('active') === 'true') {
            cardStyler.circleAttendanceState(card);
        }
    });
});



// REWARD STUDENTS =========================================
up.compiler('#reward-controls', function(element) {
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

        // Getting the value of the reward_points input
        let rewardPoints = document.querySelector('#reward_points').value;
        // if rewardPoints is 0, do nothing
        if (rewardPoints === '0') {
            // show browser message "The reward points must not be 0"
            window.alert("The reward points must not be 0");
            return;
        }

        if (upOrDown === 'down') {
            rewardPoints = rewardPoints * -1;
        }
        // A helper function to collect student IDs based on attendance status
        let students = Array.from(document.querySelectorAll(`#display_cards .reward`))
                        .map(card => card.getAttribute('record-id'))
                        .join('-');

        let checkDate = document.querySelector('#check_date');
        let url = window.location.href.split('?')[0] + `?post=reward&check_date=${checkDate.value}&reward_points=${rewardPoints}&students=${students}`;

        up.render({
            url: url, 
            method: 'post', 
            headers: {'X-CSRFToken': csrftoken,},
            target: ':none',
        })
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

    document.querySelector('#select-all').addEventListener('click', function() {
        // Select all cards
        selectStudents('#display_cards .card:not(.grayouted)', "select");
    });
    document.querySelector('#deselect-all').addEventListener('click', function() {
        // Deselect all cards
        selectStudents('#display_cards .card', "deselect");
    });
    document.querySelector('#select-reverse').addEventListener('click', function() {
        // Select reserve cards
        selectStudents('#display_cards .card', "toggle");
        selectStudents('#display_cards .grayouted', "deselect");
    });

    document.querySelector('#display_cards').addEventListener('click', function(event) {
        // Select card
        const card = event.target.closest('.card');
        if (card) {
            selectStudents(card, "toggle");
        }
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


