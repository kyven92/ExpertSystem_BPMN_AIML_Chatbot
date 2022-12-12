// jQuery Document
$(document).ready(function(){

    var synth = window.speechSynthesis;
    var msg = new SpeechSynthesisUtterance();
    var voices = synth.getVoices();

    msg.voice = voices[0];
    msg.rate = 1;
    msg.pitch = 1;

    ask_question = function(question, show_question) {
        var xhttp = new XMLHttpRequest();
        xhttp.onload = function () {
            if (this.status == 200 && this.responseText != null) {
                var response = JSON.parse(this.responseText);
                var vid = document.getElementById("myvid");
                msg.text = response.response.answer;
                if (show_question == true) {
                    $("#chatbox").append ("<p><b>You:</b> "+response.response.question.toUpperCase()+"</p>" );
                }

                saidas = response.response.answer.toUpperCase();
                lista_saidas = saidas.split("-");

                len_lista_saida = lista_saidas.length;
                msg.text = ''
                for (i=0 ; i<len_lista_saida; i++) {
                    saida = lista_saidas[i];
                    if (saida != '.' && saida.trim() != '') {
                        // delay
                        msg.text = msg.text + saida
                        $("#chatbox").append ("<p><b>Ari:</b> "+saida+"</p>" );
                        $("#chatbox")[0].scrollTop = $("#chatbox")[0].scrollHeight;
                    }

                }

               msg.lang = 'pt-BR'

               if (document.getElementById("checkcomavatar").checked) {
                    vid.play();
               }

               if (document.getElementById("checkcomvoz").checked)
                   speechSynthesis.speak(msg);
               }

        }

        xhttp.open("GET", "/api/web/v1.0/ask?question="+question);
        xhttp.setRequestHeader("Content-type", "application/json");
        xhttp.send();

 		return false;
    }

    ask_question("YINITIALQUESTION", false)

    $(".question").click(function() {
        var question = $(this).text()
        return ask_question(question, true)
    });

    $(document).on('click', '.postback', function(){
	    var question = "";
	    var attr = $(this).attr('postback');
        if (typeof attr !== typeof undefined && attr !== false) {
            question = attr
        } else {
            question = $(this).text();
        }
        return ask_question(question, true)
    });

	$("#submitmsg").click(function(){
        var question = $("#usermsg").val();
        $("#usermsg").val("");
        return ask_question(question, true)
	});

});