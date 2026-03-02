const form = document.getElementById("missioncontent")
const update = document.getElementById("updatebutton")
const description = document.getElementById("question")

// getData()

update.addEventListener("click", async (e) => {
    e.preventDefault();

    const urlParams = new URLSearchParams(window.location.search);
    const id = urlParams.get("id");

    const data = {"id":id, "question":description.value};

    try{
        const response = await fetch (window.location.href, {
            method: "POST",
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data),
        })

        const content = await response.text()
        window.location.href = content;
    }
    catch (error){
        console.log(error)
    }
})

// async function getData(){
//     const response = await fetch(window.location.href)
//     const data = await response.text()
//     console.log("Data: " + data)

//     description.value = data["question"]
// }
