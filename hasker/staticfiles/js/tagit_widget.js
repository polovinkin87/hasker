$(document).ready(function() {
    $(".tagit").tagit({
        allowSpaces: true,
        autocomplete: {delay: 0,
                       minLength: 2,
                       source: "/tag_autocomplete/"
        },
        tagLimit: 3
    });
});