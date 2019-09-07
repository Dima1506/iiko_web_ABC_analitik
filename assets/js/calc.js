$(document).ready(function () {

    /*Выставление цен по умолчанию*/
    $("#Other_INFO").html($("#Other").val() + " рублей");
    $("#AC_INFO").html($("#AC").val() + " рублей");
    $("#RC_INFO").html($("#RC").val() + " рублей");
    calculation();

    /*Расчет цен по ползункам*/
    $("#Other").on("input", function () {
        $("#Other_INFO").html($(this).val() + " рублей");
        var xhr = new XMLHttpRequest();

        // 2. Конфигурируем его: GET-запрос на URL 'phones.json'
        xhr.open('GET', 'http://85.143.222.116:8000/update/', false);

        // 3. Отсылаем запрос
        xhr.send();
        calculation();
    });

    $("#AC").on("input", function () {
        $("#AC_INFO").html($(this).val() + " рублей");
        calculation();
    });

    $("#RC").on("input", function () {
        $("#RC_INFO").html($(this).val() + " рублей");
        calculation();
    });

    /*Изменение настроек*/
    $("#UA").on("input",function(){
        calculation();
    });

    $("#C1").on("input",function(){
        calculation();
    });

    $("#AGPrice").on("input",function(){
        calculation();
    });

    $("#AGCount").on("input",function(){
        calculation();
    });

    $("#NetCost").on("input",function(){
        calculation();
    });

    $("#Delivery").on("input",function(){
        calculation();
    });

    $("#APC").on("input",function(){
        calculation();
    });

    function calculation() {
        var UA = parseFloat($("#UA").val());//Число подписчиков чатбота, которые конвертируются в покупателей
        var C1 = parseFloat($("#C1").val());//Конверсия подписчиков чатбота в Покупателей в %
        var buyers = UA * C1;//Количество покупателей, с чатботом
        var AGPrice = parseFloat($("#AGPrice").val());//Средняя цена товара в магазине, который покупается клиентами
        var AGCount = parseFloat($("#AGCount").val());//Среднее число товаров в корзине клиента
        var AVPrice = AGPrice * AGCount;//Средний чек в магазине
        var NetCost = parseFloat($("#NetCost").val());//COGS себестоимость
        var Delivery = parseFloat($("#Delivery").val());//Стоимость доставки
        var Other = parseFloat($("#Other").val());//Стоимость затрат на обеспечение продажи: З/п шкала %% продавцам , повышающая продажи
        var APC = parseFloat($("#APC").val());//Среднее число покупок (в когорте) одним Покупателем, установившем чатбота
        var ARPPU = (AVPrice - (NetCost + Delivery + Other)) * APC;//Доход с одного платящего клиента за время жизни когорты.
        var ARPU = ARPPU * C1;//Доход с одного уникального подписчика чатбота
        var AC = parseFloat($("#AC").val());//Бюджет на привлечение когорты: десерт покупателю + 50 руб за каждую установку - продавцу
        var CPA = AC / UA;//Затраты на привлечение одного подписчика, установившего чатбота
        var RC = parseFloat($("#RC").val());//Бюджет на удержание клиентов: бонусы, персонализация, привилегии
        var ARC = RC * C1 / buyers;//Средние затраты на удержание подписчика чат-бота
        var ARPU_CPA_ARC = ARPU - CPA - ARC;//Прибыль с одного уникального подписчика чатбота
        var Revenue = ARPU_CPA_ARC * UA;//Прибыль,  которую мы получаем в когорте.
        var ROI = (ARPPU * buyers - (AC + RC))/(AC + RC) * 100;//ROI
        $("#CPA").html(CPA.toFixed(2));
        $("#ARC").html(ARC.toFixed(2));
        $("#ARPU_CPA_ARC").html(ARPU_CPA_ARC.toFixed(2));
        $("#Revenue").html(Revenue.toFixed(2));
        $("#ROI").html(ROI.toFixed(2));
    }
});