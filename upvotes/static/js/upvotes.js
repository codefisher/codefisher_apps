   $(".votes").click(function (event) {
       event.preventDefault();
       var form = $(this);
       var address_value = form.attr("action");
       var data = form.serialize() + "&type=ajax";
       $.ajax({
            url: address_value,
            type: "POST",
            data: data,
            dataType: "html",
            success: function(msg){
                if(/^[0-9]+$/.test(msg)) {
                    form.find(".vote").html(msg);
                } else {
                    form.tooltip({ 
                        items: form, 
                        content: msg,
                        close: function( event, ui ) { form.tooltip( "destroy" ); }
                        }).tooltip( "open" );
                }
            },
            error: function(jqXHR, textStatus, errorThrown){
                   form.tooltip({ 
                        items: form, 
                        content: "The icon request could not be up voted.",
                        close: function( event, ui ) { form.tooltip( "destroy" ); }
                        }).tooltip( "open" );
            }
       });
       return true;
    });