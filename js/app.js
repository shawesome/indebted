$(function() {
    $('.buyer img').click(function() {
        $('.buyer img').removeClass("selected");
        $(this).toggleClass("selected");
        $(this).prev("input").click();
    })

    $('.buyees img').click(function() {
        $(this).toggleClass("selected");
        $(this).prev("input").click();
    })
});
