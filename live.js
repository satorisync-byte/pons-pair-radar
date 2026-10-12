// Rilevamento in pagina: ricarica data.json ogni 60 s; se compare un nuovo pair approvato o un nuovo token Robinhood
// cambia il titolo della scheda, mostra un banner e (se attivato) emette un suono. Nessuna notifica esterna.
(function(){
  const base=document.title, known=new Set((window.PONS_DATA?.token||[]).filter(t=>t.stato==='pons').map(t=>t.indirizzo)),
        knownRh=new Set((window.PONS_DATA?.token||[]).filter(t=>t.robinhood).map(t=>t.indirizzo));
  let unseen=0;const SK='pons_suono_v1';
  const bar=document.createElement('div');bar.id='livebar';bar.innerHTML='<label class="mut" style="display:flex;align-items:center;gap:8px;min-height:44px"><input type="checkbox" id="snd" style="width:22px;height:22px;min-height:0"> 🔊 Suono quando appare un nuovo pair (pagina aperta)</label><div id="livemsg"></div>';
  document.querySelector('main').prepend(bar);
  const snd=document.getElementById('snd');snd.checked=localStorage.getItem(SK)==='1';snd.onchange=()=>{localStorage.setItem(SK,snd.checked?'1':'0');if(snd.checked)beep()};
  function beep(){try{const c=new (window.AudioContext||window.webkitAudioContext)();[0,0.18,0.36].forEach((t,i)=>{const o=c.createOscillator(),g=c.createGain();o.frequency.value=660+i*220;o.connect(g);g.connect(c.destination);g.gain.setValueAtTime(0.15,c.currentTime+t);g.gain.exponentialRampToValueAtTime(0.001,c.currentTime+t+0.16);o.start(c.currentTime+t);o.stop(c.currentTime+t+0.17)})}catch(e){}}
  document.addEventListener('visibilitychange',()=>{if(!document.hidden&&unseen){unseen=0;document.title=base}});
  async function poll(){if(location.protocol==='file:')return;
    try{const d=await (await fetch('data.json?t='+Date.now(),{cache:'no-store'})).json();
      const nuoviP=d.token.filter(t=>t.stato==='pons'&&!known.has(t.indirizzo)), nuoviR=d.token.filter(t=>t.robinhood&&!knownRh.has(t.indirizzo));
      nuoviP.forEach(t=>known.add(t.indirizzo));nuoviR.forEach(t=>knownRh.add(t.indirizzo));
      if(nuoviP.length||nuoviR.length){unseen+=nuoviP.length+nuoviR.length;document.title=`(${unseen}) 🆕 ${nuoviP.length?'Nuovo pair Pons: '+nuoviP.map(t=>t.ticker).join(', '):'Nuovo token Robinhood'} · `+base;
        const m=document.getElementById('livemsg');m.innerHTML=`<div class="warn" style="border-color:#2ea043;background:#0f3d1f">🆕 ${nuoviP.map(t=>'<b>'+t.ticker+'</b> approvato su Pons').concat(nuoviR.map(t=>'<b>'+t.ticker+'</b> nuovo su Robinhood')).join(' · ')} — <a href="" onclick="location.reload();return false">ricarica la pagina</a> · <a href="https://ponsfamily.com/launchpad" target="_blank" rel="noopener">Pons</a></div>`+m.innerHTML;
        if(snd.checked&&nuoviP.length)beep()}}catch(e){}}
  setInterval(poll,60000);
})();
