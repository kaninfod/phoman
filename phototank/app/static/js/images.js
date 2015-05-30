/**
 * Created by martin on 19/03/15.
 */


$(document).ready(function() {

    $('#right-panel-link').click({
        side: 'right',
        clickClose: false,
        duration: 600,
        easingOpen: 'easeInBack',
        easingClose: 'easeOutBack'
        });

    $('#close-panel-bt').click(function() {
      $.panelslider.close();
    });


    //Initiate the autocomplete element
    $( "#keywordInput" ).autocomplete({
        source: "/keywords",
        minLength: 2,
        select: function( event, ui ) {
            action = $("#keywordAction").attr("keyword-action")
            addKeyword(ui.item.id, ui.item.value, action)

            //reload page when new keyword is added
            submit_album()

            //clear autocomplete input
            $(this).val('');
            return false;
          }
    });

    //when page reloads, all keywords in album should get added to keyword box
    $.each( keywords_in_album, function( key, obj ) {
        addKeyword(obj.id, obj.value, obj.action)
    });

    //Adds a keyword to UI
    function addKeyword(id, value, action) {
        div = $("#keywordsInAlbum")
        var newSpan = $("<span></span>").appendTo(div);
        newSpan.attr("id",id)
        newSpan.addClass("label")
        newSpan.addClass(getClass(action))
        newSpan.html(value)
        newSpan.append("<a></a>")
        newSpan.children("a").append("<i></i>")
        newSpan.children("a").children("i").addClass("fa fa-minus-circle")
        return newSpan

    }

    function getClass(action) {
        if (action==1) {
            return "label-success"
        } else {
            return "label-danger"
        }
    }

    $(document).on ("click", "#keywordsInAlbum > span > a > i", function (event) {
        event.target.parentElement.parentElement.remove()
        submit_album()
    });

    //Gets all keywords added in ui, puts them in list for backend to process
    function get_keywords() {
        outer_div = $("#keywordsInAlbum");

        var included = [];
        outer_div.find('.label-success').each(function(i) {
            included.push( { 'id': $(this).attr("id"), 'action': 1 } );
        });
        var excluded = [];
        outer_div.find('.label-danger').each(function(i) {
            excluded.push({ 'id': $(this).attr("id"), 'action': 2 } );
        });
        var keywords = included.concat(excluded)
        return keywords;
    }


    $('.input-group-btn > ul > li').click(function(event){
        state = event.target.getAttribute("btn-text")

        if (state=="Include") {
            $("#keywordAction").attr("keyword-action", "1")
            $("#keywordAction").addClass("btn-success")
            $("#keywordAction").removeClass("btn-danger")
        } else {
            $("#keywordAction").attr("keyword-action", "2")
            $("#keywordAction").removeClass("btn-success")
            $("#keywordAction").addClass("btn-danger")
        }

    })


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
                'selected': get_selected_images(),
                    'selected_only': true
            };
        } else {
            post_data = {
                'name': $("#album_name").val(),
                'keywords': get_keywords(),
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
    panel = $(".panel-heading").children("a").attr("id")
    album_id = sessionStorage["album_id"]
});
