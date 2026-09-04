var fileInput = document.getElementById("policy-file");

var fileName = document.getElementById("file-name");

var deleteFileButton = document.getElementById("delete-file-button");

var userInput = document.getElementById("user-input");

var sendButton = document.getElementById("send-button");

var chatBox = document.getElementById("chat-box");


// =====================================================
// ARCHIVO SELECCIONADO
// =====================================================

var selectedFileName = null;


// =====================================================
// SELECCIONAR ARCHIVO
// =====================================================

fileInput.addEventListener("change", function () {

    if (fileInput.files.length === 0) {
        return;
    }

    var file = fileInput.files[0];


    // Validar PDF
    if (file.type !== "application/pdf") {

        alert("Solo puedes seleccionar archivos PDF.");

        fileInput.value = "";
        fileName.textContent = "";

        deleteFileButton.style.display = "none";
        selectedFileName = null;

        return;
    }

    // Guardar nombre del archivo
    selectedFileName = file.name;

    // Mostrar nombre
    fileName.textContent = file.name;

    // Mostrar botón eliminar
    deleteFileButton.style.display = "inline-block";


    // Subir automáticamente
    uploadPolicy();
});


// =====================================================
// SUBIR PÓLIZA
// =====================================================

function uploadPolicy() {

    if (fileInput.files.length === 0) {
        return;
    }

    var file = fileInput.files[0];

    var formData = new FormData();

    formData.append(
        "file",
        file
    );


    // Desactivar controles mientras se procesa
    fileInput.disabled = true;
    sendButton.disabled = true;


    fetch("/upload-policy", {

        method: "POST",

        body: formData

    })

    .then(function (response) {

        if (!response.ok) {

            throw new Error(
                "Error HTTP: " + response.status
            );
        }

        return response.json();
    })

    .then(function (data) {

        console.log(
            "Póliza subida:",
            data
        );


        addBotMessage(
            "Tu póliza fue cargada correctamente. Ya puedes hacer preguntas sobre su contenido."
        );


        fileInput.disabled = false;

        toggleSendButton();
    })

    .catch(function (error) {

        console.error(
            "Error:",
            error
        );


        alert(
            "No se pudo procesar la póliza."
        );


        fileInput.value = "";
        fileName.textContent = "";

        deleteFileButton.style.display = "none";
        selectedFileName = null;

        fileInput.disabled = false;

        toggleSendButton();
    });
}


// =====================================================
// ELIMINAR PÓLIZA
// =====================================================

deleteFileButton.addEventListener(
    "click",
    function () {

        fetch(
            "/delete-policy",
            {
                method: "DELETE"
            }
        )

        .then(function (response) {

            if (!response.ok) {

                throw new Error(
                    "Error HTTP: " + response.status
                );
            }

            return response.json();
        })

        .then(function (data) {

            console.log(
                "Póliza eliminada:",
                data
            );


            fileInput.value = "";

            fileName.textContent = "";

            deleteFileButton.style.display = "none";
            
            selectedFileName = null;

            addBotMessage(
                "La póliza fue eliminada. Puedes subir una nueva cuando quieras."
            );
        })

        .catch(function (error) {

            console.error(
                "Error:",
                error
            );

            alert(
                "No se pudo eliminar la póliza."
            );
        });
    }
);


// =====================================================
// ACTIVAR / DESACTIVAR BOTÓN ENVIAR
// =====================================================

userInput.addEventListener(
    "input",
    toggleSendButton
);


function toggleSendButton() {

    sendButton.disabled =
        userInput.value.trim() === "";
}


// =====================================================
// BOTÓN ENVIAR
// =====================================================

sendButton.addEventListener(
    "click",
    sendMessage
);

function sendMessage() {

    var message = userInput.value.trim();

    if (message === "") {
        return;
    }

    // =================================================
    // CREAR MENSAJE VISUAL
    // =================================================

    var displayMessage = message;

    if (selectedFileName !== null) {

        displayMessage =
            "📎 " +
            selectedFileName +
            "\n" +
            message;
    }

    // Mostrar mensaje del usuario
    addUserMessage(
        displayMessage
    );

    // =================================================
    // LIMPIAR INPUT
    // =================================================

    userInput.value = "";

    toggleSendButton();

    // =================================================
    // LIMPIAR ADJUNTO DE LA INTERFAZ
    // =================================================

    fileInput.value = "";

    fileName.textContent = "";

    deleteFileButton.style.display =
        "none";

    selectedFileName = null;

    // =================================================
    // MOSTRAR PROCESANDO
    // =================================================

    var processingMessage =
        addBotMessage(
            "⏳ Preparando respuesta..."
        );

    // =================================================
    // SCROLL
    // =================================================

    chatBox.scrollTop =
        chatBox.scrollHeight;

    // =================================================
    // ENVIAR AL BACKEND
    // =================================================

    fetch(
        "/chatbot",
        {
            method: "POST",

            headers: {
                "Content-Type":
                    "application/json"
            },

            body: JSON.stringify({
                prompt: message
            })
        }
    )

    .then(function (response) {

        if (!response.ok) {

            throw new Error(
                "Error HTTP: " +
                response.status
            );
        }

        return response.text();
    })

    .then(function (data) {

        // Quitar "Preparando respuesta..."
        processingMessage.remove();

        // Mostrar respuesta real
        addBotMessage(
            data
        );
    })

    .catch(function (error) {

        console.error(
            "Error:",
            error
        );

        // Quitar "Preparando respuesta..."
        processingMessage.remove();

        // Mostrar error
        addBotMessage(
            "Ocurrió un error al procesar tu pregunta."
        );
    });
}

// =====================================================
// MENSAJE DEL USUARIO
// =====================================================

function addBotMessage(message) {

    var botMessageDiv =
        document.createElement("div");

    botMessageDiv.className =
        "message bot-message";

    if (
        message.startsWith('"') &&
        message.endsWith('"')
    ) {
        message =
            message.substring(
                1,
                message.length - 1
            );
    }

    message =
        message.replace(/\\n/g, "\n");

    message =
        message.replace(/\\\*/g, "*");

    botMessageDiv.innerHTML =
        marked.parse(message);

    chatBox.appendChild(
        botMessageDiv
    );

    chatBox.scrollTop =
        chatBox.scrollHeight;

    return botMessageDiv;
}