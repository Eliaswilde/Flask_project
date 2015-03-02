$(document).ready(function(){
	$(".myStat").circliful();

    $("#login-form, #signup-form").submit(function(e) {
        e.preventDefault();
        var $form = $(e.target);
        var url = $form.attr('action');
        $.ajax({
            url: url,
            type: 'post',
            dataType: 'json',
            data: $form.serialize(),
            success: function(data) {
                // Remove all error messages
                var $general_error = $('.form-error', $form);
                $general_error.html('').hide();
                $('ul.errors').html('').hide();
                
                if (data.status === 'success') {
                    window.location.reload();
                } else {
                    // Showing general form error (e.g. wrong login/password)
                    if (data.general_error) {
                        $('.form-error', $form).html(data.general_error).show();
                    }
                    
                    // Populating fields errors
                    for (key in data.fields_errors) {
                        var $errors_ul = $('input[name=' + key  + ']', $form).siblings('ul');
                        var errors = data.fields_errors[key];
                        for (var i=0; i<errors.length; i++) {
                            $errors_ul.show().append('<li>' + errors[i]  + '</li>');
                        }
                    }
                }
            }
        });
        return false;
    });
});
