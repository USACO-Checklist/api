$(document).ready(function () {
    $("#logout-link").click(function (event) {
        event.preventDefault();
        logout();
    });

    $(".nav-item").filter(function () {
        return window.location.href === this.href
    }).addClass("active");
});


function logout() {
    // localStorage.clear()
    $.ajax({
        type: "POST",
        url: "/auth/logout-user",
        success: function () {
            window.location.assign("/");
        },
        error: function (response) {
            var errors = $.parseJSON(response.responseText);
            $.each(errors, function (key, value) {
                displayNotification('danger', value);
            });
        },
    });
}

function displayNotification(type, content) {
    $("#notification-box").append(
        '<div class= "alert alert-' + type + ' fade show">' + content +
        '<button type="button" class="close" data-dismiss="alert" aria-label="Close">' +
        '<span aria-hidden="true">&times;</span>' +
        '</button></div>'
    );
}