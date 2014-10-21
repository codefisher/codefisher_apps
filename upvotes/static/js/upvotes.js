   $(".vote-link").click(function (event) {
       event.preventDefault();
       var anchor = $(this);
       var address_value = anchor.attr("href");
       $.ajax({
            url: address_value + "ajax/",
            type: "GET",
            dataType: "html",
            success: function(msg){
                if(/^[0-9]$/.test(msg)) {
                    anchor.children(".vote").html(msg);
                } else {
                    anchor.tooltip({ 
                        items: anchor, 
                        content: msg,
                        close: function( event, ui ) { anchor.tooltip( "destroy" ); }
                        }).tooltip( "open" );
                }
            },
            error: function(jqXHR, textStatus, errorThrown){
                   anchor.tooltip({ 
                        items: anchor, 
                        content: "The icon request could not be up voted.",
                        close: function( event, ui ) { anchor.tooltip( "destroy" ); }
                        }).tooltip( "open" );
            }
       });
       return true;
    });