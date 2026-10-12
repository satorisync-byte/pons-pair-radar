// Suggerimenti meme token basati su regole (settore dell'azienda → temi). Sono solo spunti, da verificare (marchi registrati!).
const SETTORI={
 chip:{t:'NVDA AMD INTC MU AVGO TSM MRVL SNDK SKHY QCOM ARM SMCI SOXX AAOI WDC ASML TXN AMAT LRCX KLAC PENG',k:/semicond|micro|chip/i},
 ai:{t:'PLTR SNOW DDOG NBIS NET CRWV AI PATH ORCL IBM MSFT GOOGL META AMZN CRM ADBE NOW S',k:/software|cloud|data/i},
 auto:{t:'TSLA RIVN F GM LCID NIO UBER LYFT',k:/motor|auto/i},
 spazio:{t:'RKLB ASTS LMT BA RCAT SPCX LUNR PL KTOS NOC RTX',k:/aero|space|defen/i},
 crypto:{t:'COIN MSTR HOOD CRCL BULL GLXY MARA RIOT CLSK BMNR SBET WYFI',k:/coin|bitcoin|crypto|digital/i},
 meme:{t:'GME AMC BB DJT RDDT SNAP RBLX TTWO NFLX SPOT DIS ROKU',k:/entertain|media|game/i},
 farma:{t:'LLY PFE MRNA JNJ HIMS NVO ABBV MRK UNH',k:/pharm|thera|bio|health/i},
 energia:{t:'CEG BE USO OKLO SMR VST XOM CVX NEE CCJ',k:/energy|power|oil|nuclear|uranium/i},
 metalli:{t:'GLD SLV GDX',k:/gold|silver|metal|mining/i},
 indice:{t:'SPY QQQ INDA EWY SGOV BND VTI IWM DIA TLT',k:/ETF|Trust|Fund|Index|Treasury|iShares|SPDR|Vanguard/i},
 consumo:{t:'COST LULU SHOP BABA AMZN NKE SBUX MCD WMT UPS FIG',k:/retail|store|food|apparel/i},
 quantum:{t:'QUBT IONQ RGTI QBTS QNT',k:/quantum/i}};
