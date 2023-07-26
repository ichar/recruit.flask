//Отображение ошибок

'use strict'

var modal_w = {};
var drop_shadow;

//Возвращение модальных окон из под drop-shadow
//$(document).on('hide.bs.modal', '#errors_docs', function (e) {

  // $('#errors_docs').on('hidden.bs.modal', function () {
  //   alert(1);
  //   for (const [modal, zIndex] of Object.entries(modal_w)) {
  //     $('#' + modal).css('z-index', zIndex);
  //   }
  // });

$(document).on('click', '#modal_errors_button_cancel', function() {
  for (const [modal, zIndex] of Object.entries(modal_w)) {
      $('#' + modal).css('z-index', zIndex);
    }
})

//отображение модального окна ошибки
//str: banner - Заголовок окна
//object: error_text - Объект ошибок
//            (error_text['error_human_text']: читаемый текст, error_text['error_text']: полный текст ошибки)
//array: modals_to_close - массив dom- объектов модальных окон,
//            которые необходимо скрыть за drop-shadow при отображении окна ошибки

function show_error(banner, error_text, modals_to_close) {
  drop_shadow = $('.modal-backdrop').css('z-index');

  if (Array.isArray(modals_to_close)) {
    console.log('show_error', $('#errors_docs'));
    modals_to_close.forEach(modal_window => {
        if (modal_window.hasClass('modal')) {
          if (modal_window.css('z-index') > drop_shadow) {
            modal_w[modal_window.attr('id')] = modal_window.css('z-index');
            modal_window.css('z-index', drop_shadow - 1);
          }
        }
      }
    );
  }
  $('#errors_docs_banner').text(banner);
  $('#error-human').text(error_text['error_human_text']);
  $('#error-div').text(error_text['error_text']);
  $('#errors_docs').modal('show');
}

$('#btn-errorText-toggle').click(function () {
      $('#error-div').slideToggle('slow');
      $('#down, #up').toggle();
});

//Изменение стиля бордюра для данных формы с атрибутом required

function show_errors_form(class_selector) {
  var count_error = 0;
  $('.' + class_selector).each(function (index) {
    if (($(this).val() == '') && ($(this).prop('required'))) {
      count_error++;
      $(this).attr('placeholder', 'Обязательное поле');
      $(this).css('border', '1px solid red');
    } else {
      $(this).css('border', '1px solid #ced4da');
    }
  });
  return count_error
}
