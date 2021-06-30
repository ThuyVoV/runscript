let searchBox = document.getElementById("upload_filter")

searchBox.addEventListener("keyup", filterUpload)

function filterUpload() {
    let filter, ul, li, a, i, txtValue;
    filter = searchBox.value.toUpperCase();
    ul = document.getElementById("upload_all");
    li = ul.getElementsByTagName("li");
    for (i = 0; i < li.length; i++) {
        a = li[i].getElementsByTagName("a")[0];
        txtValue = a.textContent || a.innerText;
        if (txtValue.toUpperCase().indexOf(filter) > -1) {
            li[i].style.display = "";
        } else {
            li[i].style.display = "none";
        }
    }
}