import os
from flask import Flask, request, redirect, url_for, render_template_string, abort, session

from db_helper import (
    init_db, create_conversation, get_conversation,
    set_conversation_title_if_empty, get_conversations,
    insert_message, get_messages_for_conversation,
    upsert_fact, delete_fact, list_facts, get_all_facts_dict
)
from client import respond_with_openai, respond_about_me

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret")
FACTS_PASSWORD = os.getenv("FACTS_PASSWORD", "hello123")

# app.py (excerpt) — unified chick-themed template
TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>ChickieGPT 🐣</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    :root {
      --bg: #fffdf6;
      --panel: #fffefc;
      --text: #3a2c1a;
      --muted: #8b7355;
      --accent: #facc15;
      --accent-soft: #fef9c3;
      --border: #fce7a1;
      --shadow: 0 6px 18px rgba(250,204,21,0.3);
    }
    * { box-sizing: border-box; }
    body { margin: 0; background: var(--bg); color: var(--text); font: 15px/1.45 "Comic Neue", system-ui, sans-serif; }
    .app { display:flex; height:100vh; gap: 14px; padding: 14px; }
    .sidebar {
      width: 300px; background: var(--panel); border: 2px solid var(--border); border-radius: 20px;
      padding: 14px; box-shadow: var(--shadow); display:flex; flex-direction:column; gap: 12px; overflow: hidden;
    }
    .logo { font-weight: 700; font-size: 18px; display:flex; align-items:center; gap:6px; }
    .btn { background: var(--accent); color: #3a2c1a; border: 0; padding: 6px 12px; border-radius: 12px; font-weight: 700; cursor: pointer; box-shadow: var(--shadow); }
    .nav { display:flex; flex-direction:column; gap:8px; }
    .nav a, .nav button.linky {
      display:block; padding:10px; border-radius:12px; text-decoration:none; color:inherit; background: var(--accent-soft); border:1px solid var(--border); text-align:left;
    }
    .nav a.active, .nav button.linky.active { background: var(--accent); border-color: var(--accent); font-weight:700; }
    .convos { overflow:auto; max-height: 50vh; }
    .convo { display:block; padding: 10px; border-radius: 12px; text-decoration:none; border:1px solid var(--border); margin-bottom: 8px; background: var(--accent-soft); }
    .convo.active { background: var(--accent); }
    .meta { font-size: 12px; color: var(--muted); margin-top: 2px; }
    .main { flex:1; display:flex; flex-direction: column; }
    .card { background: var(--panel); border: 2px solid var(--border); border-radius: 20px; box-shadow: var(--shadow); display:flex; flex-direction: column; flex: 1; }
    .header { padding: 14px 16px; display:flex; justify-content:space-between; align-items:center; border-bottom: 2px solid var(--border); }
    .title { font-weight: 700; font-size:16px; }
    .small { color: var(--muted); font-size: 12px; }
    .chat { padding: 16px; overflow:auto; flex: 1; }
    .row { display:flex; gap: 10px; margin-bottom: 12px; align-items:flex-end; }
    .row.assistant { justify-content:flex-start; }
    .row.user { justify-content:flex-end; }
    .bubble { max-width: 75%; padding: 10px 14px; border-radius: 18px; white-space: pre-wrap; word-wrap: break-word; }
    .assistant .bubble { background: var(--accent-soft); border: 2px solid var(--border); }
    .user .bubble { background: var(--accent); border: 2px solid var(--border); font-weight: 600; }
    .avatar { width: 34px; height: 34px; border-radius: 50%; display:flex; align-items:center; justify-content:center; font-size: 18px; background: var(--accent); border: 2px solid var(--border); flex-shrink:0; }
    .user .avatar { background: var(--accent-soft); }
    .time { font-size: 11px; color: var(--muted); margin-top: 4px; text-align:center; }
    .composer { display:flex; gap: 10px; align-items:flex-start; padding: 12px; border-top: 2px solid var(--border); }
    textarea { flex:1; resize: none; min-height: 44px; padding: 10px; border-radius: 12px; border: 2px solid var(--border); background: var(--accent-soft); color: var(--text); font: inherit; }
    table { width:100%; border-collapse: collapse; }
    th, td { border:1px solid var(--border); padding:8px; }
    th { background: var(--accent-soft); text-align:left; }
    .rowline { display:flex; gap:10px; margin: 12px 0; }
    input[type=text] { flex:1; padding:8px; border:2px solid var(--border); border-radius:12px; background: var(--accent-soft); }
  </style>
</head>
<body>
<div class="app">
  <!-- SIDEBAR -->
  <aside class="sidebar">
    <div style="display:flex; align-items:center; justify-content:space-between;">
      <div class="logo"><span>🐥</span> ChickieGPT</div>
      <form method="post" action="{{ url_for('new_chat') }}">
        <button class="btn" type="submit">New</button>
      </form>
    </div>

    <div class="nav">
      <a href="{{ url_for('chat', cid=current_cid) }}" class="{% if page=='chat' %}active{% endif %}">💬 Chat</a>
      <a href="{{ url_for('facts_page') }}" class="{% if page=='facts' %}active{% endif %}">
  {% if facts_authed %}📝 Manage My Facts{% else %}🔒 Manage My Facts{% endif %}
</a>
      <div class="small">Tip: use “Ask about me” checkbox to know more about me.</div>
    </div>

    <div class="small" style="margin-top:8px; font-weight:700;">Conversations</div>
    <div class="convos">
      {% for conv in conversations %}
        <a class="convo {% if current_cid == conv['id'] %}active{% endif %}" href="{{ url_for('chat', cid=conv['id']) }}">
          <div>{{ conv['title'] or ('Chat ' ~ conv['id']) }}</div>
          <div class="meta">{{ conv['created_at'] }}</div>
        </a>
      {% endfor %}
    </div>
  </aside>

  <!-- MAIN PANE -->
  <main class="main">
    <section class="card">
      <div class="header">
        {% if page == 'chat' %}
          <div>
            <div class="title">🐤 {{ current_title or ('Chat ' ~ current_cid) }}</div>
            <div class="small">ID: {{ current_cid }}</div>
          </div>
          {% if error %}<div class="small" style="color:#ef4444;">{{ error }}</div>{% endif %}
        {% else %}
          <div>
            <div class="title">📝 Manage My Facts</div>
            <div class="small">Add, update, or remove profile facts used by “Ask about me”.</div>
          </div>
        {% endif %}
      </div>

      {% if page == 'chat' %}
        <!-- CHAT VIEW -->
        <div id="chat" class="chat">
          {% if messages|length == 0 %}
            <div class="small">No messages yet—say cheep 🐣</div>
          {% endif %}
          {% for m in messages %}
            <div class="row {{ m['role'] }}">
              {% if m['role'] == 'assistant' %}
                <div class="avatar">🐣</div>
              {% endif %}
              <div>
                <div class="bubble">{{ m['content'] }}</div>
                <div class="time">{{ m['timestamp'] }}</div>
              </div>
              {% if m['role'] == 'user' %}
                <div class="avatar">🙂</div>
              {% endif %}
            </div>
          {% endfor %}
        </div>

        <form class="composer" method="post" action="{{ url_for('chat', cid=current_cid) }}">
          <textarea name="message" placeholder="Type your message… say cheep 🐥" required></textarea>
          <label class="small" style="display:flex;align-items:center;gap:6px;">
            <input type="checkbox" name="about_me"> Ask about me
          </label>
          <button class="btn" type="submit">Send 🐤</button>
        </form>

      {% elif page == 'facts' %}
        <!-- FACTS VIEW (password-protected) -->
      <div class="chat" style="padding: 16px 16px 0;">
        {% if not facts_authed %}
          <div style="max-width:480px; margin: 30px auto; background: var(--panel); border:2px solid var(--border); border-radius:16px; padding:16px;">
            <div class="title" style="margin-bottom:8px;">🔒 Enter Password</div>
            {% if facts_error %}<div class="small" style="color:#ef4444; margin-bottom:8px;">{{ facts_error }}</div>{% endif %}
            <form method="post" action="{{ url_for('facts_page') }}">
              <input type="hidden" name="action" value="login">
              <div class="rowline">
                <input type="password" name="facts_password" placeholder="Password" required>
                <button class="btn" type="submit">Unlock</button>
              </div>
            </form>
            <div class="small" style="margin-top:8px;color:var(--muted);">
              Tip: set an environment variable FACTS_PASSWORD to change this password.
            </div>
          </div>
        {% else %}
          <form method="post" action="{{ url_for('facts_page') }}" style="display:flex; justify-content:flex-end; padding: 8px 0 0 0;">
            <button class="btn" type="submit" name="action" value="logout">Logout 🔐</button>
          </form>

          <form method="post" action="{{ url_for('facts_page') }}" class="rowline">
            <input type="text" name="key" placeholder="Key (e.g., University)" required>
            <input type="text" name="value" placeholder="Value (e.g., UCI Data Science)">
            <button class="btn" type="submit" name="action" value="upsert">Save / Update</button>
          </form>

          <div style="padding: 0 0 16px;">
            <table>
              <tr><th>Key</th><th>Value</th><th>Updated</th><th>Action</th></tr>
              {% for f in facts %}
                <tr>
                  <td>{{ f['key'] }}</td>
                  <td>{{ f['value'] }}</td>
                  <td>{{ f['updated_at'] }}</td>
                  <td>
                    <form method="post" action="{{ url_for('facts_page') }}" style="display:inline;">
                      <input type="hidden" name="key" value="{{ f['key'] }}">
                      <button class="btn" type="submit" name="action" value="delete">Delete</button>
                    </form>
                  </td>
                </tr>
              {% endfor %}
            </table>
          </div>
        {% endif %}
      </div>
    {% endif %}
    </section>
  </main>
</div>
<script>
  // Auto-scroll chat to bottom
  const chatEl = document.getElementById('chat');
  if (chatEl) chatEl.scrollTop = chatEl.scrollHeight;
</script>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def root():
    init_db()
    cid = create_conversation()
    return redirect(url_for("chat", cid=cid))

@app.route("/new", methods=["POST"])
def new_chat():
    init_db()
    cid = create_conversation()
    return redirect(url_for("chat", cid=cid))

@app.route("/c/<int:cid>", methods=["GET", "POST"])
def chat(cid):
    init_db()
    conv = get_conversation(cid)
    if not conv:
        abort(404, description="Conversation not found")

    error = None

    if request.method == "POST":
        user_text = (request.form.get("message") or "").strip()
        about_me_mode = request.form.get("about_me") == "on"

        if user_text:
            insert_message(cid, "user", user_text)
            set_conversation_title_if_empty(cid, user_text[:60])

            if about_me_mode:
                facts = get_all_facts_dict()
                answer = respond_about_me(facts, user_text)
            else:
                msgs = [{"role": "system", "content": "You are a helpful assistant."}]
                conv_msgs = get_messages_for_conversation(cid, limit=200)
                msgs += [{"role": r["role"], "content": r["content"]} for r in conv_msgs]
                answer = respond_with_openai(msgs)

            insert_message(cid, "assistant", answer)

    messages = get_messages_for_conversation(cid, limit=500)
    conversations = get_conversations()
    current_title = conv["title"]

    return render_template_string(
        TEMPLATE,
        page="chat",
        conversations=conversations,
        messages=messages,
        current_cid=cid,
        current_title=current_title,
        error=error
    )

@app.route("/facts", methods=["GET", "POST"])
def facts_page():
    init_db()

    facts_error = None
    authed = bool(session.get("facts_authed"))

    if request.method == "POST":
        action = request.form.get("action")

        if action == "login":
            supplied = (request.form.get("facts_password") or "").strip()
            if supplied and supplied == FACTS_PASSWORD:
                session["facts_authed"] = True
                authed = True
            else:
                facts_error = "Incorrect password."
                authed = False

        elif action == "logout":
            session.pop("facts_authed", None)
            authed = False

        elif action in ("upsert", "delete"):
            # Only allow edit actions when authed
            if not authed:
                facts_error = "Please unlock with the password first."
            else:
                key = (request.form.get("key") or "").strip()
                if action == "upsert" and key:
                    value = (request.form.get("value") or "").strip()
                    upsert_fact(key, value)
                elif action == "delete" and key:
                    delete_fact(key)

    facts = list_facts() if authed else []
    conversations = get_conversations()

    current_cid = conversations[0]["id"] if conversations else None
    current_title = None

    return render_template_string(
        TEMPLATE,
        page="facts",
        conversations=conversations,
        current_cid=current_cid,
        current_title=current_title,
        facts=facts,
        facts_authed=authed,
        facts_error=facts_error,
        messages=[],
        error=None
    )

if __name__ == "__main__":
    init_db()
    app.run(debug=True)