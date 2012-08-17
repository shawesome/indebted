$(function() {
    /* Sync up the checked values and the images */
    $('input[type=radio]:checked, input[type=checkbox]:checked').each(function() {
        $(this).next('img').addClass("selected");
    });

    /* Click handlers */
    $('.buyer img').click(function() {
        $('.buyer img').removeClass("selected");
        $(this).toggleClass("selected");
        $(this).prev("input").click();
    });

    $('.buyees img').click(function() {
        $(this).toggleClass("selected");
        $(this).prev("input").click();
    });
});
