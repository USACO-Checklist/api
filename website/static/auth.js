$(document).ready(function () {
    $("#form-change-password").submit(function (event) {
        event.preventDefault();
        var username = $("#username").val();
        var old_password = $("#password0").val();
        var new_password = $("#password1").val();
        var new_password_confirm = $("#password2").val();
        change_password(username, old_password, new_password, new_password_confirm);
    });

    $("#form-login").submit(function (event) {
        event.preventDefault();
        var username = $("#username").val();
        var password = $("#password").val();
        login(username, password);
    });

    $("#form-signup").submit(function (event) {
        event.preventDefault();
        var username = $("#username").val();
        var password = $("#password1").val();
        var password_confirm = $("#password2").val();
        signup(username, password, password_confirm);
    });
});


function change_password(username, old_password, new_password, new_password_confirm) {
    if (username.length === 0) {
        displayNotification('danger', 'Username cannot be empty')
        return;
    }
    if (old_password.length === 0) {
        displayNotification('danger', 'Password cannot be empty')
        return;
    }
    if (new_password.length === 0) {
        displayNotification('danger', 'New password cannot be empty')
        return;
    }
    if (new_password !== new_password_confirm) {
        displayNotification('danger', 'New passwords do not match')
        return;
    }

    var formData = {
        username: username,
        old_password: old_password,
        new_password: new_password
    };

    $.ajax({
        type: "POST",
        url: "/auth/change-password",
        data: formData,
        contentType: "application/x-www-form-urlencoded",
        success: function () {
            window.location.assign("/problems");
        },
        error: function (response) {
            var errors = $.parseJSON(response.responseText);
            $.each(errors, function (key, value) {
                displayNotification('danger', response.status, value);
            });
        },
    });
}

function login(username, password) {
    if (username.length === 0) {
        displayNotification('danger', 'Username cannot be empty')
        return;
    }
    if (password.length === 0) {
        displayNotification('danger', 'Password cannot be empty')
        return;
    }

    var formData = {
        username: username,
        password: password
    };

    $.ajax({
        type: "POST",
        url: "/auth/login-user",
        data: formData,
        contentType: "application/x-www-form-urlencoded",
        success: function () {
            window.location.assign("/problems");
        },
        error: function (response) {
            var errors = $.parseJSON(response.responseText);
            $.each(errors, function (key, value) {
                displayNotification('danger', value);
            });
        },
    });
}

function signup(username, password, password_confirm) {
    if (username.length === 0) {
        displayNotification('danger', 'Username cannot be empty')
        return;
    }
    if (password.length === 0) {
        displayNotification('danger', 'Password cannot be empty')
        return;
    }
    if (password !== password_confirm) {
        displayNotification('danger', 'Passwords do not match')
        return;
    }

    var formData = {
        username: username,
        password: password
    };

    $.ajax({
        type: "POST",
        url: "/auth/signup-user",
        data: formData,
        contentType: "application/x-www-form-urlencoded",
        success: function () {
            login(username, password);
        },
        error: function (response) {
            var errors = $.parseJSON(response.responseText);
            $.each(errors, function (key, value) {
                displayNotification('danger', value);
            });
        },
    });
}
