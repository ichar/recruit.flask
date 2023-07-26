'use strict';

//Приложение
var app = (function () {

  function _dialog_start(e) {
    if (e.data.checking) {
      window[e.data.checking];
    }
    $('.a-pointer').removeClass('active');
    $('#' + e.currentTarget.id).addClass('active');
    if (window.proc) {
      clearInterval(window.proc);
    }
    chapter.info(e.data.location).done(function (dataHtml) {

      $('#page-content').off('click.pageNameSpace');
      // if (dataHtml.includes('class="login-block"')) {
      //   $('#page-content').on('click', function() {
      //     window.location.replace('/auth/index');
      //   });
      // };

      $('#page-content').empty().append(dataHtml);
      $('#admin_manager').attr('href', '');
      $('#admin_manager').attr('href', '/manager/admin_panel?previous_active_choise=' + e.currentTarget.id);
      //$('#' + $('#sidebar').attr('data-anchor')).addClass('active');
    });
  }

  // function _dialog_start(e) {
  //   chapter.info(e.data.location).done(function (dataHtml) {
  //     $('#page-content').empty().append(dataHtml);
  //     if (dataHtml.includes('class="login-block"')) {window.location.href = '/auth/index'}
  //     else {$('#page-content').empty().append(dataHtml)}

  //   });
  // }

  // $('#page-content').on('click', function() {
  //   window.location.replace('http://localhost:5000/');
  // });

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
    $('#dialog_testing').on('click', {location: '/dialog/choices', checking: '_checking'}, _dialog_start);
    $('#group_testing').on('click', {location: '/group/choices'}, _dialog_start);
    $('#resource_data').on('click', {location: '/data/resource'}, _dialog_start);
    $('#create_blank').on('click', {location: '/blank/formation_form'}, _dialog_start);
    $('#create_buklet').on('click', {location: '/booklet/formation_booklet'}, _dialog_start);
    $('#handle_blank').on('click', {location: '/recognition/checking_forms'}, _dialog_start);
    $('#get_maps').on('click', {location: '/maps/maps'}, _dialog_start);
    $('#get_stats').on('click', {location: '/statistics/show'}, _dialog_start);
    $('#person_data').on('click', {location: '/person/index'}, _dialog_start);


    //$('#get_listResults').on('click', {location: '/pt/list_results'}, _dialog_start);
  }


  // Инициализация приложения
  function init() {
    _bindHandlers();
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    const choice = urlParams.get('previous_choice');
    $('.a-pointer').removeClass('active');
    $('#' + choice).addClass('active');
    $('#' + choice).click();
  }

  // Возвращаем наружу
  return {
    onCatchError: onCatchError,
    init: init
  }
})();

// Запускаем приложение
$(document).ready(app.init);