const TEMI={
 chip:[['{N} Chipmunk','CHIP','Lo scoiattolo che accumula GPU invece di noccioline.','scarsità di chip / corsa all\'AI'],['Wafer {T}','WAFR','Sottile, croccante, sempre esaurito.','gioco di parole sui wafer di silicio'],['{T} Moore','MOORE','La legge di Moore, ma per il prezzo.','raddoppi continui'],['Silicon Pepe','SPEPE','Pepe in camice bianco dentro la fab.','meme classico + settore'],['Baby {T}','B{T}','Il figlio meme di {N}.','formato "baby" collaudato']],
 ai:[['{N} Brain','BRAIN','Il cervello AI che non dorme mai.','narrativa AI'],['Prompt {T}','PRMPT','Un prompt alla volta verso la luna.','cultura prompt'],['Robo {T}','ROBO','Il bot che compra solo verde.','meme robot'],['{T} Cloud Cat','CCAT','Un gatto che vive nel cloud.','animale + cloud'],['Baby {T}','B{T}','Il figlio meme di {N}.','formato "baby"']],
 auto:[['{N} Turbo','TURBO','Da 0 a luna in 3 secondi.','velocità'],['Ludicrous {T}','LUDI','Modalità ludicrous attiva.','cultura auto/EV'],['{T} Robotaxi','RTAXI','Ti porta sulla luna senza autista.','guida autonoma'],['Baby {T}','B{T}','Il figlio meme di {N}.','formato "baby"']],
 spazio:[['{N} Rocket','RCKT','Countdown continuo, decollo garantito (forse).','razzi / to the moon'],['Orbit {T}','ORBT','In orbita intorno al tuo portafoglio.','spazio'],['Astro Doge {T}','ADOGE','Doge con il casco da astronauta.','doge + spazio'],['Baby {T}','B{T}','Il figlio meme di {N}.','formato "baby"']],
 crypto:[['{N} Laser Eyes','LASER','Occhi laser on-chain.','cultura bitcoin'],['Saylor Moon {T}','SMOON','Compra, non vendere mai.','HODL'],['{T} Degen','DEGEN','Per chi ha già tutto in leva.','degen culture'],['Baby {T}','B{T}','Il figlio meme di {N}.','formato "baby"']],
 meme:[['Diamond Hands {T}','DH{T}','Mani di diamante dal 2021.','retail army'],['{N} Ape','APE{T}','Le scimmie non vendono.','apes together strong'],['{T} Squeeze','SQZ','Aspettando il prossimo squeeze.','short squeeze'],['Roaring {T}','ROAR','Il ruggito del retail.','Roaring Kitty vibe'],['Baby {T}','B{T}','Il figlio meme di {N}.','formato "baby"']],
 farma:[['{N} Pill','PILL','Una pillola verde al giorno.','farmaco/candela verde'],['Dr. {T}','DOC','Il dottore prescrive: HODL.','meme dottore'],['{T} Vax Frog','VFROG','La rana immunizzata dai ribassi.','animale + salute'],['Baby {T}','B{T}','Il figlio meme di {N}.','formato "baby"']],
 energia:[['{N} Reactor','REACT','Energia infinita, volatilità pure.','nucleare/energia'],['Power {T}','PWR','Ricarica il wallet.','energia'],['{T} Barrel Cat','BCAT','Un gatto dentro un barile.','animale + petrolio'],['Baby {T}','B{T}','Il figlio meme di {N}.','formato "baby"']],
 metalli:[['Golden {T}','GOLDN','Il lingotto dei meme.','bene rifugio'],['{T} Goblin','GOBLN','Il goblin che accumula metallo.','meme goblin'],['Shiny {T}','SHINY','Luccica sempre.','metallo prezioso'],['Baby {T}','B{T}','Il figlio meme di {N}.','formato "baby"']],
 indice:[['{T} Boomer','BOOMR','Il meme del boomer che compra l\'indice.','boomer vs degen'],['Index Chad {T}','CHAD','DCA, nessuno stress.','meme chad'],['{T} Couch Potato','COUCH','Investire dal divano.','passive investing'],['Baby {T}','B{T}','Il figlio meme di {T}.','formato "baby"']],
 consumo:[['{N} Cart','CART','Il carrello pieno di verde.','shopping'],['{T} Shopaholic','SHOPA','Compra tutto, anche il dip.','consumismo'],['{N} Hotdog','HDOG','Prezzo fisso, meme infinito.','iconico consumer'],['Baby {T}','B{T}','Il figlio meme di {N}.','formato "baby"']],
 quantum:[['Schrödinger {T}','SCHRO','Su e giù allo stesso tempo.','gatto di Schrödinger'],['Qubit {T}','QUBIT','Sovrapposizione di pump e dump.','quantum'],['{T} Entangled','ENTGL','Legato a te per sempre.','entanglement'],['Baby {T}','B{T}','Il figlio meme di {N}.','formato "baby"']],
 generico:[['{N} Inu','{T4}INU','L\'inu ufficioso di {N}.','formato inu collaudato'],['Baby {T}','B{T}','Il figlio meme di {N}.','formato "baby"'],['{T} Pepe','P{T}','Pepe ha comprato {T}.','meme classico'],['{N} Moon','{T4}MOON','Destinazione: luna.','to the moon'],['{T} Cat','{T4}CAT','Il gatto di {N}.','animale meme']]};
function settore(t){const T=(t.ticker||'').toUpperCase();for(const[k,v]of Object.entries(SETTORI))if(v.t.split(' ').includes(T))return k;for(const[k,v]of Object.entries(SETTORI))if(v.k.test(t.nome||''))return k;return 'generico'}
function suggerimenti(t){const T=(t.ticker||'X').toUpperCase().replace(/[^A-Z0-9]/g,''),N=(t.nome||T).replace(/,? (Inc|Corp|Corporation|Holdings|Ltd|Group|plc|Co)\.?$/i,'').split(/\s+/).slice(0,2).join(' ');
 const sub=s=>s.replaceAll('{N}',N).replaceAll('{T4}',T.slice(0,4)).replaceAll('{T}',T),s=settore(t),out=[],seen=new Set();
 for(const[n,tk,d,a]of TEMI[s].concat(TEMI.generico)){const x={nome:sub(n),ticker:sub(tk).slice(0,10),descrizione:sub(d),angolo:sub(a)};if(seen.has(x.ticker))continue;seen.add(x.ticker);out.push(x);if(out.length>=5)break}
 return {settore:s,lista:out}}
