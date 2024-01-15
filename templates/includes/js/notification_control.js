{% load static %}

<script>
    // Sounds preloaded
    var successSound = new Audio("{% static 'sound/success.mp3' %}");
    var failSound = new Audio("{% static 'sound/fail.mp3' %}");

    // Preload all success and fail images
    var successImages = [], failImages = [];
    for (var i = 1; i <= 11; i++) {
        var img = new Image();
        img.src = '/static/img/memes/meme_success_' + i + ".png";
        successImages.push(img);
    }
    for (var i = 1; i <= 20; i++) {
        var img = new Image();
        img.src = '/static/img/memes/meme_fail_' + i + ".png";
        failImages.push(img);
    }

    // Function to play the sound
    function playSound(isSuccess) {
        if (isSuccess) {
            successSound.play();
        } else {
            failSound.play();
        }
    }

    // Function to show notification modal
    function showNotificationModal(message, imageIndex, isSuccess) {
        const $modal = $('#notificationModal');
        const $modalContent = $modal.find('.notification-modal-content');
        const $modalBody = $('#notification-modal-body');

        var image = isSuccess ? successImages[imageIndex] : failImages[imageIndex];
        $modalBody.html(`<p>${message}</p>`).append(image);

        if (isSuccess) {
            $modalContent.addClass('modal-success').removeClass('modal-fail');
        } else {
            $modalContent.addClass('modal-fail').removeClass('modal-success');
        }

        playSound(isSuccess);

        $modal.css('display', 'block');

        setTimeout(function() {
            $modal.css('display', 'none');
        }, 5000);
    }

    function getRandomImageIndex(count) {
        return Math.floor(Math.random() * count);
    }

    function showPopupSuccess(message) {
        const imageIndex = getRandomImageIndex(successImages.length);
        showNotificationModal(message, imageIndex, true);
    }

    function showPopupFail(message) {
        const imageIndex = getRandomImageIndex(failImages.length);
        showNotificationModal(message, imageIndex, false);
    }

</script>
