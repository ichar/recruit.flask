// ********************************
// FRONT SIDE PAGE CONTROLS MANAGER
// --------------------------------
// Version: 3.00
// Date: 20-01-2023

// =================================
// Common Page Controls declarations
// =================================


var $ConfirmDialog = {
    container : null,
    opened    : false,
    focused   : false,

    init: function() {
        this.container = $("#confirm-container");
    },

    is_focused: function() {
        return this.focused;
    },

    open: function(msg, width, height, title) {
        if (this.opened)
            return;

        this.init();

        this.opened = true;
        this.focused = true;

        this.setContent(msg);

        this.container.dialog("option", "title", !is_empty(title) ? title : keywords['Confirm notification form']);

        if (!is_empty(width))
            this.container.dialog("option", "width", width);
        if (!is_empty(height))
            this.container.dialog("option", "height", height);

        this.container.dialog("open");
    },

    onClose: function() {
        this.opened = false;
        this.focused = false;
    },

    setContent: function(msg) {
        var box = $("#confirm-info");
        var s = '<p>'+msg.replace(/{/g, '<').replace(/}/g, '>')+'</p>';

        isConfirmation = true;

        box.html(s);
    },

    cancel: function() {
        this.focused = false;
        this.close();
    },

    close: function() {
        isConfirmation = false;

        this.container.dialog("close");
        this.onClose();
    }
};

var $NotificationDialog = {
    container : null,

    opened    : false,
    focused   : false,

    init: function() {
        this.container = $("#notification-container");
    },

    is_focused: function() {
        return this.focused;
    },

    open: function(msg, width, height, title) {
        if (this.opened)
            return;

        this.init();

        this.opened = true;
        this.focused = true;

        this.setContent(msg);

        this.container.dialog("option", "title", !is_empty(title) ? title : keywords['Notification form']);

        if (!is_empty(width))
            this.container.dialog("option", "width", width);
        if (!is_empty(height))
            this.container.dialog("option", "height", height);

        this.container.dialog("open");
    },

    onClose: function() {
        this.opened = false;
        this.focused = false;
    },

    setContent: function(msg) {
        var box = $("#notification-info");
        var s = '<p>'+msg.replace(/{/g, '<').replace(/}/g, '>')+'</p>';

        isNotificationation = true;

        box.html(s);
    },

    cancel: function() {
        this.focused = false;
        this.close();
    },

    close: function() {
        isNotificationation = false;

        this.container.dialog("close");
        this.onClose();
    }
};


// =======
// Dialogs
// =======

jQuery(function($) 
{

    // --------------------
    // Confirm form: Yes/No
    // --------------------

    $("#confirm-container").dialog({
        autoOpen: false,
        width:400,
        //height:600,
        //position:0,
        buttons: [
            {text: keywords['yes'], click: function() { $Confirm(1, $(this)); }},
            {text: keywords['no'], click: function() { $Confirm(0, $(this)); }}
        ],
        modal: true,
        draggable: true,
        resizable: false,
        position: {my: "center center", at: "center center", of: window, collision: "none"},
        create: function (event, ui) {
            $(event.target).parent().css("position", "fixed");
        },
        close: function() {
            $ConfirmDialog.onClose();
        }
    });

    // ----------------------
    // Notification form: Yes
    // ----------------------

    $("#notification-container").dialog({
        autoOpen: false,
        width:400,
        //height:600,
        //position:0,
        buttons: [
            {text: keywords['OK'], click: function() { $Notification(1, $(this)); }},
        ],
        modal: true,
        draggable: true,
        resizable: false,
        position: {my: "center center", at: "center center", of: window, collision: "none"},
        create: function (event, ui) {
            $(event.target).parent().css("position", "fixed");
        },
        close: function() {
            $NotificationDialog.onClose();
        }
    });
});
