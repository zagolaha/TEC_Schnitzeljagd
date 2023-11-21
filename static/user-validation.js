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
                if(result.taken == "Benutzername is frei"){
                    user_input.style.borderColor = "green";
                    document.getElementById("start_use").disabled = false;
                    document.getElementById("hint").innerHTML = result.taken;
                    document.getElementById("hint").style.color = "green";
                    
                }else if(result.taken == "Benutzername bereits vergeben"){
                    user_input.style.borderColor = "red";
                    document.getElementById("start_use").disabled = true;
                    document.getElementById("hint").style.color = "red";
                    document.getElementById("hint").innerHTML = result.taken;
                }else{
                    user_input.style.borderColor = "red";
                    document.getElementById("start_use").disabled = true;
                    document.getElementById("hint").style.color = "red";
                    document.getElementById("hint").innerHTML = result.taken;
                }
            } else {
                console.error('Error during XMLHttpRequest. Status:', xhr.status);
            }
        }
    };
    var data = JSON.stringify({ username: username });
    xhr.send(data);
}