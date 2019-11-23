$(document).ready(function () {

    /*Выставление цен по умолчанию*/
    $("#Other_INFO").html($("#Other").val() + " рублей");
    $("#AC_INFO").html($("#AC").val() + " рублей");
    $("#RC_INFO").html($("#RC").val() + " рублей");
    //var a = 5;
    calcukate()
    

    /*Расчет цен по ползункам*/
    
    $("#Other").on("input", function () {
        $("#Other_INFO").html($(this).val() + " рублей");
    });

    $("#AC").on("input", function () {
        $("#AC_INFO").html($(this).val() + " рублей");
        
    });

    $("#RC").on("input", function () {
        $("#RC_INFO").html($(this).val() + " рублей");
    });
    
    function calcukate() {
      var xhr = new XMLHttpRequest();
      var Other2 = parseFloat($("#Other").val());
      var AC2 = parseFloat($("#AC").val());//Бюджет на привлечение когорты: десерт покупателю + 50 руб за каждую установку - продавцу
      var RC2 = parseFloat($("#RC").val());
        // 2. Конфигурируем его: GET-запрос на URL 'phones.json'
      
      var body = 'id='+state+'&Other=' + Other2 +  '&AC=' + AC2+ '&RC=' + RC2
        // 3. Отсылаем запрос
      xhr.open('GET', '/update/'+body, false);
      xhr.send();
      console.log(xhr.status);
      cpa = parseFloat(xhr.responseText.split(",")[0].split("[")[1]);
      arc = parseFloat(xhr.responseText.split(",")[1]);
      arpu_cpa_arc = parseFloat(xhr.responseText.split(",")[2]);
      revenue = parseFloat(xhr.responseText.split(",")[3]);
      roi = parseFloat(xhr.responseText.split(",")[4].split("]")[0]);
      console.log(xhr.responseText);
      console.log(cpa);
      
  
      $("#CPA").html(cpa.toFixed(2));
      $("#ARC").html(arc.toFixed(2));
      $("#ARPU_CPA_ARC").html(arpu_cpa_arc.toFixed(2));
      $("#Revenue").html(revenue.toFixed(2));
      $("#ROI").html(roi.toFixed(2));
      
    }

    
    addEventListener("mouseup", calcukate);
    addEventListener('touchend', calcukate,false);

    

});