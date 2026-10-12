#!/usr/bin/env python3
"""📈 Pons Radar: monitoraggio in SOLA LETTURA dei pair token approvati su Pons (Robinhood Chain, chain 4663).
Nessuna firma, nessuna chiave privata, nessuna transazione: solo eth_getLogs / eth_call pubblici e API Robinhood."""
import json, os, time, html, requests

RPC = os.environ.get("RPC_URL", "https://rpc.mainnet.chain.robinhood.com")
RH_API = "https://api.robinhood.com/rhj/assets"
CHAIN = 4663
FACTORY = "0x7ed598bcef8bd9edd8c97a195c6d13f40801ec7e"
FACTORY_START = 26841846  # blocco di deploy della factory (primo log: 0x19992f6)
CHUNK = 9_999_999          # l'RPC pubblico accetta al massimo 10M blocchi per eth_getLogs
EXPLORER = "https://robinhoodchain.blockscout.com"
PONS = "https://ponsfamily.com/launchpad"
# topic0 calcolati con keccak256 dalle firme dell'ABI verificato su Blockscout (PonsV2LaunchFactory.sol)
T_APPROVAL = "0x060d1992d069dc524985f328329aae36102a017c59733c5c91fc0691ee0703b6"   # PairTokenApprovalUpdated(address,bool)
T_ECON = "0x67d517ee0e305d608b8410ddef27bbd2ed964d843d9b936e84ea2ad1bd65e5d1"       # PairTokenEconomicsUpdated(address,uint256,uint256,uint8)
SEL_APPROVED = "0x9831705e"  # approvedPairTokens(address)
SEL_ECON = "0x31082134"      # pairTokenEconomics(address)
SEL_SYMBOL, SEL_NAME = "0x95d89b41", "0x06fdde03"
NEW_DAYS = 7
S = requests.Session(); S.headers["User-Agent"] = "pons-pair-radar/1.0 (sola lettura)"

def rpc(method, params, tries=3):
    for i in range(tries):
        try:
            j = S.post(RPC, json={"jsonrpc": "2.0", "id": 1, "method": method, "params": params}, timeout=60).json()
            if "error" in j: raise RuntimeError(str(j["error"])[:200])
            return j["result"]
        except Exception as e:
            if i == tries - 1: raise
            time.sleep(2 + 3 * i)

def rpc_batch(calls):
    out = []
    for k in range(0, len(calls), 50):
        part = calls[k:k + 50]
        body = [{"jsonrpc": "2.0", "id": i, "method": m, "params": p} for i, (m, p) in enumerate(part)]
        try:
            res = S.post(RPC, json=body, timeout=60).json()
            if not isinstance(res, list): raise RuntimeError("batch non supportato")
            d = {r["id"]: r.get("result") for r in res}
            out += [d.get(i) for i in range(len(part))]
        except Exception:
            for m, p in part:
                try: out.append(rpc(m, p))
                except Exception: out.append(None)
    return out

def pad(a): return "0" * 24 + a.lower()[2:]
def dec_str(h):
    try:
        b = bytes.fromhex(h[2:]); off = int.from_bytes(b[:32], "big"); n = int.from_bytes(b[off:off + 32], "big")
        return b[off + 32:off + 32 + n].decode("utf-8", "replace")
    except Exception: return ""

def fetch_robinhood():
    r = S.get(RH_API, timeout=40); r.raise_for_status()
    out = {}
    for a in r.json().get("assets", []):
        for d in a.get("deployments") or []:
            if d.get("chainId") == CHAIN and d.get("contractAddress"):
                addr = d["contractAddress"].lower()
                out[addr] = {"indirizzo": addr, "ticker": a.get("tokenSymbol") or "", "nome": (a.get("tokenName") or "").replace(" • Robinhood Token", ""),
                             "stato_rh": (a.get("status") or "").replace("ASSET_STATUS_", "").lower(), "logo": a.get("logoUrl") or "", "isin": a.get("isin") or "",
                             "decimali": a.get("tokenDecimals")}
    return out

