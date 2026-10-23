import { useState } from "react";

const API = "http://127.0.0.1:8000";

export default function App() {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([
    { role: "suvi", text: "I am on your command. What would you like to do?" }
  ]);
  const [busy, setBusy] = useState(false);

  async function send(e) {
    e?.preventDefault();
    const text = message.trim();
    if (!text || busy) return;
    setMessages(old => [...old, { role: "you", text }]);
    setMessage("");
    setBusy(true);
    try {
      const response = await fetch(`${API}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text })
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Request failed");
      setMessages(old => [...old, { role: "suvi", text: data.reply }]);
    } catch (err) {
      setMessages(old => [...old, {
        role: "suvi",
        text: `I could not reach the backend. Check that the SUVI API is running. (${err.message})`
      }]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="shell">
      <header className="topbar">
        <div className="brand-mark">S</div>
        <div><h1>SUVI</h1><p>SMART UNIFIED VOICE INTELLIGENCE</p></div>
        <span className="status"><i /> LOCAL SYSTEM</span>
      </header>
      <section className="hero">
        <div className="orb"><div className="orb-core">S</div></div>
        <p className="eyebrow">YOUR PERSONAL AI</p>
        <h2>I'm listening.</h2>
        <p className="muted">Type a command to begin. Voice integration connects to your existing SUVI engine.</p>
      </section>
      <section className="panel">
        <div className="panel-heading"><h3>Conversation</h3><span>LOCAL ASSISTANT</span></div>
        <div className="messages" aria-live="polite">
          {messages.map((item, i) => (
            <div className={`message ${item.role}`} key={i}>
              <b>{item.role === "you" ? "YOU" : "SUVI"}</b>
              <p>{item.text}</p>
            </div>
          ))}
          {busy && <div className="message suvi"><b>SUVI</b><p>Thinking…</p></div>}
        </div>
        <form onSubmit={send} className="composer">
          <input value={message} onChange={e => setMessage(e.target.value)}
            placeholder="Ask SUVI anything…" aria-label="Message SUVI" maxLength={4000} />
          <button disabled={busy || !message.trim()} type="submit">SEND ↗</button>
        </form>
      </section>
      <footer>SUVI • Local-first assistant • Actions require explicit enablement</footer>
    </main>
  );
}
