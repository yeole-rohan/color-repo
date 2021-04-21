var $ = jQuery.noConflict();

$(document).ready(function(){
    $('#id_design_description').attr('rows', '4')
    $("#upload-submit").attr("disabled", "true")
    $( "#id_design_image" ).change(function() {
        $("#upload-submit").removeAttr("disabled")
      });
    $('.razorpay-payment-button').addClass('checkout')
    $('#id_address').attr('rows', '4')
    $('#id_design_desc').attr('rows', '4')
    // $('#id_design_image').change(function(){
    //     $("#upload-submit").attr("disabled", "false")
    // })
    // $('#paths').on("click", function() {
    //     if($(this).hasClass('paths')){
    //         $('#path').css({ fill: "#0000003b" });
    //         $(this).removeClass('paths')
    //     }else{
    //         console.log($('.wish').attr('data-id'))
    //         $.ajax({
    //             url:$('.wish').attr('data-href'),
    //             data:{
    //                 'data_id': $('.wish').attr('data-id'),
    //                 'csrfmiddlewaretoken' : $('input[name="csrfmiddlewaretoken"]').val(),
    //             },
    //             type:'POST',
    //             dataType: 'json',
    //             success: function (res, status) {
    //                 if (res['status'] == 'ok') {
    //                     $(this).addClass('paths')
    //                     $('#path').css({ fill: "#EF465A" });
    //                 }
    //             },
    //             error: function (res) {
    //                 console.log(res.status);
    //             }
    //         })
            
    //     }
    // });
    // $('.add-cart').on('click', function(params){
    //     params.preventDefault();
    //     console.log($(this).attr('href'));
    //     $.ajax({
    //         url:$(this).attr('href'),
    //         data:{
    //             'data_id': $(this).attr('data-id'),
    //             'csrfmiddlewaretoken' : $('input[name="csrfmiddlewaretoken"]').val(),
    //         },
    //         type:'POST',
    //         dataType: 'json',
    //         beforeSend: function() {
    //             document.querySelector('.add-cart').textContent = 'Adding to Cart';
    //         },
    //         success: function (res, status) {
    //             if (res['status'] == 'ok') {
    //                 window.location.replace("/view-cart/");
    //             }
    //         },
    //         error: function (res) {
    //             console.log(res.status);
    //         }
    //     })
    $('.prod_color').on('click', function () {

      var index = $(this).index();
      var color = document.querySelectorAll('.prod_color');
      var color_style = color[index - 1].style.backgroundColor
      console.log("color_style", color_style);

      $('#prod_color_id').val(color_style);
    });
    
    $('.prod_size').on('click', function () {

      var index = $(this).index();
      var prod_size = document.querySelectorAll('.prod_size');
      var prod_value = prod_size[index - 1].innerText
      console.log("prod_value", prod_value);

      $('#prod_size_id').val(prod_value);
    });
 });