const webSocket = require("ws")

const table = "table1"
const playerID = "player1"
const url = "ws://127.0.0.1:8000/ws/" + table + "/" + playerID

console.log(url)

const message = {
    "action": "test"
}

const options = {
    "origin": "http://127.0.0.1:8000"
}

const ws = new webSocket(url, options)

ws.on("open", () => {
    ws.send(JSON.stringify(message))
})

ws.on("message", (data) => {
    console.log(JSON.parse(data.toString()))
})

ws.on("error", (error) => {
    console.log(error)
})

