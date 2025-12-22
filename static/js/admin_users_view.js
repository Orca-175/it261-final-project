$('.admin-approval-form').on('submit', function(event) {
    event.preventDefault();

    $.post(
        $(this).attr('action'),
        $(this).serialize()
    ).done(
        (response) => {
            alert(response)
            $.get(
                '/get_admins'
            ).done(
                (response) => {
                    $('.registration-rows').remove();
                    response.forEach(user => {
                        $('#admin-registrations-table-body').append(`
                            <tr class="registration-rows">
                                <td>${user['id']}</td>
                                <td>${user['username']}</td>
                                <td>${user['approved']}</td>
                                <td class="d-flex justify-content-center">
                                    <form class="admin-approval-form" action="/approve_user" method="POST">
                                        <input name="admin-id" type="hidden" value="${user['id']}">
                                        <input type="submit" class="btn btn-primary" value="Approve">
                                    </form>
                                </td>
                            </tr>
                        `);
                    });
                }
            ).fail(
                (jqXHR) => {
                    alert(jqXHR.responseText);
                }
            );
        }
    ).fail(
        (jqXHR) => {
            alert(jqXHR.responseText);
        }
    );
});

$('#admin-accounts-btn').on('click', function() {
    $('#customer-accounts-btn').removeClass('active-text-color').addClass('inactive-text-color text-btn-hover');
    $(this).removeClass('inactive-text-color text-btn-hover').addClass('active-text-color');

    $('#customer-accounts-table').addClass('hidden');
    $('#admin-accounts-table').removeClass('hidden');
});

$('#customer-accounts-btn').on('click', function() {
    $('#admin-accounts-btn').removeClass('active-text-color').addClass('inactive-text-color text-btn-hover');
    $(this).removeClass('inactive-text-color text-btn-hover').addClass('active-text-color');

    $('#admin-accounts-table').addClass('hidden');
    $('#customer-accounts-table').removeClass('hidden');
});
