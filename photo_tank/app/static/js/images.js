/**
 * Created by martin on 19/03/15.
 */


$(document).ready(function() {

    $(".include-keyword").click(function() {

        parent_div = $(this).closest("div");

        badge = parent_div.find("a > span");
        if (badge.is("[include]")) {
            badge.removeAttr("include");
            badge.removeClass("badge-danger");
            badge.removeClass("badge-success");
        } else {
            badge.attr("include",'');
            badge.removeAttr("exclude",'');
            badge.removeClass("badge-danger");
            badge.addClass("badge-success");
        }



        include_menu = parent_div.find("ul > li > a").attr("id");

        if (album_id !== 'None') {
            submit_album()
        }

    });

    $(".exclude-keyword").click(function() {
        parent_div = $(this).closest("div");

        badge = parent_div.find("a > span");
        if (badge.is("[exclude]")) {
            badge.removeAttr("exclude");
            badge.removeClass("badge-danger");
            badge.removeClass("badge-success");
        } else {
            badge.attr("exclude",'');
            badge.removeAttr("include",'');
            badge.addClass("badge-danger");
            badge.removeClass("badge-success");
        }

        include_menu = parent_div.find("ul > li > a").attr("id");

        if (album_id !== 'None') {
            submit_album()
        }

    });

    $(".photo-tick").click(function() {

        selected_images = get_selected_images();

        group = $(this).parent();

        untick = group.children(".fa-circle-o");
        tick = group.children(".fa-check-circle-o");
        img = group.children("img");
        id = img.attr("id");

        untick.toggle();
        tick.toggle();

        var index = selected_images.indexOf(id);
        if (index > -1) {
            selected_images.splice(index, 1);
        } else {
            selected_images.push(id)
        }

        sessionStorage["selected_images"] = JSON.stringify(selected_images);
        show_selected()
    });

    $('#selected').click( function() {
        submit_album(true); return false;
    });

    $("#save_album_name").click(function() {
        if (album_id !== 'None') {
            submit_album()
        }
    });

    function get_included_keywords() {
        outer_div = $("#accordion");

        var included = [];
        outer_div.find('[include]').each(function(i) {
            included.push( $(this).attr("id") );
        });

        return included;
    }

    function get_excluded_keywords() {
        outer_div = $(".bs-example");

        var excluded = [];
        outer_div.find('[exclude]').each(function(i) {
            excluded.push( $(this).attr("id") );
        });

        return excluded;
    }

    function get_selected_images() {
        if (sessionStorage["selected_images"] === "") {
            selected_images = []
        } else {
            selected_images = JSON.parse(sessionStorage["selected_images"])
        }
        return selected_images

    }

    function update_ticks() {

        selected_images = get_selected_images();

        for (var i = 0; i < selected_images.length; i++) {
            id = selected_images[i];
            console.log(id);
            img = $(document.getElementById(id));

            if (img.length > 0) {
                group = img.parent();

                untick = group.children(".fa-circle-o");
                tick = group.children(".fa-check-circle-o");

                untick.toggle();
                tick.toggle()
            }
        }
    }

    function show_selected() {

        selected_images = get_selected_images();
        element = $(document.getElementById("selected"));
        if (selected_images.length >    0) {
            element.show();
            element.text(selected_images.length)
        } else {
            element.hide()

        }
    }

    function submit_album(selected_only) {

        if (selected_only === true) {
            post_data = {
                'name': $("#album_name").val(),
                'included': [],
                'excluded': [],
                'selected': get_selected_images(),
                    'selected_only': true
            };
        } else {
            post_data = {
                'name': $("#album_name").val(),
                'included': get_included_keywords(),
                'excluded': get_excluded_keywords(),
                'selected': get_selected_images(),
                'selected_only': false
            };
        }
        var request = $.ajax({
            type: 'POST',
            contentType: 'application/json',
            url: "/album/save/" + album_id,
            data: JSON.stringify(post_data),
            dataType: 'json'

        })
            .done(function( html ) {
                window.location = "/image/album/" + album_id
            })
    }


    update_ticks();
    show_selected();

    album_id = sessionStorage["album_id"]
});
