<script>
$(document).ready(function() {
    // Handle individual card click
    $('.card-student-with-big-image').click(function() {
        $(this).toggleClass('selected-background');
    });

    // Handle "Select All" button click
    $('#selectAllBtn').click(function() {
        $('.card-student-with-big-image:not(.grayed-out)').each(function() {
            $(this).addClass('selected-background');
        });
    });

    // Handle "Deselect All" button click
    $('#deselectAllBtn').click(function() {
        $('.card-student-with-big-image').removeClass('selected-background');
    });



    // Add or subtract money
    $('#addMoneyBtn').click(function() {
        let globalMoneyChange = parseInt($('#globalMoneyChange').val());
        sendMoneyData(globalMoneyChange, function(success) {
            if (success) {
                updateMoneyAmount(globalMoneyChange);
                addEffect(globalMoneyChange);
            }
        });
    });

    $('#subtractMoneyBtn').click(function() {
        let globalMoneyChange = -parseInt($('#globalMoneyChange').val());
        sendMoneyData(globalMoneyChange, function(success) {
            if (success) {
                updateMoneyAmount(globalMoneyChange);
                addEffect(globalMoneyChange);
            }
        });
    });


    function sendMoneyData(globalMoneyChange, callback) {
        let selectedStudents = [];

        $('.card-student-with-big-image.selected-background').each(function() {
            let studentId = $(this).data('student-id');
            selectedStudents.push({ id: studentId, money: globalMoneyChange });
        });

        // Send the data to the server
        $.ajax({
            url: "{% url 'add_money_to_students' %}",
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(selectedStudents),
            success: function(response) {
                console.log('Success:', response);
                callback(true);
            },
            error: function(error) {
                console.log('Error:', error);
                callback(false);
            }
        });
    }


    // Update money amount for each selected student
    function updateMoneyAmount(amount) {
        $('.card-student-with-big-image.selected-background').each(function() {
            let currentMoney = parseInt($(this).find('.money-display-text').text());
            $(this).find('.money-display-text').text(currentMoney + amount);
        });
    }

    // Add effects
    function addEffect(globalMoneyChange) {
        if(globalMoneyChange > 0) {
            showPopupSuccess(`CHÚC MỪNG! <br> ${globalMoneyChange} dollars đã được thêm vào ngân hàng.`);
        } else {
            showPopupFail(`BÁO QUÁ BÁO LUÔN Á! <br> ${Math.abs(globalMoneyChange)} dollars đã bị trừ khỏi ngân hàng.`);
        }

        $('.card-student-with-big-image.selected-background').each(function() {
            $(this).addClass('shake');
            setTimeout(() => {
                $(this).removeClass('shake');
            }, 9000); // 6s
        });
    }


});
</script>
