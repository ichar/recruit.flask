// ******************************
// FRONT SIDE COMMON DECLARATIONS
// ------------------------------
// Version: 3.00
// Date: 20-01-2023

var keywords = new Object();
var script_version = 1;
var default_timeout = 100;
var default_loader_timeout = 300;

var IsDebug = 0;                   // Turn on/off Debug-mode  
var IsDeepDebug = 0;               // Turn on/off DeepDebug-mode  
var IsTrace = 0;                   // Turn on/off Trace-mode
var IsLog = 1;                     // Turn on/off console log

var IsTriggeredSubmit = 0;         // Show/Hide startup page

// ----------------
//  Browsers types
// ----------------

var IsMSIE = 0;
var is_webkit = 0;

// ---------------------------------------------------------
//  Line Page Submit Type:
//  0 - page submit, 1 - startup action, 2 - selected action
// ---------------------------------------------------------
var default_submit_mode = 0;        // Page Refresh type (mode:0|1|2|3)
var default_action = null;          // Action code for default refreshing (SUBLINE), submit mode > 0
var default_page_action = null;     // Action code for refreshing Page Main Tab area
var default_print_action = null;    // Action code for printing Tab area
var default_handler = null;         // Handler for Tab Area Action, optional
var default_params = null;          // Params for Tab Area Action, optional
var default_input_name = '';        // Name of LINE input tag
var default_option_delimeter = '/'; // Symbol to split options controls input

var should_be_updated = false;      // Optional flag to update LINE

var current_context = '';           // Current context name
var placeholder = '';               // Search placeholder text
var loader_page = '';               // Loader Page name 
var selected_menu_action = null;    // Selected DataMenu Action

var active_dialog = null;           // Active dialog for error keypress 

// ==========================================================================================================

// ----------------
// Global Constants
// ----------------

var TID = new Array();

var isWebServiceExecute = false;
var isSubmitted = false;
var isKeyboardDisabled = false;
var isConfirmation = false;
var isDropdownActive = false;
var isCallback = false;

var confirm_action = '';
var confirm_response = null;

var DEFAULT_HTML_SPLITTER = '_';

var CSS_INVISIBLE = 'invisible';

// ------------
// Module items
// ------------

var model = 0;
var root = '';
var back = '';
var baseURI = '';
var loaderURI = '';

var is_show_error = false;
var is_loaded_success = false;
var page_state = -1;
var page_scroll_top = 0;

var is_loaded_success = false;
var is_link = false;
var is_scroll_top = false;
var is_on_refresh = false;

var no_window_scroll = false;

var orientation = '';               // Page print list format

// ----------------
// Global Functions
// ----------------

function interrupt(start, mode, timeout, callback, index, type) {
    //
    //  Модуль прерываний. Алгоритмы загрузки контента AJAX
    //  ---------------------------------------------------
    //  start [true, false] - фаза исполнения: true-старт, false-финиш
    //  mode - индекс алгоритма
    //  timeout - длительность таймаута
    //  callback - функция обратного вызова[9] (строка) или строковый параметр[-1]
    //  index - индекс таймаута
    //  type - тип функции: 0/1, setTimeout/setInterval
    //
    if (start) {
        var i = !is_null(index) ? index : TID.length;
        //var s = "interrupt(false, "+mode+", 0, "+(callback ? "'"+callback+"'" : 'null')+", "+i+")";
        var delay = timeout ? timeout : default_timeout;
        var func = function() { interrupt(false, mode, 0, callback, i, type); };
        if (i == TID.length) TID.push(null);
        //TID[i] = (type === 1) ? window.setInterval(func, delay) : window.setTimeout(func, delay);
        if (type == 1)
            TID[i] = window.setInterval(func, delay);
        else
            TID[i] = window.setTimeout(func, delay);

        if (IsLog)
            console.log('start:'+mode+', index:'+i+', len:'+TID.length);

    } else if (mode) {
        if (IsLog)
            console.log('interrupt:'+mode+', TID:'+TID.join('-'));

        if (mode == -1) {
            // Callback for Back|Forward
            window.location.replace(callback || '');
        } else if (mode == 1) {
            // OnReady Upload
            interrupt(false, 0, 0, null, index);
            $ShowOnStartup();
        }

    } else if (TID.length > index && TID[index] != null) {
        if (type == 1)
            window.clearInterval(TID[index]);
        else 
            window.clearTimeout(TID[index]);

        if (index == TID.length-1)
            TID.splice(index, 1);
        else
            TID[index] = null;

        if (IsLog)
            console.log('stop index:'+index+', len:'+TID.length);
    }
}

function $_mobile() {
    return false;
}

function $_window_orientation() {
    return typeof(window.orientation) !== 'undefined' ? (
        window.orientation == 0 || window.orientation == 180 ? 'portrait' : 'landscape') : (
        screen.msOrientation || screen.mozOrientation || (screen.orientation || {}).type);
}

