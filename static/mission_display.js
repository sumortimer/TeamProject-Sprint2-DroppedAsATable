const redButton = document.getElementById("redbutton");
const blueButton = document.getElementById("bluebutton");
const greenButton = document.getElementById("greenbutton");
const error = document.getElementById("errormessage");

redButton.addEventListener("click", (e) => {
    const value = redButton.name;
    if(value == "Correct"){
        alert("Correct");
        window.location.href = "/missions_t1";
    }else{
        error.innerText = "Incorrect"
    }
    
})

blueButton.addEventListener("click", (e) => {
    const value = blueButton.name;
    if(value == "Correct"){
        alert("Correct");
        window.location.href = "/missions_t1";
    }else{
        error.innerText = "Incorrect"
    }
})

greenButton.addEventListener("click", (e) => {
    const value = greenButton.name;
    if(value == "Correct"){
        alert("Correct");
        window.location.href = "/missions_t1";
    }else{
        error.innerText = "Incorrect"
    }
})

