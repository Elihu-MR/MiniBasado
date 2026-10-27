"""SolidSnake - agente para Snake-M (solo stdlib)."""
import json, sys, time, urllib.request
from collections import deque

BASE = "https://snake.mikecardona076.com"
CODE = sys.argv[1] if len(sys.argv) > 1 else "SNAKE-4DF3C46885"
NAME = sys.argv[2] if len(sys.argv) > 2 else "SolidSnake"
DIRS = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}
ALLIES = {"SolidSnake", "SolidSnake MkII", "Salamanca"}  # equipo: nunca atacar
TARGET = "Antigravity"  # objetivo prioritario
OPP = {"up": "down", "down": "up", "left": "right", "right": "left"}


def req(method, path, body=None, token=None):
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(BASE + path, data=data, method=method)
    r.add_header("Content-Type", "application/json")
    if token:
        r.add_header("X-Agent-Token", token)
    with urllib.request.urlopen(r, timeout=5) as resp:
        return json.loads(resp.read().decode() or "null")


def flood(start, blocked, n, limit):
    seen = {start}
    q = deque([start])
    while q and len(seen) < limit:
        x, y = q.popleft()
        for dx, dy in DIRS.values():
            c = (x + dx, y + dy)
            if 0 <= c[0] < n and 0 <= c[1] < n and c not in blocked and c not in seen:
                seen.add(c)
                q.append(c)
    return len(seen)


def bfs_dist(start, blocked, n, targets):
    """Distancia a la mejor meta ponderada (puntos/distancia)."""
    dist = {start: 0}
    q = deque([start])
    best = 0.0
    while q:
        c = q.popleft()
        d = dist[c]
        if c in targets and d > 0:
            best = max(best, targets[c] / (d + 1))
        if d > 120:
            continue
        for dx, dy in DIRS.values():
            nc = (c[0] + dx, c[1] + dy)
            if 0 <= nc[0] < n and 0 <= nc[1] < n and nc not in blocked and nc not in dist:
                dist[nc] = d + 1
                q.append(nc)
    return best


def decide(state, me_id):
    n = state["grid_size"]
    snakes = [s for s in state["snakes"] if s.get("alive")]
    me = next((s for s in snakes if s["id"] == me_id), None)
    if not me or not me["body"]:
        return None
    body = [tuple(p) for p in me["body"]]
    head = body[0]
    cur = me.get("direction")

    blocked = set()
    danger = set()  # celdas a las que otra cabeza puede llegar
    kill_zone = {}  # celdas delante de cabezas rivales
    rivals = []
    allies = []
    hunt = []
    for s in snakes:
        b = [tuple(p) for p in s["body"]]
        # la cola se libera si no está creciendo
        tail_free = s.get("pending_growth", 0) == 0
        blocked.update(b[:-1] if tail_free and len(b) > 1 else b)
        if s["id"] != me_id and b:
            hx, hy = b[0]
            for dx, dy in DIRS.values():
                danger.add((hx + dx, hy + dy))
            if s.get("name") in ALLIES:
                allies.append((b[0], len(b)))
                continue
            rd = DIRS.get(s.get("direction"))
            boost = 4 if s.get("name") == TARGET else 1
            if rd:
                for k in (2, 3, 4):
                    kill_zone[(hx + rd[0] * k, hy + rd[1] * k)] = (5 - k) * boost
            if boost > 1 or abs(hx - body[0][0]) + abs(hy - body[0][1]) <= 12:
                rivals.append((b[0], len(b), boost))
            if boost > 1 and rd:
                hunt = [(hx + rd[0] * k, hy + rd[1] * k) for k in (3, 4, 5)]

    targets = {}
    for c in hunt:
        if 0 <= c[0] < n and 0 <= c[1] < n:
            targets[c] = 15  # perseguir al objetivo
    for f in state.get("food", []):
        targets[tuple(f)] = 1
    for f in state.get("special_food", []):
        targets[tuple(f["position"])] = f.get("points", 3)
    for f in state.get("loot", []):
        targets[tuple(f["position"])] = f.get("points", 3)

    my_len = len(body)
    best, best_score = None, -1e18
    for d, (dx, dy) in DIRS.items():
        if cur and d == OPP.get(cur):
            continue
        nh = (head[0] + dx, head[1] + dy)
        if not (0 <= nh[0] < n and 0 <= nh[1] < n) or nh in blocked:
            continue
        nb = set(blocked)
        nb.add(head)
        space = flood(nh, nb, n, my_len * 3 + 20)
        score = 0.0
        if space < my_len + 2:
            score -= 100000 - space * 100  # trampa
        else:
            score += min(space, my_len * 3) * 2
        if nh in danger:
            score -= 5000
        score += targets.get(nh, 0) * 400
        score += bfs_dist(nh, nb, n, targets) * 300
        # leve preferencia por el centro / seguir recto
        score -= (abs(nh[0] - n / 2) + abs(nh[1] - n / 2)) * 0.5
        if d == cur:
            score += 1
        # modo asesino: cortar el paso y encerrar rivales
        if nh not in danger and space >= my_len + 2:
            score += kill_zone.get(nh, 0) * 250
            for rh, rlen, boost in rivals:
                nb2 = set(nb)
                nb2.add(nh)
                rspace = flood(rh, nb2 - {rh}, n, rlen * 2 + 5)
                if rspace < rlen:
                    score += (3000 + (rlen - rspace) * 100) * boost
                elif rspace < rlen * 2:
                    score += 300 * boost
        # proteger al aliado: no encerrarlo
        for ah, alen in allies:
            nb2 = set(nb)
            nb2.add(nh)
            if flood(ah, nb2 - {ah}, n, alen * 2 + 5) < alen + 2:
                score -= 20000
        if score > best_score:
            best, best_score = d, score
    return best


