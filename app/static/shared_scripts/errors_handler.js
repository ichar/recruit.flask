'use strict';

var err_show = (function () {

  // Отображение ошибки в модальном окне
  function getModalError(err_text) {
    // $('#errors_modal').on('shown.bs.modal', function () {
    //   $('#errors_banner').text('Ошибка запроса');
    //   $('#error-area').text(err_text);
    // }).modal('show');
    console.log('err_text', err_text);
  }

  // Возврат
  return {
    info: getModalError
  }
})();
