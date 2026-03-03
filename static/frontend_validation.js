const username_input = document.getElementById("username_input");
const email_input = document.getElementById("email_input");
const password_input = document.getElementById("password_input");
const confirm_password_input = document.getElementById("confirm_password_input");
const error_message = document.getElementById("error_message");
const form = document.querySelector("#form");

var inputs = [];

form.addEventListener('submit', (e) => {


    let errors = [];

    if (email_input){
        //Sign Up page
        errors = signUpErrors(username_input.value, email_input.value, password_input.value, confirm_password_input.value);
        inputs = [username_input, email_input, password_input, confirm_password_input];
    }
    else{
        //Log in page
        errors = logInErrors(username_input.value, password_input.value);
        inputs = [username_input, password_input];
    }

    if (errors.length > 0){
        error_message.innerText = errors.join(". ")
    }
})

// async function sendData(){
//     const data = {
//         username: username_input.value,
//         password: password_input.value
//     }

//         try{
//             const response = await fetch(window.location.href, {
//                 method: "POST",
//                 headers: {
//                     'Accept': 'application/json',
//                     'Content-Type': 'application/json'
//                 },
//                 body: JSON.stringify(data),
//             });

//             // let clone = response.clone()

//             // try {
//             //     const content = await response.json();
//             //     console.log(content);
//             //     error_message.innerText = response.error;
//             // } catch {
//             //     const content = await clone.text();
//             //     window.location.href = content;
//             // }

//             const content = await response.text();
//             if (content[0] == "/") {
//                 window.location.href = content;
//             } else {
//                 console.log(content);
//                 error_message.innerText = content;
//             }

//         }
//         catch (e){
//             console.log(e);
//         }
// }

function signUpErrors(username, email, password, confirm_password){

    let errors = [];

    if (username === "" || username === null){
        errors.push("Username is missing");
        username_input.parentElement.classList.add('incorrect')
    }
    if (email === "" || email === null){
        errors.push("Email is missing");
        email_input.parentElement.classList.add('incorrect')
    }
    if (password === "" || password === null){
        errors.push("Password is missing");
        password_input.parentElement.classList.add('incorrect')
    }
    if (confirm_password === "" || confirm_password === null){
        errors.push("Please confirm password");
        confirm_password_input.parentElement.classList.add('incorrect')
    }
    if (password !== confirm_password){
        errors.push("Passwords do not match");
        confirm_password_input.parentElement.classList.add('incorrect')
    }

    return errors;
}

// function logInErrors(username, password){

//     let errors = [];

//     if (username === "" || username === null){
//         errors.push("Username is missing");
//         username_input.parentElement.classList.add('incorrect')
//     }
//     if (password === "" || password === null){
//         errors.push("Password is missing");
//         password_input.parentElement.classList.add('incorrect')
//     }

//     return errors;
// }



inputs.forEach(input => {
    input.addEventListener( "input", (e) => {
        if (input.parentElement.classList.contains("incorrect")){
            input.parentElement.classList.remove("incorrect")
        }
    })
})
