import { useEffect, useRef, useState } from "react";
import "./App.css";

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  const socket = useRef(null);

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8000/ws");

    socket.current = ws;

    ws.onopen = () => {
      console.log("Connected to DynaEnv server");
    };

    ws.onmessage = (event) => {
      setMessages((previousMessages) => [
        ...previousMessages,
        event.data,
      ]);
    };

    ws.onclose = () => {
      console.log("Disconnected from DynaEnv server");
    };

    return () => {
      ws.close();
    };
  }, []);

  function sendMessage() {
    const message = input.trim();

    if (!message) {
      return;
    }

    socket.current.send(message);
    setInput("");
  }

  function handleKeyDown(event) {
    if (event.key === "Enter") {
      sendMessage();
    }
  }

  return (
    <div className="app">

      <div className="left-panel">

        <div className="pinned-section">
          <h2>📌 Pinned</h2>
        </div>

        <div className="input-section">
          <input
            type="text"
            value={input}
            onChange={(event) => setInput(event.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type a message..."
          />

          <button onClick={sendMessage}>
            Send
          </button>
        </div>

      </div>

      <div className="conversation">
        {messages.map((message, index) => (
          <div
            className="message"
            key={index}
            style={{
              left: `${20 + ((index * 17) % 65)}%`,
              top: `${10 + ((index * 23) % 75)}%`,
            }}
          >
            {message}
          </div>
        ))}
      </div>

    </div>
  );
}

export default App;