function $_window_portrait() {
    return $_window_orientation().startswith('portrait');
}

function $_window_landscape() {
    return $_window_orientation().startswith('landscape');
}

function $_get_css_size(value, x) {
    return value.toString()+(x ? x : "px");
}

function $_height(m) {
    var f = $_mobile();
    if (m == 'screen-max')
        return Math.max(window.screen.availHeight, verge.viewportH());
    if (m == 'screen-min' || m == 'mobile')
        return Math.min(window.screen.availHeight, verge.viewportH());
    if (m == 'max')
        return Math.max(
            verge.viewportH(),
            window.screen.height, 
            window.screen.availHeight, 
            document.body.clientHeight, 
            document.documentElement.clientHeight
        );
    if (m == 'available' && f) {
        var mode = $_window_portrait() ? 'screen-max' : 'client';
        //var mode = 'screen-max';
        return $_height(mode);
    }
    if (m == 'client' || m == 'available')
        return document.documentElement.clientHeight || $_height('screen-min');
    else
        return Math.min(
            verge.viewportH(),
            window.screen.height,
            window.screen.availHeight,
            document.body.clientHeight,
            document.documentElement.clientHeight
        );
}

function $_width(m) {
    var f = $_mobile();
    if (m == 'screen-max')
        return Math.max(window.screen.availWidth, verge.viewportW());
    if (m == 'screen-min' || m == 'mobile')
        return Math.min(window.screen.availWidth, verge.viewportW());
    if (m == 'max')
        return Math.max(
            verge.viewportW(),
            window.screen.width,
            window.screen.availWidth,
            document.body.clientWidth,
            document.documentElement.clientWidth
        );
    if (m == 'available' && f) {
        var mode = 'screen-max';
        return $_width(mode);
    }
    if (m == 'client' || m == 'available')
        return document.documentElement.clientWidth;
    else
        return Math.min(
            verge.viewportW(),
            window.screen.width, 
            window.screen.availWidth, 
            document.body.clientWidth, 
            document.documentElement.clientWidth
        );
}

function $_screen_with_scroll(mode, offset) {
    if (['height', 'H'].indexOf(mode) > -1)
        return document.body.clientHeight + (offset || 0) > $_height('available');
    return document.body.clientWidth + (offset || 0) > $_width('available');
}

function $_screen_center(mode) {
    var m = mode || 'available';
    return { 'W':$_width(m), 'H':$_height(m) };
}

function $_show_window_in_center(container, mode, without_scroll) {
    var page = $("#html-container");
    var sh = 20;
    var sw = 0;
    var center = $_screen_center(mode);
    var top = int((center.H-container.height())/2) - sh;
    var left = int((center.W-container.width())/2) - sw;

    if ($_screen_with_scroll('H') && is_null(without_scroll))
        top += $(window).scrollTop();

    container
        .css('top', $_get_css_size(top)).css('left', $_get_css_size(left))
        .show();
}

function $_init() {
    // ------------------------------------------
    // PAGE STARTER. Call it to begin manage page
    // ------------------------------------------
    is_webkit = !(isIE || IsMSIE) ? true : false;

    // Start app (menu.js)
    app.init();
    
    if (typeof $Init !== 'undefined' && is_function($Init))
        $Init();
        
    $ShowPage(0);
}

function $_change_location(state, url) {
    window.history.pushState(state, '');
    window.location.replace(url);
}

// ===============
// Action Handlers
// ===============

function $ShowPage(disable) {
    // ------------------------------------
    // Hides or shows global HTML-CONTAINER
    // ------------------------------------
    if (disable === null)
        return;
    var startup_page_container = $("#page-content");
    if (disable)
        startup_page_container.addClass("hidden").hide();
    else
        startup_page_container.removeClass("hidden").show();
}

function $ShowOnStartup() {
    // ---------------------------------------------------------------------------
    // Handles default startup action of the page: default_page_action (show page)
    // ---------------------------------------------------------------------------
    selected_menu_action = default_page_action;
    $Handle(
        selected_menu_action, default_handler, default_params
    );
}

function $ShowSystemMessages(reset, error) {
}

function $TriggerActions(disable) {
    if (IsTriggeredSubmit && default_submit_mode == 0)
        $ShowPage(disable);
}

function $getEnjectedLinks(head) {
    if (is_null(head))
        head = $("head");

    var selector = "link[ext='1']";
    if (IsDebug) {
        var tags = head.children(selector);
        alert('$cleanHead items count before: ' + tags.length);

        if (is_empty(tags))
            return;

        alert('$cleanHead items count after: ' + tags.length);
    }
    
    return head.children(selector);
}

function $cleanHead(head) {
    //
    // Clean statics in the page head.
    // Finds and removes tags with attr 'ext=1'
    //
    $getEnjectedLinks(head).remove();
}

