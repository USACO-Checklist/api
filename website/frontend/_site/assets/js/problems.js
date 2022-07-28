window.addEventListener("pageshow", function (event) {
    var historyTraversal = event.persisted ||
        (typeof window.performance != "undefined" &&
            window.performance.navigation.type === 2);
    if (historyTraversal) {
        // Handle page restore.
        window.location.reload();
    }
});

var curD;
var editMode;
var listUUID;
var viewMode; //0, when user is looking at own list, 1 when user is looking at other lists, 2 when unlogged in user is looking at problems
var entryInfo;
var caseInfo;


function init() {
    if (localStorage.getItem('curD') == null) {
        curD = 0;
        localStorage.setItem('curD', curD)
    } else {
        curD = parseInt(localStorage.getItem('curD'));
    }

    if (localStorage.getItem('editMode') == null) {
        editMode = false;
        localStorage.setItem('editMode', editMode);
    } else {
        editMode = localStorage.getItem('editMode') === "true";
    }

    var tempUUID = getUrlParameter('uuid');
    if (!tempUUID) { //not viewing other
        listUUID = localStorage.getItem('uuid');
        if (listUUID === "null") { //user not logged in
            viewMode = 2;
        } else { //user logged in, viewing own
            viewMode = 0;
        }
    } else { //viewing other
        listUUID = tempUUID
        viewMode = 1;
    }

    $("#static-link").val('usaco.raybb.com/problems?uuid=' + listUUID)
    $("#view-share-link").attr("href", '/problems?uuid=' + listUUID)
    $("#list-title").text(localStorage.getItem('username') + '\'s List')

    if (viewMode > 0) setView();
    else if (editMode) setEdit();
    fetchProblemInfo();
    fetchChecklistInfo();
}


function setEdit() {
    var button = $("#edit-button");
    button.removeClass('btn-danger');
    button.addClass('btn-success');
    button.children('i').eq(0).removeClass('fa-eye');
    button.children('i').eq(0).addClass('fa-edit');
    button.children('span').eq(0).text("\xa0Edit");
}

function setView() {
    var button = $("#edit-button");
    button.removeClass('btn-success');
    button.addClass('btn-danger');
    button.children('i').eq(0).removeClass('fa-edit');
    button.children('i').eq(0).addClass('fa-eye');
    button.children('span').eq(0).text("\xa0View");
}


function toggleEditMode() {
    if (viewMode >= 1) return;

    if (editMode) {
        setView();
    } else {
        setEdit();
    }
    editMode = !editMode
    localStorage.setItem('editMode', editMode)
}


function fetchProblemInfo() {
    $.ajax({
        type: "GET",
        url: API_URL + "/problems/get-problem-info",
        xhrFields: {
            withCredentials: true
        },
        headers: {
            Authorization: "Bearer " + localStorage.getItem("access_token")
        },
        contentType: "application/json",
        success: function (response) {
            var problemInfo = JSON.parse(JSON.stringify(response));
            localStorage.setItem('contests', problemInfo['contests']);
            localStorage.setItem('problems', problemInfo['problems']);
            displayTable()
        },
        error: function (response) {
            var errors = $.parseJSON(response.responseText);
            $.each(errors, function (key, value) {
                displayNotification('danger', response.status, value);
            });
        },
    });
}


function fetchChecklistInfo() {
    if (viewMode >= 2) return;

    $.ajax({
        type: "GET",
        url: API_URL + "/problems/get-checklist-info/" + listUUID,
        xhrFields: {
            withCredentials: true
        },
        headers: {
            Authorization: "Bearer " + localStorage.getItem("access_token")
        },
        contentType: "application/json",
        success: function (response) {
            var checklistInfo = JSON.parse(JSON.stringify(response));
            entryInfo = checklistInfo['entries'];
            caseInfo = checklistInfo['cases'];
            displayTable()
        },
        error: function (response) {
            var errors = $.parseJSON(response.responseText);
            $.each(errors, function (key, value) {
                displayNotification('danger', response.status, value);
            });
        },
    });
}


function displayTable() {
    displayProblemTable();
    displayProblemTableInfo();
}

