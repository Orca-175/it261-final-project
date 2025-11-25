$('#registration-form').on('submit', function(event) {
    event.preventDefault();
    $.post(
        '/admin_registration',
        $(this).serialize()
    ).done(
        (response) => {
            window.location.href = response['redirect'];
        }
    ).fail(
        (jqXHR) => {
            alert(jqXHR.responseText);
        } 
    );
});

$('#login-form').on('submit', function(event) {
    event.preventDefault();
    $.post(
        '/admin_login',
        $(this).serialize()
    ).done(
        (response) => {
            window.location.href = response['redirect'];
        }
    ).fail(
        (jqXHR) => {
            alert(jqXHR.responseText);
        } 
    );
});