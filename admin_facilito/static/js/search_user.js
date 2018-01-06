$(document).ready(function(){

    //alert("Hola Mundo -> Enero 2018")

    $("#search-user-form").submit(function(e){
    e.preventDefault();

    $.ajax({
      url: $(this).attr('action'),
      type: $(this).attr('method'),
      data : $(this).serialize(),

      success: function(json){ //json es la respuesta del servidor

        console.log(json)

        var html = "";
        var link = window.location.pathname + "add/"

        for(let elem of json){
          var href = link + elem.username + "/"
          html+= '<li>' + elem.username + '<a href="'+ href +'"> -> Agregar</a> </li>'
          console.log(html)
        }

        $('#ajax-result ul').empty();
        $('#ajax-result ul').append(html);

      }

    })

  });


})