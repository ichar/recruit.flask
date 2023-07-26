'use strict';

var chapter = (function () {

  // Запрос ресурсов
  // Возвращаем объект - html: текст html
  function getСhapter(url, args) {
    return $.ajax({
      type: "POST",
      dataType: 'html',
      data: args,
      url: url,
    }).done(function (data) {
      return data['data']
    }).fail(function (data) {
      return data['text_error']
    });
  }

  // Возврат
  return {
    info: getСhapter
  }
})();