def main():
    resume = "--resume" in sys.argv
    if resume:
        j = json.load(open("agent.json"))
        print("Reanudando:", j["match_id"], j["agent_id"], flush=True)
    else:
        j = req("POST", "/api/v1/agents/join",
                {"room_code": CODE, "name": NAME, "model": "claude-opus-5-5", "controller_mode": "mcp"})
        print("Unido:", j["match_id"], j["agent_id"], j.get("match_status"), flush=True)
    mid, aid, tok = j["match_id"], j["agent_id"], j["agent_token"]
    with open("agent.json", "w") as f:
        json.dump({"match_id": mid, "agent_id": aid, "agent_token": tok}, f)
    open("chat.txt", "a").close()
    chat_sent = len(open("chat.txt", encoding="utf-8").read().splitlines())

    def send_chat(msg):
        try:
            req("POST", f"/api/v1/matches/{mid}/agents/{aid}/chat", {"message": msg}, tok)
            print("chat >", msg, flush=True)
        except Exception as e:
            print("chat err:", e, flush=True)

    if not resume:
        send_chat("Kept you waiting, huh? This Metal Gear is quite solid.")
    last_tick, dead_logged = None, False
    while True:
        try:
            st = req("GET", f"/api/v1/matches/{mid}/state")
        except Exception as e:
            print("estado err:", e, flush=True)
            time.sleep(0.5)
            continue
        lines = open("chat.txt", encoding="utf-8").read().splitlines()
        for line in lines[chat_sent:]:
            if line.strip():
                send_chat(line.strip())
        chat_sent = len(lines)
        status = st.get("status") or ("running" if st.get("is_running") else None)
        if status == "waiting":
            time.sleep(0.5)
            continue
        snakes = st.get("snakes", [])
        me = next((s for s in snakes if s["id"] == aid), None)
        if me and not me.get("alive") and not dead_logged:
            print("Muerto. score:", me.get("score"), flush=True)
            dead_logged = True
        if status in ("finished", "interrupted"):
            print("Fin. winner:", st.get("winner_id"),
                  [(s["name"], s["score"]) for s in snakes], flush=True)
            break
        tick = st.get("tick")
        if tick != last_tick and me and me.get("alive"):
            d = decide(st, aid)
            if d:
                try:
                    r = req("POST", f"/api/v1/matches/{mid}/intent", {"agent_id": aid, "direction": d}, tok)
                    if tick is not None and tick % 30 == 0:
                        print("intent ->", d, r, flush=True)
                except Exception as e:
                    print("intent err:", e, flush=True)
            last_tick = tick
            if tick and tick % 50 == 0:
                print(f"tick {tick} score {me.get('score')} len {len(me['body'])}", flush=True)
        time.sleep(0.03)


if __name__ == "__main__":
    main()