function $updateHead(statics) {
    //
    //   Load statics into page head
    // 
    //   Arguments:
    //       statics -- list, 'link' tags array
    //
    var head = $("head");

    if (IsLog)
        console.log('$updateHead:', statics);

    if (is_empty(statics))
        return;

    $cleanHead(head);

    statics.forEach(function(item, index) {
        if (!is_empty(item)) {
            head.append(item);
        }
    });
}

function $show_error(banner, error, zindex_modal) {
    var container = $('#doc_modal');
    if (is_exist(container)) {
        zindex_dr_shadow = $('.modal-backdrop').css('z-index');
        zindex_modal = $('#doc_modal').css('z-index');

        $('#doc_modal').css('z-index', zindex_dr_shadow - 1);
    }

    $('#errors_docs_banner').empty();
    $('#error-human').empty();
    $('#errors_docs_banner').text(banner);
    $('#error-human').html(error.error_human_text);
    $('#errors_docs').modal('show');
}

function $ShowError(msg, is_ok, is_error, is_session_close) {
    if (is_show_error || !msg)
        return;

    if (!is_null(active_dialog))
        active_dialog.dialog("option", "closeOnEscape", false);

    var container = $("#error-container");

    $("#error-text").html(msg);

    if (is_ok) {
        $("#error-button").append(
            '<button id="error-button-ok" class="ui-button-text" onclick="javascript:$HideError();">'+keywords['OK']+'</button>'
        );
    }
    if (is_error)
        container.removeClass("warning").addClass("error");
    else
        container.removeClass("error").addClass("warning");

    $_show_window_in_center(container, null, true);
    
    is_show_error = true;

    $("#error-button-ok").focus();

    if (is_session_close) interrupt(true, -1, 5000, '', 0);
}

function $HideError() {
    $("#error-container").hide();
    $("#error-button").html('');

    if (!is_null(active_dialog))
        active_dialog.dialog("option", "closeOnEscape", true);

    is_show_error = false;

    $SetFocus();
}

function $SetFocus(ob) {
}

function $ShowLoader(start) {
    //alert('loader:'+start+':'+isWebServiceExecute);
}

function $ResetLogPage() {

}

function $Go(action) {
    if (IsLog) {
        console.log('$Go.action', action);
    }
    $web_logging(action);
}

function $Handle(action, handler, params) {
    if (IsLog) {
        console.log('$Handle.action:', action, handler, params);
    }
    $web_logging(action, handler, params);
}

function $setPaginationFormSubmit(page) {

}

// =======================
// Event's Action Handlers
// =======================

function $onParentFormSubmit(id) {

    // -------------------------------------------
    // Submit of current selected form by given id XXX
    // -------------------------------------------

    var frm = $("#"+(id || 'filter-form'));
    var action = frm.attr('action');

    var is_run = 1;

    try { 
        is_run = performance.navigation.type == 0 ? 1 : 0; 
    }
    catch(err) {}

    if (IsDeepDebug)
        alert('$onParentFormSubmit.begin:'+id+':'+[is_run, action].join(':'));

    if (is_run)
        $("#OK", frm).val('run');

    var ob = $("#window_scroll", frm);
    var top = is_on_refresh ? page_scroll_top : $(window).scrollTop();

    if (is_exist(ob))
        ob.val(!no_window_scroll ? top : '');

    if (IsDeepDebug)
        alert('$onParentFormSubmit.end:'+frm.attr('id')+':'+ob.val()+':'+top);

    frm.submit();
}

function $onLineFormSubmit(link, id, args) {

    // ---------------------------------------------------------------
    // Checks mode of submit: 0|1|2|3 - submit|location|loader|chapter
    // ---------------------------------------------------------------

    if (IsLog)
        console.log('$onLineFormSubmit:', default_submit_mode, args);

    $ShowPage(1);

    switch (default_submit_mode) {
        case 0:
            $onParentFormSubmit();
            break;
        case 1:
            $onPageLinkSubmit(link, args);
            break;
        case 2:
            $Handle(default_action, default_handler, default_params);
            break;
        case 3:
            // dialog_start
            var e = jQuery.Event( "click", {location:link, args:args} );
            //console.log('Event:', e);
            $( "#"+id ).trigger(e);
            break;
    }
}

function $onPageLinkSubmit(link, args) {

    // ----------------------------------------
    // Submit by link. Changes location
    // Note! window.location is not a string!!!
    // ----------------------------------------

    if (IsTrace)
        alert('$onPageLinkSubmit.link:'+link);

    url = makeQueryString(link, args);

    if (IsDebug)
        alert('$onPageLinkSubmit.url:'+url);

    window.location.replace(url);
}

jQuery(function($) 
{

    // ---------------
    // Keyboard Events
    // ---------------

    $(window).keydown(function(e) {
        var exit = false;

        if (is_show_error && e.keyCode == 27) {      // Esc
            $HideError();
        }

        if (exit) {
            e.preventDefault();
            return false;
        }
    });
});

