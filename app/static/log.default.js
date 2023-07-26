// *************************************
// HELPER PAGE DEFAULT CONTENT GENERATOR
// -------------------------------------
// Version: 3.00
// Date: 30-05-2023

// -----------------
// Log page handlers
// -----------------

var $ProfileClients = {};

// ----------------------
// Page Content Generator
// ----------------------

function $updatePage(action, response) {
    var container = $("#report_container");

    if (IsLog)
        console.log('$updatePage:', action, response);

    var update_timer = window.setTimeout(function() {
        window.clearTimeout(update_timer);
        update_timer = null;
        container.scrollTop(0);
        $ShowPage(0);
    }, 100);
}

// ---------------------------------
// TabLine|Subline Content Generator
// ---------------------------------

function $updateViewData(action, response, props, total, status, path) {
}

function $updateLineData(action, response, props, total, status, path) {
}

function $updateSublineData(action, response, props, total, status, path) {
}
