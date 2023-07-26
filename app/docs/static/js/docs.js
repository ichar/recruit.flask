// *********************************************
// APPLICATION FORMS PAGE DECLARATION: /docs.js
// ---------------------------------------------
// Version: 1.00
// Date: 18-05-2023

default_submit_mode = 3;
default_action      = '200';
default_page_action = '201';
default_input_name  = 'doc_id';

var mode = '';
var valid_reporttypes = ['doc01', 'doc02', 'doc03', 'doc04', 'doc05', 'doc16', 'doc06', 'doc07', 'doc08', 'doc09', 'doc10', 'doc11', 'doc12', 'doc13', 'doc14', 'doc15'];

var show = 0;


function activate() {
    var cls = 'active';
    var ob = $("#form_data");
    if (!ob.hasClass(cls)) {
        $("."+cls).removeClass(cls);
        ob.addClass(cls);
    }
}

// --------------
// Page Functions
// --------------

function make_error(message) {
    //alert('make_error');
    //$ShowError(message, true, true, false);
    var error = { error_human_text:message };
    show_error('Предупреждение', error);
}

function make_notification(x) {
    $NotificationDialog.open(keywords['Message:Action was done successfully']);
}

function check_item(item, is_checked) {
    var value = item.attr('value');
    var checked = !is_empty(is_checked) ? 1 : 0;
    var is_check = ['checkbox','radio'].indexOf(item.prop('type')) > -1 ? true : false;
    if (is_check && int(value) > 0)
        item.prop('checked', checked);
}

function set_sign(ob, is_checked) {
    var oid = ob.attr('id');
    var sign = $("#"+oid+'-sign');
    sign.html(is_checked ? '+': '-');
}

function set_checked(key, is_checked) {
    $('input[id^="'+key+'"]').each(function(index) {
        check_item($(this), is_checked);
    });
}

function checkTree(ob, key, is_checked) {
    var oid = ob.attr('id');
    var child = $("#"+oid+'_child');

    $('input[id^="'+key+'"]', child).each(function(index) {
        var item = $(this);
        check_item(item, is_checked);
        set_sign(item, is_checked);
    });
}

function showTree(ob) {
    var oid = ob.attr('id');
    var child = $("#"+oid+'_child');
    var base = $('#params');
    var root = $("#region_root");
    var sign = $("#"+oid+'-sign');

    if (!is_exist(child)) {
        sign.html(sign.html() == '-' ? '+' : '-');
        return;
    }

    var is_closed = child.hasClass('invisible') ? 1 : 0;

    var cid = child.attr('id');

    //alert('showTree.oid:'+oid+':'+is_closed);

    if (is_closed) {
        child.removeClass('invisible');
        child.css({ 
                position : "relative", 
            });
        child.show();
        sign.html('-');
    }
    else {
        child.addClass('invisible');
        child.hide();
        sign.html('+');
    }    
}

function $Notification(mode, ob) {
    $NotificationDialog.close();

    if (mode == 1) {
        switch (confirm_action) {
            case 'order.checked':
            case 'decree.checked':
                $ProvisionSelectorDialog.exit();
        }
    }

    confirm_action = '';
}

function $upload() {
    $Handle('100', null, { 'mode': mode || 'docs' });
}

function $Init() {

    if (IsTrace)
        alert('$Init');

    activate();

    // ------------------------
    // Start default log action
    // ------------------------

    interrupt(true, 1);
}

// ===========================
// Dialog windows declarations
// ===========================

function MakeFilterSubmit(mode, page) {
    // XXX
    //$("#filter-form").attr("action", baseURI);

    switch (mode) {

        // -------------
        // Submit modes:
        // -------------

        case 0:
        case 1:
        case 2:
        case 3:
        case 4:
        case 5:
            break;

        // ---------------------------
        // LineSelector Handler submit
        // ---------------------------

        case 9:
    }

    $ResetLogPage();

    $setPaginationFormSubmit(page);
    $onParentFormSubmit('filter-form');
}

