'use strict';

var jsonData = (function () {

  // Запрос ресурсов
  // Возвращаем объект - html: текст html
  function getJSON(header) {
    return $.ajax(
      header
    ).done(function (data) {
      return data
    }).fail(function (data) {
      return data
    });
  }

  // Возврат
  return {
    info: getJSON
  }
})();
