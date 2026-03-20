const nodeRoute = document.getElementById("nodeRoute");
const locationRoute = document.getElementById("locationRoute");
const nodeReload = document.getElementById("nodeReload");
const locationReload = document.getElementById("locationReload");

const seeLess = document.getElementById("seeLess");
const seeMore = document.getElementById("seeMore");
const plus = document.getElementById("plus");
const minus = document.getElementById("minus");

nodeRoute.style.visibility = "visible";
locationRoute.style.visibility = "hidden";

// seeLess.style.visibility = "hidden";
// seeMore.style.visibility = "hidden";
seeMore.style.display = "none";
seeLess.style.display = "none";

nodeReload.addEventListener("click", (e) => {
    locationRoute.style.visibility = "visible";
    nodeRoute.style.visibility = "hidden";
});

locationReload.addEventListener("click", (e) => {
    nodeRoute.style.visibility = "visible";
    locationRoute.style.visibility = "hidden";
});

plus.addEventListener("click", (e) => {
    // seeMore.style.visibility = "hidden";
    // seeLess.style.visibility = "visible";
    seeMore.style.display = "none";
    seeLess.style.display = "block";
});

minus.addEventListener("click", (e) => {
    // seeMore.style.visibility = "visible";
    // seeLess.style.visibility = "hidden";
    seeMore.style.display = "block";
    seeLess.style.display = "none";
});