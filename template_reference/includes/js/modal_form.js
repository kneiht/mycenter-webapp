    
<script>
    $(document).on('click', '.create-modal-form', function() {
        // Get the values of the data attributes
        var idRecord = $(this).data("id-record");
        var modelName = $(this).data("model-name");

        // studentID is used for preselect student in attedance form and pau_tuition
        var studentID = $(this).data("student-id");
        $.ajax({
            url: '{% url 'form_generator' %}', // Make sure this URL is correctly configured in your Django urls.py
            type: 'get',
            dataType: 'json',
            data: {
                'model_name': modelName,
                'id_record': idRecord,
                'student_id': studentID,
            },
            success: function (data) {
                $("#modalPlaceHolder").html(data.html_modal);
                var isNew = document.getElementById("isNew").getAttribute("data");

                $("#modalForm").modal("show");
            },
            error: function (response) {
                // Handle error
                console.error("Error: " + response.responseText);
            }
        });
    });

    // Handle the form submission event to create a new transaction or edit an existing one
    $(document).on('click', '#saveFormInsideModal', function(e) {
        e.preventDefault();
          var form = $('#formInsideModal')[0]; // Get the form DOM element


          // HTML5 form validation
          if (!form.checkValidity()) {
            form.reportValidity(); // If the form is invalid, display the error messages
            return; // and stop here
          }

        var files = $('#id_image')[0].files;

        var fileIsValid = true; // Flag to track file validity
        $.each(files, function(index, file) {
            // Check if the file is not PNG or JPG, clear input
            if (!(file.type === "image/png" || file.type === "image/jpeg" || file.type === "image/webp")) {
                alert("Not supported image format. Please select png, jpg or webp. \n\nĐịnh dạng hình ảnh này không được hỗ trợ. Vui lòng chọn định dạng png, jpg hoặc webp.");
                fileIsValid = false; // Set the flag to false
                return false; // Exit the loop
            } 
        });

        if (!fileIsValid) {
            return; // Exit the function if file is not valid
        }


          var idRecord = $('#id_id').val(); // Assuming you have a hidden field for the ID
          //var formData = $('#itemForm').serialize(); // Serialize the form data


          // Get the URL from the data-api-url attribute
          var urlAPI = document.getElementById("urlAPI").getAttribute("data");


          let formData = new FormData(form);

         // Remove image data if empty
        for (let [key, value] of formData.entries()) {
            if (key === "image" &&  value.size===0) {
                formData.delete('image');
            }
        }


        // Add logic to include selected students and classes data
        $('input[name="selected_students"]:checked').each(function() {
            formData.append('selected_students[]', $(this).val());
        });

        $('input[name="paid_class_students"]:checked').each(function() {
            formData.append('paid_class_students[]', $(this).val());
        });

        $('input[name="selected_classes"]:checked').each(function() {
            formData.append('selected_classes[]', $(this).val());
        });

        $('input[name="paid_classes"]:checked').each(function() {
            formData.append('paid_classes[]', $(this).val());
        });



        // Compress and process multiple images
        if (files.length > 0) {
            var compressedImages = []; // Array to store compressed images

            // Function to process each image
            var processImage = function(file, index, callback) {
                var reader = new FileReader();
                reader.readAsDataURL(file);
                reader.onloadend = function (e) {
                    var image = new Image();
                    image.src = e.target.result;
                    image.onload = function () {
                        var canvas = document.createElement('canvas');
                        var ctx = canvas.getContext('2d');

                        // Calculate the new dimensions
                        var maxWidth = 600;
                        var maxHeight = maxWidth * (image.height / image.width);
                        canvas.width = maxWidth;
                        canvas.height = maxHeight;

                        ctx.drawImage(image, 0, 0, maxWidth, maxHeight);

                        // Convert canvas to blob and then call the callback
                        canvas.toBlob(function (blob) {
                            console.log("Size of image " + index + ": " + blob.size + " bytes");
                            compressedImages.push(blob); // Add compressed image to array
                            callback(index);
                        }, 'image/webp', 0.4); // Adjust quality as needed
                    };
                };
            };
            // Process each file
            Array.from(files).forEach(function(file, index) {
                processImage(file, index, function(index) {
                    // Check if it's the last image
                    if (index === files.length - 1) {
                        // Check if 'images' key exists in formData
                        if (formData.has('images')) {
                            // Remove original images from formData
                            formData.delete('images');

                            // Append all compressed images under the same key
                            compressedImages.forEach(function(blob, i) {
                                formData.append('images', blob, 'image' + i + '.webp');
                            });
                        }
                        // Check if 'image' key exists in formData
                        else if (formData.has('image')) {
                            formData.delete('image');
                            compressedImages.forEach(function(blob, i) {
                                formData.set('image', blob, 'image' + i + '.webp');
                            });
                        }

                        // Continue with the form submission after last image processing
                        submitForm(formData, idRecord, urlAPI);
                    }
                });
            });

        } else {
            // No images to compress, continue with form submission
            submitForm(formData, idRecord, urlAPI);
        }
    });



    function submitForm(formData, idRecord, urlAPI) {
      // Determine whether this is a new record or an existing one
      // If transactionId exists and is not empty, it's an existing record, otherwise, it's a new record
      var isNewRecord = !idRecord;

      var method = isNewRecord ? 'POST' : 'PUT'; // If it's new, use 'POST', otherwise, use 'PUT'
      var url = isNewRecord ? urlAPI : (urlAPI.endsWith('/') ? urlAPI : urlAPI + '/') + idRecord + '/';


        // Log formData to console
        //for (let [key, value] of formData.entries()) {
        //    console.log(`${key}: ${value}`);
        //}
      $.ajax({
        url: url,
        type: method,
        data: formData,
          processData: false,  // Important!
          contentType: false,  // Important!
        success: function(response) {

          // On success, you might want to hide the modal and refresh the transactions list
          $('#modalForm').modal('hide');
          // Refresh the table or add/update the row depending on the operation
          if (isNewRecord) {
            var formModelName = document.getElementById("modelName").getAttribute("data");
            if (formModelName === "pay_tuition") {
                var studentID = document.getElementById('id_student').value;
                loadOneRecordDisplay(studentID, "student");
            } else {
                location.reload();
            }
          } else {
            var modelName = "{{ model_name }}";
            console.log(modelName)
            if (modelName === "class") {
                location.reload();
            } else {
                loadOneRecordDisplay(idRecord, modelName);
            }
          }


        },
        error: function(xhr, status, error) {
          // Handle error
            console.log('Error:', error);
            console.log('Status:', status);
            console.log('Response:', xhr.responseText);
          // Optionally, display an error message on your modal
        }
      });
    }


  function loadOneRecordDisplay(idRecord, modelName) {
      $.ajax({
          url: "{% url 'fetch_one_record' %}", // URL to the view that returns records HTML
          type: "GET",
          data: {
              'model_name': modelName,
              'id_record': idRecord
          },
          success: function(response) {
              var tablerow = $("#tablerow" + idRecord);
              var card = $("#card" + idRecord);
              card.replaceWith(response.html_card_content);
              tablerow.replaceWith(response.html_table_content);
          },

          error: function(xhr, status, error) {
              // Handle error
              console.error("Error loading page content: ", status, error);
          }
      });
  }




    // Event listener for the delete button
    $(document).on('click', '#deleteRecord', function() {
        var idRecord = $('#id_id').val();

        // Get the URL from the data-api-url attribute
        var urlAPI = document.getElementById("urlAPI").getAttribute("data");
        var url = urlAPI + idRecord + '/'; 
        var url = (urlAPI.endsWith('/') ? urlAPI : urlAPI + '/') + idRecord + '/';

        var message = "Are you sure you want to delete this record?";
        showConfirmationModal(message, function() {
            $.ajax({
                url: url,
                type: 'DELETE',
                success: function(result) {
                    //showAlertModal("Record deleted successfully");
                    location.reload()
                    // Additional success handling
                },
                error: function(request, status, error) {
                    showAlertModal("Error: " + error);
                }
            });
        });
    });

    $(document).ready(function() {
        $(document).on('change', '.student-checkbox', function() {
            var studentRow = $(this).closest('tr');
            var paidClassCheckbox = studentRow.find('.paid-class-checkbox');

            if($(this).is(':checked')) {
                paidClassCheckbox.prop('disabled', false);
            } else {
                paidClassCheckbox.prop('disabled', true).prop('checked', false);
            }
        });

        $(document).on('change', '.class-checkbox', function() {
            var studentRow = $(this).closest('tr');
            var paidClassCheckbox = studentRow.find('.paid-class-checkbox');

            if($(this).is(':checked')) {
                paidClassCheckbox.prop('disabled', false);
            } else {
                paidClassCheckbox.prop('disabled', true).prop('checked', false);
            }
        });


    });


    $(document).ready(function() {
        function calculateFinalFee() {
            var selectedTuitionPlan = $('#id_tuition_plan option:selected');
            var selectedDiscount = $('#id_discount option:selected');

            var price = parseFloat(selectedTuitionPlan.data('price')) || 0;
            var discountValue = parseFloat(selectedDiscount.data('discount-value')) || 0;

            var finalFee = price - (price * discountValue);
            // Format the finalFee in Vietnamese currency format
            const formattedFinalFee = new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(finalFee);

            $('#id_final_fee').val(formattedFinalFee);
        }

        // Event listener for changes in tuition plan and discount dropdowns
        $(document).on('change', '#id_tuition_plan, #id_discount', function() {
            calculateFinalFee();
        });

        // Calculate initial fee on page load
        calculateFinalFee();
    });


    // Display preview and check image input
    $(document).ready(function() {
        $(document).on('change', '#id_image', function() {
            console.log('change')
            var files = $(this)[0].files;
            var previewContainer = $('#image_preview_container');
            previewContainer.empty(); // Clear the container

            $.each(files, function(index, file) {

                // Only process image files
                if (!file.type.match('image.*')) {
                    return;
                }

                var reader = new FileReader();
                reader.onload = function(e) {
                    var img = $('<img>').attr('src', e.target.result);
                    previewContainer.append(img); // Append the wrapper to the container
                };
                reader.readAsDataURL(file);
            });
        });
    });
</script>














