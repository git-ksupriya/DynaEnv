import { useEffect, useRef, useState } from "react";
import "./App.css";

const COLORS = [
  "#FF6B6B",
  "#4D96FF",
  "#6BCB77",
  "#FFD93D",
  "#B983FF",
  "#FF8E72",
];

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  const socket = useRef(null);

  useEffect(() => {
    const interval = setInterval(() => {
        const now = Date.now() / 1000;

        setMessages((previousMessages) =>
        previousMessages.filter(
            (message) => message.expires_at > now
        )
        );
    }, 100);

    return () => {
        clearInterval(interval);
    };
    }, []);

  // Give this browser tab a temporary identity.
  const userId = useRef(
    crypto.randomUUID()
  );

  const color = useRef(
    COLORS[
      Math.floor(Math.random() * COLORS.length)
    ]
  );

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8000/ws");

    socket.current = ws;

    ws.onopen = () => {
      console.log("Connected to DynaEnv");
    };

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);

      setMessages((previousMessages) => [
        ...previousMessages,
        message,
      ]);
    };

    ws.onclose = () => {
      console.log("Disconnected from DynaEnv");
    };

    return () => {
      ws.close();
    };
  }, []);

  function sendMessage() {
    const text = input.trim();

    if (!text) return;

    const message = {
      id: crypto.randomUUID(),
      user_id: userId.current,
      text: text,
      color: color.current,
    };

    socket.current.send(JSON.stringify(message));

    setInput("");
  }

  function handleKeyDown(event) {
    if (event.key === "Enter") {
      sendMessage();
    }
  }

  return (
    <div className="app">

      {/* Navigation rail */}
      <aside className="nav-rail">

        <button title="Profile">
          👤
        </button>

        <button title="Settings">
          ⚙️
        </button>

        <button title="Chats">
          💬
        </button>

        <button title="New board">
          ＋
        </button>

      </aside>


      {/* Pinned / persistent area */}
      <aside className="context-panel">

        <div className="pinned-section">
          <h3>📌 Pinned</h3>
        </div>

      </aside>


      {/* Spatial environment */}
      <main className="board">

        <div className="messages">

          {messages.map((message, index) => (
            <div
              key={message.id}
              className="message"
              style={{
                left: `${20 + ((index * 17) % 65)}%`,
                top: `${10 + ((index * 23) % 75)}%`,
                borderColor: message.color,
              }}
            >
              <span
                className="sender-dot"
                style={{
                  backgroundColor: message.color,
                }}
              />

              {message.text}
            </div>
          ))}

        </div>


        {/* Message input */}
        <div className="input-area">

          <input
            type="text"
            value={input}
            onChange={(event) =>
              setInput(event.target.value)
            }
            onKeyDown={handleKeyDown}
            placeholder="Say something..."
          />

          <button onClick={sendMessage}>
            Send
          </button>

        </div>

      </main>

    </div>
  );
}

export default App;