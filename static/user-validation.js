async function validateUser(url, user_input) {
   
    var username = user_input.value;
    var xhr = new XMLHttpRequest();
    var valid_user = false;

    xhr.open('POST', url, true);
    xhr.setRequestHeader('Content-Type', 'application/json');

    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4) {
            if (xhr.status == 200) {
                var result = JSON.parse(xhr.responseText);
                var start_use = document.getElementById("start_use");
                var hint = document.getElementById("hint");

                if(result.taken == "Benutzername ist frei"){
                    user_input.style.borderColor = "#6C955E";
                    start_use.disabled = false;
                    hint.innerHTML = result.taken;
                    hint.style.color = "#6C955E";
                }else if(result.taken == "Benutzername bereits vergeben"){
                    user_input.style.borderColor = "rgb(220 38 38)";
                    start_use.disabled = true;
                    hint.style.color = "rgb(220 38 38)";
                    hint.innerHTML = result.taken;
                }else if(result.taken == "Benutzername muss min. 2 Zeichen haben"){
                    user_input.style.borderColor = "rgb(220 38 38)";
                    start_use.disabled = true;
                    hint.style.color = "rgb(220 38 38)";
                    hint.innerHTML = result.taken;
                }
            } else {
                console.error('Error during XMLHttpRequest. Status:', xhr.status);
            }
        }
    };
    var data = JSON.stringify({ username: username });
    xhr.send(data);
}