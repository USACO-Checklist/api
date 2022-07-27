var API_URL = "http://127.0.0.1:8000";

$(document).ready(function () {
    $("#logout-link").click(function (event) {
        event.preventDefault();
        logout();
    });

    $(".nav-item").filter(function () {
        return window.location.href === this.href
    }).addClass("active");
});


function init_nav() {
    $.ajax({
        type: "GET",
        url: API_URL + "/auth/current-user",
        xhrFields: {
            withCredentials: true
        },
        success: function (response) {
            if (response['status'] == 1) {
                $(".logged-in-content").show();
                $(".logged-out-content").hide();
                localStorage.setItem('username', response['username']);
                localStorage.setItem('uuid', response['uuid']);
            } else {
                $(".logged-in-content").hide()
                $(".logged-out-content").show()
                localStorage.setItem('username', 'Guest');
                localStorage.setItem('uuid', null);
            }
            localStorage.setItem('isLoggedIn', response['status']);

            var dropdownUser = $("#dropdown-username");
            dropdownUser.text('\xa0' + response['username']);
            dropdownUser.prepend('<i class="fa fa-user"></i>');
        },
        error: function (response) {
            var errors = $.parseJSON(response.responseText);
            $.each(errors, function (key, value) {
                displayNotification('danger', value);
            });
        },
    });
}


function logout() {
    // localStorage.clear()
    $.ajax({
        type: "POST",
        url: API_URL + "/auth/logout-user",
        xhrFields: {
            withCredentials: true
        },
        success: function () {
            window.location.assign('/');
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

function getUrlParameter(sParam) {
    var sPageURL = window.location.search.substring(1),
        sURLVariables = sPageURL.split('&'),
        sParameterName,
        i;

    for (i = 0; i < sURLVariables.length; i++) {
        sParameterName = sURLVariables[i].split('=');

        if (sParameterName[0] === sParam) {
            return sParameterName[1] === undefined ? true : decodeURIComponent(sParameterName[1]);
        }
    }
    return false;
};