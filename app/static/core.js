// ====================================
//  CORE JAVASCRIPT LOWLEVEL FUNCTIONS
// ====================================

/****
 * 
 *  is_null  -- checked if given item is undefined or null
 * 
 *  is_empty -- checked if given item is undefined or empty (0, '', [], {})
 * 
 *  is_exist -- checked if given item exists in jQuery DOM (has length more zero)
 * 
 *  Functions to operate with object attrs under js-objects by given id (jsonify):
 *      getattr -- get attr value by key (id)
 *      setattr -- set attr value by key with given value
 *      getvalue, setvalue -- operates under value of jQuery object (DOM items)
 * 
 *  is_function -- checked if given object exists and is a function
 * 
 *  capitalize -- make string value capitalized 
 * 
 ***/

function is_null(x) { return (typeof(x) === 'undefined' || x === null || x === undefined) ? true : false; }

function int(x) { return parseInt(x); }

function is_empty(x) { return (is_null(x) || x.toString().length == 0 || (!isNaN(x) && int(x)==0)) || x == '---' ||
    (typeof(x)==='object' && Object.keys(x).length == 0) ? true : false; }

function is_exist(x) { return !is_null(x) && x.length > 0 ? true : false; }

function getattr(ob, id, value) { return (typeof(ob)=='object' && !is_null(ob) && id in ob) ? ob[id] : value; }

function setattr(ob, id, value) { if (typeof(ob)=='object' && !is_null(ob) && id in ob) ob[id] = value; }

function getvalue(ob, value) { return (typeof(ob)=='object' && is_exist(ob)) ? ob.val() : value; }

function setvalue(ob, value) { if (typeof(ob)=='object' && is_exist(ob)) ob.val(value); }

function getprop(ob, prop, value) { return (typeof(ob)=='object' && is_exist(ob)) ? ob.prop(prop) : value; }

function setprop(ob, prop, value) { if (typeof(ob)=='object' && is_exist(ob)) ob.prop(value); }

function is_function(ob) { return (!is_null(ob) && typeof(ob) === 'function' ? 1: 0) };

function capitalize(name) {
    return name.charAt(0).toUpperCase() + name.slice(1);
}

/***
 *  Functions to operate under URL query string
 * 
 ***/


function makeLocation(query_string, key, value) {
    //
    // Returns a updated query string for change location
    //

    if (query_string.startswith('?'))
        query_string = query_string.slice(1);

    var args = '{'
        + (query_string.length > 0 ? '"'+decodeURI(query_string.replace(/&/g, '","').replace(/=/g,'":"'))+'"' : '') 
        + '}';

    params = JSON.parse(args);
    
    params[key] = value;
    
    var url = '?' + Object.keys(params).map(function(key) { return key+'='+params[key]; }).join('&');
    
    return url;
}

function makeQueryString(link, args) {
    //
    // Returns encoded a JavaScript object into a string that we can pass via a GET request
    //

    var x = link.split('?');
    var url = x[0];
    var qs = x.length > 1 ? strip(x[1]) : '';
    var str = [];

    if (!is_empty(args)) {
        for (var p in args) {
            if (args.hasOwnProperty(p) && !is_null(getattr(args, p))) {
                str.push(encodeURIComponent(p) + "=" + encodeURIComponent(args[p]));
            }
        }
    }

    url = url + '?' + qs;
    
    if (!is_empty(str)) {
        var params = str.join("&");

        url = url + (qs && params ? '&': '') + params;

    }

    if (url.endswith('?'))
        url = url.slice(0, -1);

    return url;
}

// -----------------------------------------
//  Prototypes under Date object extensions
// -----------------------------------------

Date.prototype.getCorrectYear = function() {
    var y = this.getYear() % 100;
    return (y < 38) ? y + 2000 : y + 1900;
};

Date.prototype.getTwoDigitMonth = function() {
    return (this.getMonth() < 9) ? '0' + (this.getMonth()+1) : (this.getMonth()+1);
};

Date.prototype.getTwoDigitDate = function() {
    return (this.getDate() < 10) ? '0' + this.getDate() : this.getDate();
};

Date.prototype.getTwoDigitHour = function() {
    return (this.getHours() < 10) ? '0' + this.getHours() : this.getHours();
};

Date.prototype.getTwoDigitMinute = function() {
    return (this.getMinutes() < 10) ? '0' + this.getMinutes() : this.getMinutes();
};

