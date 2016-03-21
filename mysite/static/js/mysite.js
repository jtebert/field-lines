function animate_articles() {
    var articles = $(".articles-container").children();
    articles.each(function (i) {
        $(this).delay(i * 200).animate(
            {'top': 0, opacity: 1},
            {queue: true, duration: 500}
        );
        if (i + 1 == articles.length) {
            $('.pagination').delay(i * 200).animate(
                {'margin-top': 0, opacity: 1},
                {queue: true, duration: 500}
            );
        }
    });
}

$(document).ready(animate_articles());

$(".articles-container").bind("DOMSubtreeModified", function () {
    console.log('change');
    animate_articles();
});

// Expand/collapse information boxes
$('body').on('click.collapse-next.data-api', '[data-toggle=collapse-next]', function() {
    var $target = $(this).parent().next();
    if ($target.data('bs.collapse')) {
        $target.collapse('toggle')
    } else {
        $target.collapse()
    }
});
$(".extra-info-header").click(function(){
    $($(this).children()[0]).toggleClass("down");
});