function MakeReport(reporttype) {
    if (IsTrace)
        alert('MakeReport:'+reporttype);

    var frm = $('#command-form');
    var date_from = $("#date_from", frm);
    var date_to = $("#date_to", frm);
    var person = $("#person", frm);
    var speciality = $("#speciality_root", frm);
    var region = $("#region_root", frm);

    switch (reporttype) {
    case 'doc01':
    case 'doc03':
    case 'doc06':
    case 'doc07':
    case 'doc08':
        date_from.prop("disabled", 0);
        date_to.prop("disabled", 0);
        person.prop("disabled", 1);
        speciality.addClass('hidden');
        region.addClass('hidden');
        break;
    case 'doc02':
    case 'doc04':
    case 'doc05':
    case 'doc16':
        date_from.prop("disabled", 1);
        date_to.prop("disabled", 1);
        person.prop("disabled", 0);
        speciality.addClass('hidden');
        region.addClass('hidden');
        break;
    case 'doc09':
    case 'doc10':
    case 'doc11':
    case 'doc12':
    case 'doc13':
    case 'doc14':
    case 'doc15':
        date_from.prop("disabled", 0);
        date_to.prop("disabled", 0);
        person.prop("disabled", 1);
        speciality.removeClass('hidden');
        region.removeClass('hidden');
        break;
    }
}

function get_region_value(forced) {
    var value = '';
    var frm = $('#command-form');
    var ob = $("#regions", frm);
    if (!forced && is_exist(ob))
        value = ob.val();
    else
        value = get_option_values('region');
    //alert(value);
    return value;
}

function get_speciality_value(forced) {
    var value = '';
    var frm = $('#command-form');
    var ob = $("#specialities", frm);
    if (!forced && is_exist(ob))
        value = ob.val();
    else
        value = get_option_values('speciality');
    //alert(value);
    return value;
}

function getReportParams(forced) {
    var frm = $('#command-form');
    var date_from = $("#date_from", frm).val();
    var date_to = $("#date_to", frm).val();
    var person_uid = $("#person", frm).val();
    var speciality_index = get_speciality_value(forced);
    var region_index = get_region_value(forced);
    var args = {
        'date_from' : date_from,
        'date_to' : date_to,
        'person_uid' : person_uid,
        'speciality_index' : speciality_index,
        'region_index' : region_index
    }
    return args;
}

function CheckReportParams(reporttype) {
    if (IsTrace)
        alert('CheckReportParams:'+reporttype);

    args = getReportParams();

    var date_from = args.date_from;
    var date_to = args.date_to;
    var person_uid = args.person_uid;
    var speciality_index = args.speciality_index;
    var region_index = args.region_index;

    //alert('['+date_from+']:'+ is_empty(date_from));

    switch (reporttype) {
    case 'doc01':
    case 'doc03':
    case 'doc06':
    case 'doc07':
    case 'doc08':
    case 'doc09':
    case 'doc10':
    case 'doc11':
    case 'doc12':
    case 'doc13':
    case 'doc14':
    case 'doc15':
        if (is_empty(date_from)) {
            make_error(keywords['Should be present date from-to value']);
            return 0;
        }
        break;
    }
    switch (reporttype) {
    case 'doc02':
    case 'doc04':
    case 'doc05':
    case 'doc16':
        if (is_empty(person_uid)) {
            make_error(keywords['Should be present person value']);
            return 0;
        }
        break;
    }
    switch (reporttype) {
    case 'doc09':
    case 'doc10':
    case 'doc11':
    case 'doc12':
    case 'doc13':
    case 'doc14':
    case 'doc15':
        if (is_empty(speciality_index)) {
            make_error(keywords['Should be present speciality value']);
            return 0;
        }
        if (is_empty(region_index)) {
            make_error(keywords['Should be present region value']);
            return 0;
        }
        break;
    }

    return 1;
}

