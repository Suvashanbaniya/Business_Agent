const chatBox = document.getElementById("chat-box");

function addMessage(text, sender){

    const div = document.createElement("div");

    div.className = sender;

    div.innerText = text;

    chatBox.appendChild(div);

    chatBox.scrollTop = chatBox.scrollHeight;

}

async function sendMessage(){

    const input = document.getElementById("message");

    const text = input.value.trim();

    if(text==="") return;

    addMessage(text,"user");

    input.value="";

    try{

        const response = await fetch("/chat",{

            method:"POST",

            headers:{
                "Content-Type":"application/json"
            },

            body:JSON.stringify({
                message:text
            })

        });

        const data = await response.json();

        addMessage(data.response,"bot");

    }

    catch(error){

        addMessage("Cannot connect to Flask.","bot");

        console.log(error);

    }

}

function handleKey(event){

    if(event.key==="Enter"){

        sendMessage();

    }

}