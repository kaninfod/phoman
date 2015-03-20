/**
 * Created by martin on 19/03/15.
 */




$(document).ready(function() {

    $("#save_album_name").click(function() {
        if (album_id !== 'None') {

            submit_query()
        }
    })



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
            submit_query()
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
            submit_query()
        }

    });

    function submit_query() {

        outer_div = $(".bs-example");

        var excluded = [];
        outer_div.find('[exclude]').each(function(i) {
            excluded.push( $(this).attr("id") );
        });

        var included = [];
        outer_div.find('[include]').each(function(i) {
            included.push( $(this).attr("id") );
        });

        post_data = {'name': $("#album_name").val(),'included':included, 'excluded':excluded};


        function url() {
            if (album_id !== 'None') {
                return "/album/save/" + album_id
            } else {
                return "/album/new"
            }
        }


        var request = $.ajax({
            type: 'POST',
            contentType: 'application/json',
            url: url(),
            data: JSON.stringify(post_data),
            dataType: 'json'

        })
            .done(function( html ) {
                window.location = "/image/album/" + album_id
            })
    }

})
