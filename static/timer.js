window.onload = function () {
    // Check if timer already started
    if (typeof localStorage.getItem("start_timer") == 'undefined' || localStorage.getItem("start_timer") == null) {
        localStorage.setItem("start_timer", "0");
    } else if (localStorage.getItem("start_timer") == "1") {
        // Timer already started, load min and sec
        var interval = setInterval(function () {

            var max_time = parseInt(localStorage.getItem("max_time"));
            var start_time = parseInt(localStorage.getItem("start_time"));
            var current_time = Math.floor(Date.now() / 1000);
            var time_diff = current_time - start_time;

            // check if timer finished
            if (time_diff >= max_time) {
                goEnd();
                clearInterval(interval);
                localStorage.setItem("start_timer", "0");
            } else {
                // display current time
                var display = document.getElementById("time");
                if (display !== null) {
                    
                    var min = Math.floor(time_diff / 60);
                    var sec = Math.floor(time_diff % 60);

                    if(min < 10){
                        min = "0" + min.toString();
                    }

                    if(sec < 10){
                        sec = "0" + sec.toString();
                    }
                    display.innerHTML = min + ":" + sec;
                }
            }

        }, 500);

    }
}