Date.prototype.getTwoDigitSecond = function() {
    return (this.getSeconds() < 10) ? '0' + this.getSeconds() : this.getSeconds();
};

Date.prototype.getISODate = function() {
    return this.getCorrectYear() + '-' + this.getTwoDigitMonth() + '-' + this.getTwoDigitDate();
};

Date.prototype.getHourMinute = function() {
    return this.getTwoDigitHour() + ':' + this.getTwoDigitMinute();
};

Date.prototype.getHourMinuteSecond = function() {
    return this.getTwoDigitHour() + ':' + this.getTwoDigitMinute() + ':' + this.getTwoDigitSecond();
};

Date.prototype.getToday = function() {
  var mm = this.getMonth() + 1;
  var dd = this.getDate();
  return [this.getFullYear(), (mm>9 ? '' : '0') + mm, (dd>9 ? '' : '0') + dd].join('-');
};

// -------------------------------------------
//  Prototypes under String object extensions
// -------------------------------------------

String.prototype.pad_left = function(pad_length, pad_string) {
    var new_string = this;
    for (var i = 0; new_string.length < pad_length; i++) {
        new_string = pad_string + new_string;
    }
    return new_string;
};

String.prototype.startswith = function(s) {
    return (s && this.substr(0, s.length) == s) ? true : false;
};

String.prototype.endswith = function(s) {
    return (s && this.substr(-s.length) == s) ? true : false;
};

String.prototype.key_is_inside = function(s, key) {
    return (s && s.indexOf(key) > -1) ? true : false;
};

function strip(s) {
    return s.replace(/^\s+|\s+$/g, ''); // trim leading/trailing spaces
}

function dumping(ob) {
    var s = '';
    if (typeof(ob) != 'object')
        s = ob.toString();
    else {
        try { 
            for (p in ob) s += p+'['+ob[p].toString()+']:'; 
        }
        catch(e) {}
    }
    return s;
}

var htmlMap = {
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': '&quot;',
    "'": '&#39;',
    "/": '&#x2F;'
};

function escapeHtml(string) {
    return String(string).replace(/[&<>"'\/]/g, function (s) {
        return htmlMap[s];
    });
}

function cleanTextValue(string) {
    return String(string).replace(/[&<>"'\/]/g, function (s) {
        return '';
    });
}

function right(str, chr)
{
    return str.slice( -( chr ) );
}
function left(str, chr)
{
    return str.slice( 0, chr );
}

// ----------------------------------------
//  Get the computed style for and element
// ----------------------------------------

function getStyle(oElm, strCssRule) {
    var strValue = "";

    if (document.defaultView && document.defaultView.getComputedStyle) {
        strValue = document.defaultView.getComputedStyle(oElm, "").getPropertyValue(strCssRule);
    }
    else if (oElm.currentStyle) {
        strCssRule = strCssRule.replace(/\-(\w)/g, function (strMatch, p1){
            return p1.toUpperCase();
        });
        strValue = oElm.currentStyle[strCssRule];
    }

    return strValue;
}

// -------------------------
//  Prototypes under Arrays
// -------------------------

if (!Array.prototype.forEach) Array.prototype.forEach = function(callback) {
    var T, k;

    if (this == null) {
        throw new TypeError('this is null or not defined');
    }

    var O = Object(this);
    var len = O.length >>> 0;

    if (typeof callback !== 'function') {
        throw new TypeError(callback + ' is not a function');
    }

    if (arguments.length > 1) {
        T = arguments[1];
    }

    k = 0;
    while (k < len) {
        var kValue;
        if (k in O) {
            kValue = O[k];
            callback.call(T, kValue, k, O);
        }
        k++;
    }
};

if (!Array.prototype.indexOf) Array.prototype.indexOf = function(value) {
    for (var i=0; i<this.length; i++) {
        if (this[i] === value) return i;
    }
    return -1;
};

if (typeof Array.isArray === 'undefined') {
    Array.isArray = function(obj) {
        return Object.prototype.toString.call(obj) === '[object Array]';
    }
};

Array.prototype.isEqual = function(arr) {
    if (this.length != arr.length)
        return false;
    for(var i=0; i<this.length; i++) {
        if (this[i] != arr[i])
            return false;
    }
    return true;
};

Array.prototype.makeEqual = function() {
    var value = new Array();
    for(var i=0; i<this.length; i++) {
        value.push(this[i]);
    }
    return value;
};

