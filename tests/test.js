const webSocket = require("ws")

const table = "table1"
const url = "ws://127.0.0.1:8000/ws/" + table

console.log(url)

const options = {
    "origin": "http://127.0.0.1:8000",
    "headers": {
        "token": "jakis token lol"
    }
}

const ws = new webSocket(url, options)

ws.on("open", () => {
    console.log("connected")
})

ws.on("message", (data) => {
    console.log("new message: ")
    console.log(JSON.parse(data.toString()))
})

ws.on("error", (error) => {
    console.log(error)
})

ws.on("close", () => {
    console.log("closed")
    ws.close()
})

process.stdin.on("data", (data) => {
    const message = data.toString().trim();

    if (message === "close") {
        ws.close();
    }

    if (message === "call"){
        ws.send(JSON.stringify({
            "action": "call"
        }))
    }

    if (message === "bet"){
        ws.send(JSON.stringify({
            "action": "bet",
            "amount": 10
        }))
    }

    if (message === "fold"){
        ws.send(JSON.stringify({
            "action": "fold"
        }))
    }

    if (message === "get state"){
        ws.send(JSON.stringify({
            "action": "get state"
        }))
    }
});