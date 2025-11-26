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
                        $('#registrations-table-body').append(`
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