function displayProblemTable() {
    const contests = JSON.parse(localStorage.getItem('contests'));
    const problems = JSON.parse(localStorage.getItem('problems'));

    var p = $("#problem-list");
    p.empty();
    for (var i = contests.length - 1; i >= 0; i--) {
        p.append(
            '<tr id="contest' + contests[i]["id"] + '"><th class="contest-header bg-light">' +
            contests[i]["year"] + ' ' + contests[i]["month"] + '</th></tr>'
        );
    }

    for (var i = 0; i < problems.length; i++) {
        var p = $("#contest" + problems[i]["contest_id"])
        p.append(
            '<td id="problem' + problems[i]["id"] + '" class="problem-entry table-default" onclick="updateStatus(this)">' +
            '<div class="problem-container"><div class="problem-name"><a href="http://www.usaco.org/index.php?page=viewproblem2&cpid=' +
            problems[i]["id"] + '" onclick="event.stopPropagation()" target="_blank">' +
            problems[i]["name"] + ' </a></div></div></td>'
        )
    }
    filterTable(curD);
}


function displayProblemTableInfo() {
    if (viewMode >= 2) return;

    if (entryInfo !== undefined) {
        const entries = JSON.parse(entryInfo);
        for (var i = 0; i < entries.length; i++) {
            var cell = $("#problem" + entries[i]["problem_id"]);
            cell.removeClass("table-default");
            cell.addClass(int2class(entries[i]["status"]));
            cell.children('div').eq(0).append('<div id="cases' + entries[i]["id"] + '" class="case-info"></div>')
        }
    }
    if (caseInfo !== undefined) {
        const cases = JSON.parse(caseInfo);
        for (var i = 0; i < cases.length; i++) {
            var div = $("#cases" + cases[i]["entry_id"]);
            if (cases[i]["is_correct"] === "True")
                div.append(
                    '<div class="case case-correct" onclick="event.stopPropagation()"><div><a target="_blank">' +
                    cases[i]["symbol"] + '</a></div></div>'
                );
            else
                div.append(
                    '<div class="case case-incorrect" onclick="event.stopPropagation()"><div><a target="_blank">' +
                    cases[i]["symbol"] + '</a></div></div>'
                );
        }
    }
    filterTable(curD);
}


function filterTable(difficulty) {
    $("#b" + curD).removeClass("active");
    $("#b" + difficulty).addClass("active");
    curD = difficulty;

    localStorage.setItem('curD', curD);

    const contests = JSON.parse(localStorage.getItem('contests'));
    for (var i = 0; i < contests.length; i++) {
        var p = $("#contest" + contests[i]["id"]);
        var searchInput = $("#search-input").val().toUpperCase()
        var problemsInContest = p.children('td')
        var foundProblem = false;
        for (var j = 0; j < problemsInContest.length; j++) {
            var name = $(problemsInContest[j]).children('div').eq(0).children('div').eq(0).children('a').eq(0).text();
            if (name.toUpperCase().indexOf(searchInput) > -1 && div2int(contests[i]["division"]) === curD) {
                foundProblem = true;
            }
        }
        if (foundProblem) p.show();
        else p.hide();
    }
}


function updateStatus(problemCell) {
    if (!editMode || viewMode >= 1) return;
    var cur = $(problemCell);
    var currIntStatus = status2int(problemCell.classList[problemCell.classList.length - 1]);
    var newIntStatus = (currIntStatus + 1) % 4

    var entryData = {
        "status": parseInt(newIntStatus),
        "problem_id": parseInt(problemCell.id.substring(7))
    };

    $.ajax({
        type: "POST",
        url: API_URL + '/problems/update',
        xhrFields: {
            withCredentials: true
        },
        headers: {
            Authorization: "Bearer " + localStorage.getItem("access_token")
        },
        data: JSON.stringify(entryData),
        contentType: "application/json",
        success: function () {
            cur.removeClass(problemCell.classList[problemCell.classList.length - 1]);
            cur.addClass(int2class(newIntStatus))
        },
        error: function (response) {
            var errors = $.parseJSON(response.responseText);
            $.each(errors, function (key, value) {
                displayNotification('danger', response.status, value);
            });
        },
    });
}


function div2int(div) {
    if (div === "Bronze") return 3;
    if (div === "Silver") return 2;
    if (div === "Gold") return 1;
    if (div === "Platinum") return 0;
    else return -1;
}

function status2int(status) {
    if (status === "table-default") return 0;
    if (status === "table-warning") return 1;
    if (status === "table-primary") return 2;
    if (status === "table-success") return 3;
    else return -1;
}

function int2class(num) {
    if (num == 0) return "table-default";
    if (num == 1) return "table-warning";
    if (num == 2) return "table-primary";
    if (num == 3) return "table-success";
    else return -1;
}


function copylink() {
    var text = document.getElementById("static-link");
    text.select();
    document.execCommand("copy");
}