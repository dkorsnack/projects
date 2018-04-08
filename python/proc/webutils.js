
function reload() {
    var now = new Date();
    var url = "/internal/?t=" + now.getTime(); //kills browser cache
    if (window.XMLHttpRequest) {
        req = new XMLHttpRequest();
    } else if (window.ActiveXObject) {
        req = new ActiveXObject("Microsoft.XMLHTTP");
    }
    if (req != undefined) {
        req.onreadystatechange = function() {reloaddone(url, "internal");};
        req.open("GET", url, true);
        req.send("");
    }
}
function reloaddone(url, target) {
    if (req.readyState == 4) { // only if req is "loaded"
        if (req.status == 200) { // only if "OK"
            document.getElementById("internal").innerHTML = req.responseText;
        }
    }
}
function postdata(s) {
    var params = s + ".x=1";
    if (window.XMLHttpRequest) {
        req = new XMLHttpRequest();
    } else if (window.ActiveXObject) {
        req = new ActiveXObject("Microsoft.XMLHTTP");
    }
    if (req != undefined) {
        req.open("POST", "/", true);
        req.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
        req.setRequestHeader("Content-length", params.length);
        req.setRequestHeader("Connection", "close");
        req.send(params);
    }
    reload();
}
function init(n) {
    reload();
    setInterval(reload, n);
}

