// ********************************
// HELPER FUNCTION CONTROLS MANAGER
// --------------------------------
// Version: 1.0
// Date: 05-20-2023

// =======================
// Component control class
// =======================

var $PageController = {
    callbacks : null,
    container : null,
    group : '',

    timer : null,

    IsDebug : 0, IsTrace : 0, IsLog : 0,

    init: function(action, default_action) {
        this.group = selector.group || 'docs';
        if (this.IsTrace)
            alert('docs.$PageController.init: '+action+':'+default_action);
    },

    _init_state: function() {
        if (this.IsLog)
            console.log('docs.$PageController._init_state:');
    },

    reset: function(force) {},

    trace: function(force) {},

    default_action: function(action, args) {
        if (action == default_action) {
            ObjectUpdate(args, {
                'change_id' : SelectedGetItem(this.group, 'id'),
                'row_id' :  selector.id,
                'param_status' : '',  //$("#paramstatus").val()
                'group' : selector.group
            });
        }
        return action;
    },

    action: function(action, args, params) {
        if (action > default_action) {
            var group = selector.group;
            var mode = selector.mode;
            ObjectUpdate(args, {
                'action' : action,
                'command': $("#command").val(),
                'change_id' : SelectedGetItem(group, 'id'),
                'group' : group,
                'mode' : mode, 
                'row_id' :  selector.id,
                'content' : $("#config_content").val(),
            });

            if (this.IsTrace)
                alert('docs.$PageController.action:'+action+', group:'+this.group+', change_id:'+args.change_id);

            if (this.IsLog)
                console.log('docs.$PageController.action:', action, args);
        }
    },

    updateView: function(action, callbacks, response, props, total) {
        if (this.IsLog)
            console.log('docs.$PageController.updateView', action, response, props, total);
    },

    sleep: function(callback, timeout) {
        if (this.IsDebug)
            alert('docs.$PageController.sleep:'+timeout);
        this.timer = setTimeout(callback, timeout);
    },

    clear_timeout: function() {
        if (!is_null(this.timer)) {
            clearTimeout(timer);
            this.timer = null;
        }
    },

    activate: function(group, row_id, next_row, chunk) {
        this.clear_timeout();

        if (this.IsLog)
            console.log('docs.$PageController.activate.before:', group, row_id, this.container);
    }
};
