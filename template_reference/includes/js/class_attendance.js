<script>
$(document).ready(function() {
    let isAttendanceButtonClicked = false;  // Flag to track if the attendance button was clicked
    const attendanceColors = {
        'not_checked': 'grey',
        'present': 'lightgreen',
        'absent': 'tomato',
        'late': 'lightblue',
        'left_early': 'plum',
    };
    const colorToStatus = {
        'rgb(128, 128, 128)': 'not_checked', // grey
        'rgb(144, 238, 144)': 'present',     // lightgreen
        'rgb(255, 99, 71)': 'absent',        // tomato
        'rgb(173, 216, 230)': 'late',        // lightblue
        'rgb(221, 160, 221)': 'left_early',  // plum
    };

    // Get neccessary vals
    const classId = '{{ class.id }}';  // class ID
    const date = $('#attendance-date').val();  // Use the current value in the date input

    applyGrayout();

    $('#attendanceButton').on('click', function() {
        isAttendanceButtonClicked = true;  // Set the flag to true when attendance button is clicked
        if (date) {
            fetchAttendanceData(classId, date)
                .then(attendanceData => {
                    // Use the attendance data here
                    //console.log(attendanceData);
                    updateStudentCardsWithAttendance(attendanceData)
                })
                .catch(error => {
                    // Handle errors here
                    console.error("Fetching attendance data failed:", error);
                });

        } else {
            console.error('Date is required to fetch attendance data');
        }
        $('#moneyControlBar').hide();
        $('#attendanceControlBar').show();
        
    });

    $('#confirmAttendanceBtn').on('click', function() {
        const learningHours = $('#learningHours').val();
        // Check if learning hours are selected
        if (!learningHours) {
            alert("Please select learning hours."); // Show an alert or a user-friendly message
            return; // Prevent form submission if learning hours not selected
        }

        if (date) {
            let attendanceData = collectAttendanceData();
            removeSelectedBackground();
            sendAttendanceData(classId, date, attendanceData, function(success, response) {
                if (success) {
                    console.log('Attendance updated:', response);
                    resetStudentCardColors();
                    applyGrayout(attendanceData);
                    playSound('successSound');
                    showPopupSuccess(`ĐIỂM DANH THÀNH CÔNG <br> Ngày: ${date}`);
                } else {
                    resetStudentCardColors();
                    applyGrayout();
                    console.error('Failed to update attendance:', response);
                    playSound('failSound');
                    showPopupFail(`XẢY RA LỖI KHI ĐIỂM DANH <BR> VUI LÒNG THỬ LẠI`);
                    // Additional logic for a failed request
                }
            });


        } else {
            console.error('Date is required to send attendance data');
        }
        $('#attendanceControlBar').hide();
        $('#moneyControlBar').show();
        isAttendanceButtonClicked = false;
    });


    $('#cancelAttendanceBtn').on('click', function() {
        removeSelectedBackground();
        resetStudentCardColors();
        $('#attendanceControlBar').hide();
        $('#moneyControlBar').show();
        applyGrayout();
        isAttendanceButtonClicked = false;
    });




    $(document).on('click', '.card-student-with-big-image', function() {
        if (isAttendanceButtonClicked) {
            cycleCardColor($(this));
        }
    });

    function cycleCardColor(card) {
        // Get the current background color as an RGB string
        const currentColor = card.css('background-color');

        // Find the current status based on the current color
        const currentStatus = colorToStatus[currentColor] || 'default';

        // Get the list of statuses and find the next status
        const statuses = Object.keys(attendanceColors);
        const currentIndex = statuses.indexOf(currentStatus);
        const nextIndex = (currentIndex + 1) % statuses.length;
        const nextStatus = statuses[nextIndex];

        // Set the new background color and data-status attribute
        card.css('background-color', attendanceColors[nextStatus]);
        card.attr('data-status', nextStatus);
    }


    function resetStudentCardColors() {
        $('.card-student-with-big-image').each(function() {
            $(this).css('background-color', ''); // Resets to default or removes inline style
            $(this).removeAttr('data-status');
        });
    }


    function fetchAttendanceData(classId, date) {
        const url = "{% url 'class_attendance' 0 %}".replace(0, classId) + "?date=" + encodeURIComponent(date);
        return fetch(url)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log(data.data)
                return data.data;  // Return the parsed JSON data

            })
            .catch(error => {
                console.error('Error fetching data:', error);
                // Handle or throw the error as needed
                throw error;
            });
    }




    function collectAttendanceData() {
        const date = $('#attendance-date').val();
        const learningHours = $('#learningHours').val();  // Get the selected learning hours
        let data = [];

        $('.card-student-with-big-image').each(function() {
            let studentId = $(this).data('student-id');
            let rgbColor = $(this).css('background-color');
            let status = colorToStatus[rgbColor] || 'not_checked';

            data.push({ 
                student_id: studentId, 
                status: status, 
                check_date: date, 
                learning_hours: learningHours  // Add learning hours to each record
            });
        });

        return data;
    }

    function sendAttendanceData(classId, date, attendanceData, callback) {
        $.ajax({
            url: "{% url 'class_attendance' 0 %}".replace(0, classId),
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ date: date, attendance: attendanceData }),
            success: function(response) {
                console.log('Attendance data sent successfully:', response);
                if (callback && typeof callback === 'function') {
                    callback(true, response); // Indicates success with the server's response
                }
            },
            error: function(xhr, status, error) {
                console.error('Error sending attendance data:', error);
                if (callback && typeof callback === 'function') {
                    callback(false, error); // Indicates an error occurred, along with the error details
                }
            }
        });
    }



    function updateStudentCardsWithAttendance(attendanceData) {
        // Remove the grayout styles
        $('.card-student-with-big-image').each(function() {
            const studentId = $(this).data('student-id');
            $(this).removeClass('grayed-out');
        });

        $('.card-student-with-big-image').css('background-color', 'grey');
        attendanceData.forEach(record => {

            let studentCard = $(`.card-student-with-big-image[data-student-id='${record.student_id}']`);
            let statusColor = attendanceColors[record.status];
            if (statusColor) {
                studentCard.css('background-color', statusColor);
            }
        });
    }


    function applyGrayout(attendanceData = null) {
        // Function to process attendance data
        const processAttendanceData = data => {
            $('.card-student-with-big-image').each(function() {
                const studentId = $(this).data('student-id');
                const record = data.find(r => r.student_id == studentId);
                const status = record ? record.status : 'not_checked';
                // Gray out if status is 'not_checked' or 'absent'
                if (status === 'not_checked' || status === 'absent') {
                    $(this).addClass('grayed-out');
                } else {
                    $(this).removeClass('grayed-out');
                }
            });
        };

        if (attendanceData) {
            // If attendanceData is provided, use it directly
            processAttendanceData(attendanceData);
        } else {
            // If no data is provided, fetch it
            fetchAttendanceData(classId, date)
                .then(data => processAttendanceData(data))
                .catch(error => {
                    console.error("Fetching attendance data failed:", error);
                });
        }
    }

    function removeSelectedBackground() {
        // Remove the grayout styles
        $('.card-student-with-big-image').each(function() {
            const studentId = $(this).data('student-id');
            $(this).removeClass('selected-background');
        });
    }


});
</script>
 

<script>
// THIS SCRIPT SECTION IS FOR HADNLING DATE SELECTION
function reloadWithDate() {
    const selectedDate = document.getElementById('attendance-date').value;
    window.location.href = window.location.pathname + "?date=" + selectedDate;
}

document.addEventListener("DOMContentLoaded", function() {
    const dateInput = document.getElementById("attendance-date");
    
    // Check if a date is provided in the query parameters
    const urlParams = new URLSearchParams(window.location.search);
    const queryDate = urlParams.get('date');
    
    if (queryDate) {
        dateInput.value = queryDate;  // Set the date from the query parameter
    } else {
        const today = new Date().toISOString().split('T')[0];
        dateInput.value = today;  // Set today's date as default
    }

    // Add the event listener after setting the default date
    dateInput.addEventListener('change', function() {
        window.location.href = window.location.pathname + "?date=" + dateInput.value;
    });
});
</script>