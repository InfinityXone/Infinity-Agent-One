"use client";
import { useState } from "react";

export default function Home() {
  const [messages, setMessages] = useState<{role:string, content:string}[]>([]);
  const [input, setInput] = useState("");

  async function sendMessage() {
    const newMsg = {role:"user", content: input};
    setMessages([...messages, newMsg]);
    setInput("");

    let url = "http://localhost:8001/chat";
    let body = { message: input };

    if (input.startsWith("/faucets")) url = "http://localhost:8001/ops/faucets";
    if (input.startsWith("/airdrops")) url = "http://localhost:8001/ops/airdrops";
    if (input.startsWith("/swarm")) url = "http://localhost:8001/ops/swarm";

    const resp = await fetch(url, {
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body: JSON.stringify(body)
    });
    const data = await resp.json();
    setMessages(m => [...m, {role:"agent", content: data.reply || JSON.stringify(data)}]);
  }

  return (
    <main className="flex flex-col h-screen bg-black text-white p-4">
      <div className="flex-1 overflow-y-auto border border-gray-700 rounded p-2 mb-2">
        {messages.map((m,i)=>(
          <div key={i} className={m.role==="user"?"text-green-400":"text-cyan-400"}>
            <b>{m.role==="user"?"You":"Infinity"}:</b> {m.content}
          </div>
        ))}
      </div>
      <div className="flex">
        <input value={input} onChange={e=>setInput(e.target.value)}
               className="flex-1 bg-gray-900 border border-gray-600 rounded p-2 mr-2"
               placeholder="Type /faucets, /airdrops, /swarm or just chat"/>
        <button onClick={sendMessage} className="bg-cyan-600 px-4 py-2 rounded">Send</button>
      </div>
    </main>
  );
}
