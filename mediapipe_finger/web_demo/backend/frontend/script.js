const startButton =
    document.getElementById("startButton");

const video =
    document.getElementById("camera");

const canvas =
    document.getElementById("frameCanvas");

const backendStatus =
    document.getElementById("backendStatus");

const gestureStatus =
    document.getElementById("gestureStatus");

const middleFingerSound =
    document.getElementById("middleFingerSound");


const ctx = canvas.getContext("2d");


let socket;
let frameTimer;

let waitingForResult = false;
let middleFingerLatched = false;
let stream;
let cameraRunning = false;

startButton.addEventListener(
    "click",
    () => {

        if (cameraRunning) {
            stopDemo();
        }
        else {
            startDemo();
        }

    }
);


async function startDemo() {

    try {

        stream =
            await navigator.mediaDevices.getUserMedia({
                video: {
                    width: 640,
                    height: 480,
                    facingMode: "user"
                },

                audio: false
            });


        video.srcObject = stream;

        await video.play();


        connectWebSocket();


        cameraRunning = true;
        startButton.textContent = "Stop Camera";

    }
    catch (error) {

        console.error(error);

        gestureStatus.textContent =
            "Camera permission failed";
    }
}

function stopDemo() {

    clearInterval(frameTimer);

    if (socket) {
        socket.close();
    }

    if (stream) {

        stream.getTracks().forEach(
            track => track.stop()
        );
    }

    video.srcObject = null;

    waitingForResult = false;
    middleFingerLatched = false;
    cameraRunning = false;

    backendStatus.textContent =
        "Disconnected";

    backendStatus.style.color =
        "red";

    gestureStatus.textContent =
        "Waiting";

    startButton.textContent =
        "Start Camera";
}

function connectWebSocket() {

    const protocol =
        location.protocol === "https:"
            ? "wss"
            : "ws";


    socket = new WebSocket(
        `${protocol}://${location.host}/ws`
    );


    socket.onopen = () => {

        backendStatus.textContent =
            "Connected";

        backendStatus.style.color =
            "lightgreen";

        startSendingFrames();
    };


    socket.onmessage = (event) => {

        waitingForResult = false;

        handleGesture(event.data);
    };


    socket.onclose = () => {

        backendStatus.textContent =
            "Disconnected";

        backendStatus.style.color =
            "red";
    };


    socket.onerror = (error) => {

        console.error(
            "WebSocket error:",
            error
        );
    };
}


function startSendingFrames() {

    frameTimer = setInterval(
        sendFrame,
        125
    );
}


function sendFrame() {

    if (
        waitingForResult ||
        !socket ||
        socket.readyState !== WebSocket.OPEN ||
        video.readyState < 2
    ) {
        return;
    }


    canvas.width = 640;
    canvas.height = 480;


    ctx.drawImage(
        video,
        0,
        0,
        canvas.width,
        canvas.height
    );


    canvas.toBlob(

        async (blob) => {

            if (!blob) {
                return;
            }


            const buffer =
                await blob.arrayBuffer();


            waitingForResult = true;


            socket.send(buffer);
        },

        "image/jpeg",
        0.7
    );
}


function handleGesture(gesture) {

    if (gesture === "middle_finger") {

        gestureStatus.textContent =
            "Middle Finger";

        if (!middleFingerLatched) {

            middleFingerSound
                .cloneNode()
                .play()
                .catch(() => {});

            middleFingerLatched = true;
        }
    }

    else if (gesture === "normal") {

        gestureStatus.textContent =
            "Normal";

        middleFingerLatched = false;
    }
}