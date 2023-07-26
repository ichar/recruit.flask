// ************************
// FRONT SIDE DB CONTROLLER
// ------------------------
// Version: 3.00
// Date: 20-01-2023

var search_context = '';                // Current search context value

var is_noprogress = false;

// ****************************************************

var $DblClickAction = {
    control   : null,

    // =========================
    // DoubleClick Handler Class
    // =========================

    clicks    : 0,
    timeout   : 300,
    timer     : null,

    single    : null,
    double    : null,

    reset: function() {
        this.control = null;
        this.clicks = 0;
        this.timer = null;
        this.single = null;
        this.double = null;
    },

    click: function(single, double, control, timeout) {
        this.control = control;
        this.single = single;
        this.double = double;

        this.clicks++;

        if (this.clicks === 1) {

            this.timer = setTimeout(function() {
                var self = $DblClickAction;

                // -------------------
                // Single-click action
                // -------------------

                self.single && self.single(self.control);
                self.reset();

            }, timeout || this.timeout);

        } else if (!is_null(this.timer)) {
                var self = $DblClickAction;

                // -------------------
                // Double-click action
                // -------------------

                clearTimeout(this.timer);

                //this.single && this.single(self.control);
                this.double && this.double(self.control);
                this.reset();

        }
    }
};

// ============
// WEB-SERVICES
// ============

function $web_free() {
/***
 *  Semaphore: is controller busy or not true|false.
 */
    return !isWebServiceExecute ? true : false;
}

function $is_shown_error() {
/***
 *  Semaphore: is error shown on the screen true|false.
 */
    return is_show_error ? true : false;
}

function $web_busy() {
/***
 *  Semaphore: is controller busy true|false.
 */
    return (isWebServiceExecute || is_show_error) ? true : false;
}

function $web_logging(action, handler, params) {
/***
 *  General AJAX-backside handler.
 *  Used to interact with the core of the application.
 *
 *  Action:        action number (000-999)
 *  [Handler]:     handler (to process the returned data)
 *  [Params]:      query data (object)
 *
 *  System args and state-items:
 * 
 *  $SCRIPT_ROOT - root-part of URL
 *  loader_page  - page name, may be omitted
 *  loaderURI    - path to backside handler (/loader)
 * 
 *  isWebServiceExecute: loader is busy 1|0
 *  is_show_error: got error or not 1|0
 * 
 *  Hard link.
 */
    var uri = $SCRIPT_ROOT + loader_page + loaderURI;

    if (IsDeepDebug)
        alert('>>> web_logging.uri:'+uri+', action:'+action+':'+isWebServiceExecute+':'+is_show_error);

    if ($web_busy())
        return;

    var current_action = action;
    var args = new Object();

    if (IsLog) {
        console.log('$web_logging, action:', action, selected_menu_action, uri);
    }

    // -----------------------
    // Check Action parameters
    // -----------------------

    //$PageController.init(action, default_action);

    args = {
        'action' : action,
        'selected_menu_action' : selected_menu_action,
    };

    if (!is_null(params))
        args['params'] = jsonify(params);

    var error = {
        'exchange_error'    : 0, 
        'exchange_message'  : '', 
        'error_description' : '', 
        'error_code'        : '', 
        'errors'            : ''
    };

    if (IsLog) {
        console.log('$web_logging, args with params:', args, current_action);
    }

    // ------------
    // START ACTION
    // ------------

    $TriggerActions(true);

    is_loaded_success = false;

    if (IsLog) {
        console.log('$web_logging.uri:', $SCRIPT_ROOT+loaderURI);
    }

    $ShowSystemMessages(true, true);
    $ShowLoader(1);

    $.post(uri, args, function(response) {
        var action = response['action'];

        // -----------------------
        // Server Exchange erorors
        // -----------------------

        error.exchange_error = parseInt(response['exchange_error'] || 0);
        error.exchange_message = response['exchange_message'];

        if (IsTrace)
            alert('$web_logging.post:'+action+':'+uri);

        if (IsLog)
            console.log('$web_logging.post:'+action+':'+current_action+':'+default_action, 'error:', error.exchange_error);

        var total = parseInt(response['total'] || 0);
        var status = response['status'];
        var path = response['path'];
        var data = response['data'];
        var props = response['props'];
        var columns = response['columns'];

        var refresh_state = true;

        // --------
        // RESPONSE
        // --------

        $ShowLoader(-1);

        if (typeof log_callback_error === 'function' && should_be_updated) {
            var errors = response['errors'];
            log_callback_error(action, errors);
        }

        if (error.exchange_error)
            refresh_state = false;

        else if (!is_null(handler)) {

            var type_of_handler = typeof handler;

            if (IsTrace)
                alert('$web_logging.handler:'+action+':'+type_of_handler);

            handler(response);
        }

        // -----------------------------------------
        // Run default action (change LINE position)
        // -----------------------------------------

        else if (['100', '101', '102'].indexOf(action) > -1) 
        {
            $updateHead(getattr(data, 'statics'));
        }
        else if (current_action == default_action)
        {
            $updateSublineData(current_action, response, props, total, status, path);
        }
        else if (action == default_page_action)
        {
            $updatePage(current_action, response);
        }
        else
        {
            $updateViewData(current_action, response, props, total, status, path);
        }

        is_loaded_success = true;

        $TriggerActions(false);

        //$ShowLogPage();

        // --------------------
        // Run Callback Handler
        // --------------------

        if (isCallback) {
            isCallback = false;

            if (typeof log_callback === 'function')
                log_callback(current_action, data, props);
        }

    }, 'json')
    .fail(function() {
        is_loaded_success = false;
    })
    .always(function() {
        if (page_state == -1)
            page_state = 0;

        $ShowLoader(-1);
        $TriggerActions(false);
    });
}
