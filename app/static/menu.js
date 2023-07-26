'use strict';

//Приложение
var app = (function () {

  var timer = null;

  function _dialog_start(e) {
     //  -------------------
     //  AJAX POST callpoint
     //  -------------------

    var location = 'location' in e ? e.location : e.data.location;
    var args = getattr(e, 'args');

    //console.log('_dialog_start:', e, args);

    if (IsTrace)
        alert('_dialog_start: '+e.currentTarget.id+':'+location);

    $('.a-pointer').removeClass('active');

    $('#' + e.currentTarget.id).addClass('active');

    if (window.proc) {
      clearInterval(window.proc);
    }
    if (!timer) {
      timer = window.setTimeout(function() {
        window.clearTimeout(timer);
        timer = null;
        chapter.info(location, args).done(function (dataHtml) {
          var ob = $('#page-content');
          ob.off('click.pageNameSpace');
          ob.empty().append(dataHtml);
          if (!is_function($ShowPage)) ob.removeClass('hidden');
          $('#admin_manager').attr('href', '');
          $('#admin_manager').attr('href', '/manager/admin_panel?previous_active_choise=' + e.currentTarget.id);
          //$('#' + $('#sidebar').attr('data-anchor')).addClass('active');
        });
      }, 100);
    }
  }

  function _dialog_submit(e) {

     //  -------------
     //  GET callpoint
     //  -------------

    if (IsTrace)
        alert('dialog_submit: '+e.currentTarget.id+':'+e.data.location);

    window.location.replace(e.data.location);
  }

  function onCatchError(response) {
    // var json = response.responseJSON,
    //   message = (json && json.error)
    //     ? json.error
    //     : json['text_error'];
    console.log(response);
  }

  function _select_choice() {
    if ($('#sidebar').attr('data-anchor') !== '') {
      $('#' + $('#sidebar').attr('data-anchor')).addClass('active');
    }
  }

  // Привязка событий нажатия пунктов меню

  function _bindHandlers() {
    /***
     *
     *  Handler for start refresh page dialogs (http-methods):
     *    GET       -- dialog submit (changes page location)
     *    AJAX POST -- dialog_start
     *  May be used together with common-db.controller extention, using
     *  'default_submit_mode' action code.
     *  Look at static/js/common.js -> '$onLineFormSubmit' callpoint.
     *
     ***/

    var handler = null;
    if (is_null(default_submit_mode)) {
        default_submit_mode = 3;
    }
    if (default_submit_mode === 1)
        handler = _dialog_submit;
    else
        handler = _dialog_start;

    if (IsTrace)
        alert('_bindHandlers.default_submit_mode: '+default_submit_mode);

    $('#dialog_testing').on('click', {location: '/dialog/choices'}, _dialog_start);
    $('#group_testing').on('click', {location: '/group/choices'}, _dialog_start);
    $('#resource_data').on('click', {location: '/data/resource'}, _dialog_start);
    $('#create_blank').on('click', {location: '/blank/formation_form'}, _dialog_start);
    $('#create_buklet').on('click', {location: '/booklet/formation_booklet'}, _dialog_start);
    $('#handle_blank').on('click', {location: '/recognition/checking_forms'}, _dialog_start);
    $('#get_maps').on('click', {location: '/maps/maps'}, _dialog_start);
    $('#get_stats').on('click', {location: '/statistics/show'}, _dialog_start);
    $('#person_data').on('click', {location: '/person/index'}, _dialog_start);

    if (handler === null)
        return;

    $('#form_data').on('click', {location: '/docs/index'}, handler);
  }


  // Инициализация приложения
  function init() {
    _bindHandlers();
    const queryString = window.location.search;
    console.log('queryString', queryString);
    const urlParams = new URLSearchParams(queryString);
    const choice = urlParams.get('previous_choice');
    if (choice) {
      $('.a-pointer').removeClass('active');
      $('#' + choice).addClass('active');
      $('#' + choice).click();
    }
  }

  // Возвращаем наружу
  return {
    onCatchError: onCatchError,
    init: init
  }
})();

// Запускаем приложение (перенесего в simple-init.html)
//$(document).ready($_init());
