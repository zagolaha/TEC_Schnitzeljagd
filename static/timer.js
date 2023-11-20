window.onload = function () {
    // Check if timer already started
    if (typeof localStorage.getItem("start_timer") == 'undefined' || localStorage.getItem("start_timer") == null) {
        localStorage.setItem("start_timer", "0");
        localStorage.setItem("min", "00");
        localStorage.setItem("sec", "00");
    } else if (localStorage.getItem("start_timer") == "1") {
        // Timer already started, load min and sec
        var interval = setInterval(function () {

            var min = localStorage.getItem("min");
            var sec = localStorage.getItem("sec");

            // check if timer finished
            if (min == localStorage.getItem("max_min") && sec == localStorage.getItem("max_sec")) {
                goEnd();
                clearInterval(interval);
                localStorage.setItem("start_timer", "0");
            } else {
                // display current time
                var display = document.getElementById("time");
                if (display !== null) {
                    time = min + ":" + sec;
                    display.innerHTML = time;
                }

                if (sec == 59) {
                    min++;
                    sec = "00";
                    if (min < 10) {
                        min = "0" + min;
                    }
                } else {
                    sec++;
                    if (sec < 10) {
                        sec = "0" + sec;
                    }
                }
                // update time
                localStorage.setItem("min", min);
                localStorage.setItem("sec", sec);
            }

        }, 1000);

    } else if (localStorage.getItem("start_timer") == "0") {
        localStorage.setItem("min", "00");
        localStorage.setItem("sec", "00");
    }
}