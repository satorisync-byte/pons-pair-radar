# 📈 Pons Pair Radar

Radar in **sola lettura** dei pair token approvati su [Pons](https://ponsfamily.com/launchpad) (Robinhood Chain, chain ID 4663) e preparazione di bozze di meme token.

- Sito live: https://satorisync-byte.github.io/pons-pair-radar/
- Aggiornamento automatico ogni 5 minuti tramite GitHub Actions (`.github/workflows/update.yml`).
- Uso locale: `pip install -r requirements.txt && python3 aggregate.py` (genera `index.html`, `preset.html`, `data.json`).

## ⚠️ Ambito e avvertenze
- **Solo monitoraggio e preparazione**: nessuna chiave privata, nessuna firma, nessuna transazione, nessuna chiamata di lancio. Solo `eth_getLogs`/`eth_call` pubblici e l'API Robinhood.
- I Termini di Pons (https://ponsfamily.com/terms) escludono le giurisdizioni UE, Italia inclusa. Non è consulenza finanziaria o legale.
- Nessun avviso Telegram: le novità sono mostrate nella sezione **🔔 Novità** della dashboard.

## Come funziona
1. **Lista Robinhood**: `GET https://api.robinhood.com/rhj/assets`, filtrata ai deployment con `chainId` 4663 (ticker, nome, indirizzo, logo, ISIN). L'API non fornisce la data di deploy: si usa la data di primo rilevamento (`history.json`).
2. **Approvazioni Pons**: factory `PonsV2LaunchFactory` `0x7ed598bcef8bd9edd8c97a195c6d13f40801ec7e` (sorgente verificato su Blockscout).
   - `eth_getLogs` sull'RPC pubblico `https://rpc.mainnet.chain.robinhood.com`, un topic per query, blocchi da 10M (limite dell'RPC; con topic in OR il limite scende a 100k blocchi). Cache incrementale in `logs_cache.json`, rescansione completa ogni 24 h.
   - `PairTokenApprovalUpdated(address,bool)` → `0x060d1992…0703b6`
   - `PairTokenEconomicsUpdated(address,uint256,uint256,uint8)` → `0x67d517ee…e5d1`
   - Riconciliazione con `approvedPairTokens(address)` e `pairTokenEconomics(address)` via `eth_call`.
3. **Stati**: *Già su Pons* (approvato, con orario del blocco e soglia di graduazione), *Candidato* (nella lista Robinhood ma non approvato), *Nuovo su Robinhood* (comparso negli ultimi 7 giorni dopo il primo avvio).
4. **Imitazioni**: contano solo gli indirizzi della lista Robinhood; un pair con lo stesso ticker ma indirizzo diverso viene segnalato.

## Preset lancio (`preset.html`)
Bozze con i campi del lancio Pons: nome, ticker, descrizione, logo (URL o file salvato come dataURL; **prima del lancio va caricato su IPFS**), X, Telegram, Discord, sito, Farcaster, tassa creatore %, buyback, destinatario fee, dev-buy, note. Salvate nel `localStorage`, con Esporta/Importa JSON e “Copia tutto”. Per collegarle al radar committa il file esportato come `presets.json` (formato `{"bozze":[{"stock":"NVDA","nome":"…","ticker":"…",…}]}`).

## Limiti
Il cron di GitHub gira ogni 5 minuti ma può ritardare. Per una reazione al secondo servirebbe un server sempre acceso con websocket (`eth_subscribe`) o il feed del sequencer.