def fetch_logs(start, head):
    """Una query per topic (l'RPC pubblico limita a 100k blocchi le query con topic OR, 10M con un valore per posizione)."""
    logs = []
    for topic in (T_APPROVAL, T_ECON):
        s, step = start, CHUNK
        while s <= head:
            e = min(head, s + step)
            try:
                logs += rpc("eth_getLogs", [{"address": FACTORY, "fromBlock": hex(s), "toBlock": hex(e), "topics": [topic]}], tries=2)
                s, step = e + 1, CHUNK
            except Exception:
                if step < 2000: raise
                step //= 4
    return logs

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    now = int(time.time())
    try: hist = json.load(open("history.json"))
    except Exception: hist = {}
    hist.setdefault("rh_first_seen", {}); hist.setdefault("approved_first_seen", {}); hist.setdefault("blocchi_ts", {})
    first_run = "baseline_ts" not in hist
    if first_run: hist["baseline_ts"] = now
    errori = []

    rh = fetch_robinhood()
    for a in rh:
        hist["rh_first_seen"].setdefault(a, now)

    head = int(rpc("eth_blockNumber", []), 16)
    # cache incrementale dei log (rescansione completa ogni 24h per sicurezza contro reorg/omissioni)
    try: cache = json.load(open("logs_cache.json"))
    except Exception: cache = {}
    if not cache.get("fino") or now - cache.get("completo_ts", 0) > 86400:
        cache = {"fino": FACTORY_START - 1, "logs": [], "completo_ts": now}
    da = max(FACTORY_START, cache["fino"] - 2000)
    nuovi = fetch_logs(da, head)
    vist = {(l["transactionHash"], l["logIndex"]) for l in cache["logs"]}
    cache["logs"] += [{k: l[k] for k in ("topics", "data", "blockNumber", "transactionHash", "logIndex")} for l in nuovi if (l["transactionHash"], l["logIndex"]) not in vist]
    cache["fino"] = head
    json.dump(cache, open("logs_cache.json", "w"))
    logs = cache["logs"]
    blocks = sorted({l["blockNumber"] for l in logs} - set(hist["blocchi_ts"]))
    for b, res in zip(blocks, rpc_batch([("eth_getBlockByNumber", [b, False]) for b in blocks])):
        if res: hist["blocchi_ts"][b] = int(res["timestamp"], 16)
    ev = {}
    for l in sorted(logs, key=lambda l: (int(l["blockNumber"], 16), int(l["logIndex"], 16))):
        a = "0x" + l["topics"][1][-40:]; e = ev.setdefault(a, {"eventi_approvazione": 0, "eventi_economia": 0})
        ts = hist["blocchi_ts"].get(l["blockNumber"])
        if l["topics"][0] == T_APPROVAL:
            ok = int(l["data"], 16) == 1; e["eventi_approvazione"] += 1; e["approvato_evento"] = ok
            if ok and "approvato_ts" not in e: e["approvato_ts"] = ts; e["approvato_tx"] = l["transactionHash"]
            if ok: e["ultimo_approvato_ts"] = ts
            else: e["revocato_ts"] = ts
        else:
            d = l["data"][2:]; e["eventi_economia"] += 1
            e["economia_evento"] = {"phantomQuote": str(int(d[0:64], 16)), "graduationThreshold": str(int(d[64:128], 16)), "decimali": int(d[128:192], 16), "ts": ts}

    # Riconciliazione con lo stato on-chain: approvedPairTokens(addr) / pairTokenEconomics(addr) (eth_call, sola lettura)
    addrs = sorted(set(rh) | set(ev))
    calls = []
    for a in addrs:
        calls += [("eth_call", [{"to": FACTORY, "data": SEL_APPROVED + pad(a)}, "latest"]), ("eth_call", [{"to": FACTORY, "data": SEL_ECON + pad(a)}, "latest"])]
    res = rpc_batch(calls)
    stato = {}
    for i, a in enumerate(addrs):
        ap, ec = res[2 * i], res[2 * i + 1]
        st = {"approvato": None if ap is None else int(ap, 16) == 1}
        if ec and len(ec) >= 2 + 192:
            d = ec[2:]; pq, gt, dc = int(d[0:64], 16), int(d[64:128], 16), int(d[128:192], 16)
            if pq or gt: st["economia"] = {"phantomQuote": str(pq), "graduationThreshold": str(gt), "decimali": dc}
        stato[a] = st
    if any(v["approvato"] is None for v in stato.values()): errori.append("Alcune letture eth_call non riuscite: usato lo stato derivato dagli eventi.")

    # Pair non presenti nella lista Robinhood (ETH-wrapper, USDG, cbBTC...): leggi symbol/name
    altri = [a for a in ev if a not in rh]
    meta = rpc_batch([c for a in altri for c in (("eth_call", [{"to": a, "data": SEL_SYMBOL}, "latest"]), ("eth_call", [{"to": a, "data": SEL_NAME}, "latest"]))])
    tickers_rh = {v["ticker"].upper(): a for a, v in rh.items()}

    def human(v, dc):
        try: return round(int(v) / 10 ** dc, 6)
        except Exception: return None

    tokens = []
    for a in addrs:
        e = ev.get(a, {}); st = stato[a]
        appr = st["approvato"] if st["approvato"] is not None else e.get("approvato_evento", False)
        econ = st.get("economia") or {k: v for k, v in (e.get("economia_evento") or {}).items() if k != "ts"} or None
        if econ: econ = dict(econ, soglia_graduazione=human(econ["graduationThreshold"], econ["decimali"]), phantom=human(econ["phantomQuote"], econ["decimali"]))
        if a in rh:
            t = dict(rh[a], robinhood=True)
        else:
            i = altri.index(a); sym, nm = dec_str(meta[2 * i] or "0x"), dec_str(meta[2 * i + 1] or "0x")
            t = {"indirizzo": a, "ticker": sym, "nome": nm, "robinhood": False, "logo": ""}
            if sym.upper() in tickers_rh: t["sospetto"] = f"Ticker uguale a {sym} di Robinhood ma indirizzo diverso: possibile imitazione"
        fs = hist["rh_first_seen"].get(a)
        if appr:
            hist["approved_first_seen"].setdefault(a, now)
            t["stato"] = "pons"
        elif a in rh and fs and fs > hist["baseline_ts"] and now - fs < NEW_DAYS * 86400:
            t["stato"] = "nuovo"
        elif a in rh:
            t["stato"] = "candidato"
        else:
            t["stato"] = "revocato" if e.get("eventi_approvazione") else "altro"
        if a in rh and fs and fs > hist["baseline_ts"] and now - fs < NEW_DAYS * 86400: t["nuovo_rh"] = True
        t.update({"approvato_ts": e.get("approvato_ts"), "approvato_tx": e.get("approvato_tx"), "revocato_ts": e.get("revocato_ts"), "economia": econ,
                  "eventi": e.get("eventi_approvazione", 0), "visto_rh_ts": fs, "explorer": f"{EXPLORER}/token/{a}"})
        if a not in rh and t["stato"] == "altro" and not e: continue
        tokens.append(t)
    ordine = {"pons": 0, "nuovo": 1, "candidato": 2, "revocato": 3, "altro": 4}
    tokens.sort(key=lambda t: (ordine[t["stato"]], -(t.get("approvato_ts") or 0), t["ticker"]))
    conteggi = {k: sum(1 for t in tokens if t["stato"] == k) for k in ordine}
    conteggi["pons_robinhood"] = sum(1 for t in tokens if t["stato"] == "pons" and t["robinhood"])
    conteggi["robinhood_totale"] = len(rh)
    # Novità: approvazioni/revoche on-chain (orario del blocco) + nuovi token Robinhood rilevati dopo il primo avvio
    novita = []
    for t in tokens:
        if t.get("approvato_ts") and now - t["approvato_ts"] < 30 * 86400:
            novita.append({"tipo": "approvato", "ts": t["approvato_ts"], "ticker": t["ticker"], "nome": t["nome"], "indirizzo": t["indirizzo"], "robinhood": t["robinhood"], "tx": t.get("approvato_tx")})
        if t.get("revocato_ts") and now - t["revocato_ts"] < 30 * 86400:
            novita.append({"tipo": "revocato", "ts": t["revocato_ts"], "ticker": t["ticker"], "nome": t["nome"], "indirizzo": t["indirizzo"], "robinhood": t["robinhood"]})
        if t.get("nuovo_rh"):
            novita.append({"tipo": "nuovo_rh", "ts": t["visto_rh_ts"], "ticker": t["ticker"], "nome": t["nome"], "indirizzo": t["indirizzo"], "robinhood": True})
    novita.sort(key=lambda n: -n["ts"])
    data = {"novita": novita[:60], "baseline_ts": hist["baseline_ts"], "aggiornato": now, "blocco": head, "factory": FACTORY, "metodo": "eth_getLogs (PairTokenApprovalUpdated + PairTokenEconomicsUpdated, blocchi da 10M) + eth_call approvedPairTokens/pairTokenEconomics",
            "primo_avvio": first_run, "conteggi": conteggi, "errori": errori, "token": tokens}
    json.dump(data, open("data.json", "w"), ensure_ascii=False, indent=1)
    json.dump(hist, open("history.json", "w"), ensure_ascii=False, indent=1, sort_keys=True)
    try: presets = json.load(open("presets.json"))
    except Exception: presets = {"bozze": []}
    blob = json.dumps({"data": data, "presets": presets}, ensure_ascii=False).replace("</", "<\\/")
    for tpl, out in (("template.html", "index.html"), ("preset_template.html", "preset.html")):
        open(out, "w").write(open(tpl).read().replace("/*__DATA__*/null", blob))
    print(f"Robinhood 4663: {len(rh)} | eventi factory: {len(logs)} | conteggi: {conteggi}")

if __name__ == "__main__":
    main()