Array.prototype.remove = function(value) {
    for(var i=0; i<this.length; i++) {
        if (this[i] === value) {
            this.splice(i,1);
            break;
        }
    }
};

Array.prototype.sum = function() {
    return this.reduce(function(a, b) { return a + b; }, 0);
};

Array.prototype.max = function() {
  return Math.max.apply(null, this);
};

Array.prototype.min = function() {
  return Math.min.apply(null, this);
};

Array.prototype.unique = function() {
    var a = this.concat();
    for(var i=0; i<a.length; ++i) {
        for(var j=i+1; j<a.length; ++j) {
            if(a[i] === a[j])
                a.splice(j--, 1);
        }
    }
    return a;
};

Array.prototype.union = function(arr) {
    var out = new Array();
    this.concat(arr).forEach(function(x) {
        if (out.indexOf(x) == -1)
            out.push(x);
    });
    return out;
};

// --------------------------
//  Prototypes under Objects
// --------------------------

function setObjectByValue(key, value) {
    var x = new Object();
    x[key] = value;
    return x;
}

function getObjectValueByKey(ob, key, value) {
    return !is_empty(ob) && (key in ob) ? ob[key] : value;
}

function objectKeys(ob) {
    return ob ? Object.keys(ob) : [];
}

function objectValues(ob) {
    return ob ? Object.values(ob) : [];
}

function objectItems(ob) {
    return ob ? Object.entries(ob) : [];
}

function objectKeyValues(ob) {
    return '{'+Object.keys(ob).map(function (key) { return key+':'+(typeof ob[key] === 'object' ? 'Object' : ob[key]); })+'}';
}

function reprObject(ob) {
    var s = is_null(ob) ? 'null' : '{'+Object.keys(ob).map(function (key) { 
        return key+':'+(typeof ob[key] === 'object' ? reprObject(ob[key]) : ob[key]); 
    })+'}';
    return s;
}

function reprObjectsList(obs) {
    var s = '';
    obs.forEach(function(item, index) {
        var x = '{'+Object.keys(item).map(function (key) { return key+':'+item[key]; })+'}';
        s += x.join(',');
    });
    return s;
}

function joinToPrint(values, delimeter) {
    return values.join(delimeter || ':');
}

function get_option_values(key, delimeter) {
    if (is_empty(delimeter))
        delimeter = default_option_delimeter
    values = [];
    $('input[id^="'+key+'"]').each(function(index) {
        var item = $(this);
        var value = item.attr('value');
        var is_check = ['checkbox','radio'].indexOf(item.prop('type')) > -1 ? true : false;
        if (is_check && int(value) > 0 && item.prop('checked'))
            values.push(delimeter+value+delimeter);
    });
    return joinToPrint(values);
}

function makeTempObject(s) {
    var ob = {};
    var items = s.split(',') || [];
    items.forEach(function(x) {
        var item = x.split(':');
        ob[item[0]] = item[1];
    });
    return ob;
}

function jsonify(ob) {
    if (typeof(ob) === 'object') {
        Object.keys(ob).map(function(key, index) {
            if (is_null(ob[key]))
                ob[key] = '';
        });
        return JSON.stringify(ob);
    }
    else
        return ob;
}

function difference(x1, x2) {
    return Math.max(x1, x2) - Math.min(x1, x2);
}

function ObjectAssign(target, sources) {
    // --------------------
    // JS CLASS INHERITANCE
    // --------------------
    // var $dialog = ObjectAssign({}, [class1, class2, ...]);
    // alert(joinToPrint(objectKeys($dialog), ':'));
    // alert(reprObject($dialog));
    //
    sources.forEach(function(source) {
        Object.defineProperties(
            target, 
            Object.keys(source).reduce(function(descriptors, key) {
                descriptors[key] = Object.getOwnPropertyDescriptor(source, key);
                return descriptors;
            }, {})
        );
    });
    return target;
}

function ObjectUpdate(ob/*, …*/) {
    for (var i=1; i<arguments.length; i++) {
        for (var prop in arguments[i]) {
            var val = arguments[i][prop];
            if (typeof val == "obect") // this also applies to arrays or null!
                ObjectUpdate(ob[prop], val);
            else
                ob[prop] = val;
        }
    }
    return ob;
}


// ----------------
// Global namespace
// ----------------

//var self = window;

var $SCRIPT_ROOT = '';
var $IS_MOBILE = false;
var $IS_FRAME = true;
var $IS_DEMO = false;
var isIE = 0;
var isFirefox = 1;

var n_a = 'n/a';
