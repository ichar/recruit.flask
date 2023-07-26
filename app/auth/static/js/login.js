'use strict';

//Приложение
var app = (function () {

  function selected() {
    $('#login-block option:first').attr('disabled','disabled')
    $('#login-block option:first').prop('selected', true);
  }

  function onCatchError(response) {
    // var json = response.responseJSON,
    //   message = (json && json.error)
    //     ? json.error
    //     : json['text_error'];
    console.log('onCatchError response', response);
  }

  function _select_choice() {
    if ($('#sidebar').attr('data-anchor') !== '') {
      $('#' + $('#sidebar').attr('data-anchor')).addClass('active');
    }
  }

  // Привязка событий нажатия пунктов меню

  function _bindHandlers() {
    //selected();
    $('.login-block').on('change', '.form-username', function () {
      var user = $(this).find('option:selected').val();
      console.log('user', user);
      var header = {
        url: '/auth/user_info',
        method: 'post',
        data: {selected: user}
      }
      jsonData.info(header).done(function (data) {
        console.log('data:', data);
        $('.login-sec').empty().append(data['form']);
        //selected();
      });
    })
  }

  // Инициализация приложения
  function init() {
    _bindHandlers();

  }

  // Возвращаем наружу
  return {
    onCatchError: onCatchError,
    init: init
  }
})();

// Запускаем приложение
$(document).ready(app.init);