function printReport(show) {
    var id = "report_container";
    var title = document.title;
    var container = $("#"+id);
    if (!is_exist(container))
        return false;

    var report_body = container[0].outerHTML;

    console.log(title, report_body.length);

    var body = '<!DOCTYPE html>' +
        '<html><head><title>' + title  + '</title>\n' +
        '<meta charset="UTF-8">' +
        '<meta http-equiv="Cache-Control" content="must-revalidate">' +
        '<meta http-equiv="Pragma" content="no-cache">' +
        'HIDE_SCREEN\n' +
        '<style type="text/css" media="screen,print">\n' +
        '@page { size:'+ orientation +' }\n' +
        'body { margin:0 20px 0 20px; font-family:Arial,Tahoma; background-color:#ffffff; }\n' +
        '#page_container { margin:0px auto; padding:0; overflow:hidden; }\n' +
        '</style>' +
        '</head><body><div id="page_container">' + report_body + '</div>' +
        '<style type="text/css">\n' +
        '.document, .report, report-container { border:none !important; }\n' +
        '.page-break { page-break-before: auto; break-before: auto; }\n' +
        '</style>' +
        '</body></html>';

    body = body.replace(/HIDE_SCREEN/g,
        (show ? '' : '<style type="text/css" media="screen">body { display:none; }</style>'));

    var w = window.open('', '_blank');

    w.document.open('','','');
    w.document.write(body);
    w.document.close();

    if (show == 0) {
        w.print();
        w.close();
    }
}

// ====================
// Page Event Listeners
// ====================

jQuery(function($)
{

    // -----------
    // Page Events
    // -----------

    $(".sign").on('click', function(e) {
        var item = $(this);
        var id = item.attr('id');
        var x = id.split('-');
        var oid = x[0];
        var ob = $("#"+oid);

        showTree(ob);

        e.preventDefault();
        e.stopPropagation();
    });

    $(".check-region").on('click', function(e) {
        var item = $(this);
        var id = item.attr('id');
        var x = id.split('_');
        var is_checked = item.prop('checked') ? 1 : 0;

        //alert('click: '+id+' : '+is_checked);
        
        is_noprogress = true;

        $DblClickAction.click(
            function(ob) {
                is_noprogress = false;
                //alert('click on: '+ob.attr('id')+', key:'+x[0]);
                checkTree(ob, x[0], is_checked);
            },
            function(ob) {
                showTree(ob);
            },
            item
        );
    })
    .on("dblclick", function(e){
        e.preventDefault();
    });

    $(".check-speciality").on('click', function(e) {
        var item = $(this);
        var id = item.attr('id');
        var x = id.split('_');

        if (x[1] == '0') {
            var is_checked = item.prop('checked') ? 1 : 0;
            //alert('checked='+is_checked+' : '+item.prop('checked'));
            set_checked('speciality', is_checked);
        }
    });

    $(".reporttype").on('click', function(e) {
        var id = $(this).attr('id');
        var reporttype = id.split('_')[1];

        MakeReport(reporttype);
    });

    $("button").on('click', function(e) {
        var id = $(this).attr('id');
        var link = '';
        var reporttype = '';

        if (IsTrace)
            alert('on button click, id:' + id);
        switch (id) {

            case 'page_main':
                link = '/auth/default';
                break;
            case 'page_back':
                link = '/docs/index';
                break;
            case 'make_report':
                reporttype = $("input[name=reporttype]:checked", '#command-form').val();
                if (!is_null(reporttype) && valid_reporttypes.indexOf(reporttype) > -1 && CheckReportParams(reporttype))
                    link = '/docs/' + reporttype;
                break;
            case 'page_print':
                printReport(show);
        }

        if (!is_empty(link)) {
            var args = getReportParams(0);
            //alert(link);
            $onLineFormSubmit(link, 'form_data', args);
        }
    });

})

function page_is_focused(e) {
    return 0;
}

// =======
// STARTER
// =======

$(function()
{
    IsTrace = 0;
    IsLog = 0;

    mode = $("#page").val();

    if (IsTrace)
        alert('Document Ready ('+mode+')'+' submit mode:'+default_submit_mode);

    //if (default_submit_mode == 3) $upload();

    IsActiveScroller = 0;

    current_context = mode;
    isKeyboardDisabled = false;

    $("#search-context").attr('placeholder', keywords['Search Find'+mode]+'...');

    //document.oncontextmenu = function() { return false; };

    $_init();
});
