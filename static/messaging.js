
String.prototype.replaceAt = function (index, replacement) {
    return this.substring(0, index) + replacement + this.substring(index + replacement.length);
}

const messageform = document.getElementById("messageform")
const messagebox = document.getElementById("message")
const messagecontainer = document.getElementById("container")
const typingprompt = document.getElementById("typing")
const pingcount = document.getElementById("ping-count")
const currenttime = document.getElementById("current-time")
const statustext = document.getElementById("status-text")
const userlist = document.getElementById("user-list")
var username = ""

messagebox.focus();

document.addEventListener("keydown", evt => {
    messagebox.focus();
})
function input(prompt, callback) {
    typingprompt.innerHTML = prompt + "▮"
    messagebox.onkeyup = evt => {
        var preview = messagebox.value
        preview = preview.replaceAt(evt.target.selectionStart, "▮")
        typingprompt.innerHTML = prompt + preview
        messagecontainer.scrollTop = messagecontainer.scrollHeight;
    }
    messagebox.oninput = evt => {
        var preview = messagebox.value
        preview = preview.replaceAt(evt.target.selectionStart, "▮")
        typingprompt.innerHTML = prompt + preview
        messagecontainer.scrollTop = messagecontainer.scrollHeight;
    }
    messageform.onsubmit = ev => {
        ev.preventDefault()
        username = messagebox.value
        messagebox.value = ""
        typingprompt.innerHTML = ""
        callback()
    };
}
input("Username: ", main)
currenttime.innerHTML = "Time: " + new Date().toLocaleTimeString()
setInterval(() => {
    currenttime.innerHTML = "Time: " + new Date().toLocaleTimeString()
}, 1000);
function main() {
    var socket = io();
    var lastping;

    var pinginterval = setInterval(() => {
        lastping = Date.now()
        socket.emit("ping")
    }, 1000);

    const commands = {
        "/disconnect": () => {
            socket.emit("left", { user: username })
            pingcount.innerHTML = "n/a"
            socket.ondisconnect()
            console.log("Disconnected.")
            alert("Disconnecting...")
            clearInterval(pinginterval);
        },
        "/reconnect": () => {
            socket.connect();
        }
    }

    window.onbeforeunload = closingCode;
    function closingCode() {
        commands["/disconnect"]();
        return null;
    }

    socket.on("pingresponse", function (response) {
        var ping = Date.now() - lastping
        pingcount.innerHTML = "Ping: " + ping + "ms"
    })

    function resetUserList() {
        while (userlist.firstChild) {
            userlist.removeChild(userlist.lastChild);
        }
    }
    function isCommand(text) {
        return text in commands
    }

    function runCommand(commandname) {
        commands[commandname]();
    }

    function moveToBottom() {
        messagecontainer.appendChild(typingprompt);
    }

    function CreateNewMessage(author, content, epochdate) {
        message = document.createElement('div');
        if (epochdate != null) {
            timestamp = new Date(epochdate * 1000)
            console.log(timestamp)
            message.innerHTML = author + ": " + content + " (" + timestamp.toLocaleTimeString() + ")";
        } else {
            message.innerHTML = author + ": " + content;
        }
        message.classList.add("postedmessage");
        return message;
    }

    socket.on("onconnect", function () {
        socket.emit("joined", { user: username })
        statustext.innerHTML = "Status: connected"
        messagecontainer.appendChild(CreateNewMessage("Server", "you're now connected!"))
        messagecontainer.scrollTop = messagecontainer.scrollHeight;
        moveToBottom();
        resetUserList();
    })
    socket.on("disconnect", function () {
        statustext.innerHTML = "Status: disconnected"
        messagecontainer.appendChild(CreateNewMessage("Server", "disconnected from server."))
        messagecontainer.scrollTop = messagecontainer.scrollHeight;
        moveToBottom();
        resetUserList();
    });
    socket.on("onmessage", function (json) {
        messagecontainer.appendChild(CreateNewMessage(json.author, json.content, json.timestamp))
        messagecontainer.scrollTop = messagecontainer.scrollHeight;
        moveToBottom();
    });
    socket.on("userupdate", function (json) {
        resetUserList()
        json.users.forEach(user => {
            userelement = document.createElement("li")
            userelement.innerHTML = user
            userlist.appendChild(userelement)
        });
    });
    socket.on("userleft", function (json) {
        messagecontainer.appendChild(CreateNewMessage("Server", json.user + " left."))
        messagecontainer.scrollTop = messagecontainer.scrollHeight;
        moveToBottom();
    })
    messageform.onsubmit = ev => {
        ev.preventDefault()
        if (isCommand(messagebox.value)) {
            runCommand(messagebox.value)
            messagebox.value = ""
            typingprompt.innerHTML = ""
            moveToBottom();
            return
        }
        if (!socket.connected) {
            messagebox.value = ""
            typingprompt.innerHTML = ""
            messagecontainer.appendChild(CreateNewMessage("Server", "you're not connected... Reconnect to continue sending messages."))
            moveToBottom();
            return
        }
        socket.emit('message', { data: messagebox.value, author: username });
        messagebox.value = ""
        typingprompt.innerHTML = ""
    };

    messagebox.onkeyup = evt => {
        var preview = messagebox.value
        preview = preview.replaceAt(evt.target.selectionStart, "▮")
        typingprompt.innerHTML = preview
        messagecontainer.scrollTop = messagecontainer.scrollHeight;
    }
    messagebox.oninput = evt => {
        var preview = messagebox.value
        preview = preview.replaceAt(evt.target.selectionStart, "▮")
        typingprompt.innerHTML = preview
        messagecontainer.scrollTop = messagecontainer.scrollHeight;
    }
}