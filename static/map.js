const nodeRoute = document.getElementById("nodeRoute");
const locationRoute = document.getElementById("locationRoute");
const nodeReload = document.getElementById("nodeReload");
const locationReload = document.getElementById("locationReload");

nodeRoute.style.visibility = "visible";
locationRoute.style.visibility = "hidden";

nodeReload.addEventListener("click", (e) => {
    locationRoute.style.visibility = "visible";
    nodeRoute.style.visibility = "hidden";
});

locationReload.addEventListener("click", (e) => {
    nodeRoute.style.visibility = "visible";
    locationRoute.style.visibility = "hidden";
});