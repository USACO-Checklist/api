$(document).ready(function () {
    $("#form-sync-usaco").submit(function (event) {
        event.preventDefault();
        var username = $("#username").val();
        var password = $("#password").val();
        syncUsaco(username, password);
    });
});


function syncUsaco(username, password) {
    if (username.length === 0) {
        displayNotification('danger', 'Username cannot be empty')
        return;
    }
    if (password.length === 0) {
        displayNotification('danger', 'Password cannot be empty')
        return;
    }

    var formData = {
        usaco_uname: username,
        usaco_password: password
    };

    $.ajax({
        type: "POST",
        url: "/problems/fetch-all-cases/",
        data: formData,
        contentType: "application/x-www-form-urlencoded",
        success: function () {
            displayNotification('primary', 'Fetching all problem cases, check back in a few minutes');
        },
        error: function (response) {
            var errors = $.parseJSON(response.responseText);
            $.each(errors, function (key, value) {
                displayNotification('danger', value);
            });
        },
    });
}