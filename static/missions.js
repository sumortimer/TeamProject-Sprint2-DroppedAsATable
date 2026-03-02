const currentPage = document.title;
const missions = document.getElementsByClassName("mission");
const pins = document.getElementsByClassName("pin");
const trophys = document.getElementsByClassName("trophy");
const editButtons = document.getElementsByClassName("editbutton");
const missionText = document.getElementsByClassName("missiontext");
const userClass = "trusted";
var tier;
var pinTier;
var selected;

//This decides which missions screen we are currently on and assigns relevent variables
if (currentPage === "Missions Tier 1"){
    selected = document.getElementById("tier1");
    pinTier = "pinValuesTier1";
    tier = "tier1";
    setTrophyColors("rgb(147, 111, 13)");
}
else if (currentPage === "Missions Tier 2"){
    selected = document.getElementById("tier2");
    pinTier = "pinValuesTier2";
    tier = "tier2";
    setTrophyColors("rgb(184, 182, 178)")
}
else{
    selected = document.getElementById("tier3");
    pinTier = "pinValuesTier3";
    tier = "tier3";
    setTrophyColors("rgb(203, 157, 30)")
}

//This sets the background color for the trophy icons
function setTrophyColors(color){
    Array.from(trophys).forEach(trophy => {
        trophy.style.backgroundColor = color;
    })
}

//This adds a highlight effect to the the button of the current tier
selected.style.backgroundColor = "rgb(187, 218, 248)";
selected.style.border = "3px solid black";

// selected.addEventListener("mouseenter", (e) => {
//     selected.style.backgroundColor = "red";
// });

// selected.addEventListener("mouseleave", (e) => {
//     selected.style.backgroundColor = "blue";
// });

//This array stores the visibility value of the pin in each mission
var pinValues = getPinValues(pinTier);
setPinValues();

//This returns the relevent array of pin visibility values from the websites local storage
function getPinValues(key){
    const values = localStorage.getItem(key) || JSON.stringify(["hidden", "hidden", "hidden", "hidden", "hidden", "hidden"]);
    return JSON.parse(values);
}

//This saves the pin visibility values to local storage
function savePinValues(key){
    const values = JSON.stringify(pinValues);
    localStorage.setItem(key, values);
}

//This sets the actual visibility for each pin, according the the pinValues array
function setPinValues(){
    Array.from(pins).forEach( (pin, i) => {
        pin.style.visibility = pinValues[i];
    })
}

//This adds an event listener to each mission element for when the mission is clicked
Array.from(missionText).forEach((mission, i) => {
    mission.addEventListener("click", (e) => {
        //This swaps the value of the pin's visiblity
        if (pinValues[i] === "visible"){
            pinValues[i] = "hidden";
        }
        else{
            pinValues[i] = "visible";
        }
        setPinValues();
        savePinValues(pinTier);

        let id = i + 1;

        window.location.href = "/mission_display?id=" + id;
    });
});

if (userClass === "trusted"){
    Array.from(editButtons).forEach(button => {
        button.style.visibility = "visible";
    });
}
else{
    Array.from(editButtons).forEach(button => {
        button.style.visibility = "hidden";
    });
}
