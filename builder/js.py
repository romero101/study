# -*- coding: utf-8 -*-
"""Весь JS лендинга: ~4 КБ, без библиотек, грузится с defer в конце body."""

JS = r"""
(function(){
"use strict";
var CFG = __CFG__;

/* ---------- аналитика: единая точка, работает и без счётчиков ---------- */
function track(goal, params){
  try{
    if(CFG.ym && window.ym) window.ym(CFG.ym,'reachGoal',goal,params||{});
    if(window.gtag) window.gtag('event',goal,params||{});
    (window.dataLayer=window.dataLayer||[]).push(Object.assign({event:goal},params||{}));
  }catch(e){}
}
window.__track = track;

/* Метрика подключается лениво — после первого действия или 4 с простоя,
   чтобы не портить LCP/TBT на мобильном. */
var mLoaded=false;
function loadMetrika(){
  if(mLoaded||!CFG.ym) return; mLoaded=true;
  window.ym=window.ym||function(){(window.ym.a=window.ym.a||[]).push(arguments)};
  window.ym.l=+new Date();
  var s=document.createElement('script');
  s.src='https://mc.yandex.ru/metrika/tag.js'; s.async=true;
  document.head.appendChild(s);
  window.ym(CFG.ym,'init',{clickmap:true,trackLinks:true,accurateTrackBounce:true,webvisor:true});
}
['pointerdown','keydown','touchstart','scroll'].forEach(function(ev){
  window.addEventListener(ev,loadMetrika,{once:true,passive:true});
});
setTimeout(loadMetrika,4000);

/* ---------- клики по телефону и мессенджерам ---------- */
document.addEventListener('click',function(e){
  var a=e.target.closest('a'); if(!a) return;
  var h=a.getAttribute('href')||'';
  if(h.indexOf('tel:')===0) track('call_click',{place:a.dataset.place||'page'});
  else if(h.indexOf('wa.me')>-1||h.indexOf('whatsapp')>-1) track('wa_click',{place:a.dataset.place||'page'});
  else if(h.indexOf('t.me')>-1) track('tg_click',{place:a.dataset.place||'page'});
  else if(h.indexOf('mailto:')===0) track('mail_click');
},{passive:true});

/* ---------- маска телефона ---------- */
function maskPhone(el){
  el.addEventListener('input',function(){
    var d=el.value.replace(/\D/g,'');
    if(d[0]==='8') d='7'+d.slice(1);
    if(d[0]!=='7') d='7'+d;
    d=d.slice(0,11);
    var o='+7';
    if(d.length>1) o+=' ('+d.slice(1,4);
    if(d.length>=5) o+=') '+d.slice(4,7);
    if(d.length>=8) o+='-'+d.slice(7,9);
    if(d.length>=10) o+='-'+d.slice(9,11);
    el.value=o;
    el.setAttribute('aria-invalid','false');
  });
  el.addEventListener('focus',function(){ if(!el.value) el.value='+7 ('; });
}
function validPhone(v){ return v.replace(/\D/g,'').length===11; }
document.querySelectorAll('input[type=tel]').forEach(maskPhone);

/* ---------- деньги ---------- */
function money(n){ return new Intl.NumberFormat('ru-RU').format(Math.round(n))+' ₽'; }

/* ---------- калькулятор: цена ДО запроса контактов ---------- */
var calc=document.getElementById('calc');
if(calc){
  var depth=calc.querySelector('#c-depth');
  var depthOut=calc.querySelector('#c-depth-out');
  var sumOut=calc.querySelector('#c-sum');
  var brk=calc.querySelector('#c-break');
  var started=false;
  function recalc(){
    var m=+depth.value;
    var kind=calc.querySelector('input[name=kind]:checked');
    var extra=[].slice.call(calc.querySelectorAll('input[name=extra]:checked'));
    var rate=+(kind?kind.dataset.rate:CFG.calc.baseRate);
    var drill=m*rate;
    var rows=[[ (kind?kind.dataset.label:'Бурение')+', '+m+' м × '+money(rate)+'/м', drill ]];
    var total=drill;
    extra.forEach(function(x){
      var v=+x.dataset.price||0;
      // проценты помечаются data-pct
      if(x.dataset.pct) v=drill*(+x.dataset.pct/100);
      rows.push([x.dataset.label,v]); total+=v;
    });
    sumOut.textContent='от '+money(total);
    brk.innerHTML=rows.map(function(r){
      return '<li><span>'+r[0]+'</span><b>'+money(r[1])+'</b></li>';
    }).join('');
    calc.querySelectorAll('[data-calc-carry]').forEach(function(f){
      f.value=sumOut.textContent+' — '+rows.map(function(r){return r[0]}).join('; ');
    });
    if(depthOut) depthOut.textContent=m+' м';
    if(!started){ started=true; track('calc_start'); }
  }
  calc.addEventListener('input',recalc);
  calc.addEventListener('change',recalc);
  recalc();
  // «досчитал» = дошёл до результата и задержался
  var done=false;
  calc.addEventListener('pointerup',function(){
    if(done) return; done=true;
    setTimeout(function(){ track('calc_complete',{sum:sumOut.textContent}); },600);
  });
}

/* ---------- квиз: телефон только на последнем шаге ---------- */
var quiz=document.getElementById('quiz');
if(quiz){
  var steps=[].slice.call(quiz.querySelectorAll('.quiz__step'));
  var bar=quiz.querySelector('.quiz__bar i');
  var cnt=quiz.querySelector('.quiz__cnt');
  var i=0, answers=[];
  function show(n){
    steps.forEach(function(s,k){ s.hidden = k!==n; });
    bar.style.width=Math.round((n+1)/steps.length*100)+'%';
    cnt.textContent='Шаг '+(n+1)+' из '+steps.length;
    i=n;
    var f=steps[n].querySelector('input,button');
    if(f && n>0) try{ f.focus({preventScroll:true}); }catch(e){}
  }
  quiz.addEventListener('click',function(e){
    var nx=e.target.closest('[data-next]');
    if(nx){
      var cur=steps[i];
      var picked=cur.querySelector('input[type=radio]:checked');
      if(picked) answers.push((cur.dataset.q||'')+': '+picked.dataset.label);
      if(i===0) track('quiz_start');
      if(i<steps.length-1) show(i+1);
      quiz.querySelectorAll('[data-quiz-carry]').forEach(function(f){ f.value=answers.join(' | '); });
    }
    var bk=e.target.closest('.quiz__back');
    if(bk){ answers.pop(); show(Math.max(0,i-1)); }
  });
  show(0);
}

/* ---------- отправка форм ---------- */
document.querySelectorAll('form[data-lead]').forEach(function(form){
  var msg=form.querySelector('.formmsg');
  var btn=form.querySelector('button[type=submit]');
  form.dataset.t0=Date.now();
  form.addEventListener('submit',function(e){
    e.preventDefault();
    var tel=form.querySelector('input[type=tel]');
    if(tel && !validPhone(tel.value)){
      tel.setAttribute('aria-invalid','true'); tel.focus();
      return;
    }
    // антиспам: скрытое поле + слишком быстрая отправка
    var hp=form.querySelector('input[name=_gotcha]');
    if(hp && hp.value) return;
    var fd=new FormData(form);
    fd.append('_page', location.href);
    fd.append('_form', form.dataset.lead);
    fd.append('_elapsed', String(Math.round((Date.now()-+form.dataset.t0)/1000)));
    var label=btn?btn.textContent:'';
    // витрина без backend: показываем, что произойдёт, вместо ложной ошибки
    if(!CFG.endpoint){
      form.reset();
      if(msg){ msg.className='formmsg formmsg--ok';
        msg.textContent='Демонстрация: на рабочем сайте заявка уходит в Telegram и на почту за секунды.'; }
      track('form_submit',{form:form.dataset.lead,demo:1});
      return;
    }
    if(btn){ btn.disabled=true; btn.textContent='Отправляем…'; }
    fetch(CFG.endpoint,{method:'POST',body:fd})
      .then(function(r){ return r.ok?r.json().catch(function(){return{ok:true}}):Promise.reject(r.status); })
      .then(function(){
        form.reset();
        if(msg){ msg.className='formmsg formmsg--ok'; msg.textContent=CFG.okText; }
        track('form_submit',{form:form.dataset.lead});
      })
      .catch(function(){
        // канал недоступен — не теряем заявку: уводим в WhatsApp с заполненным текстом
        if(msg){
          msg.className='formmsg formmsg--err';
          msg.innerHTML='Не удалось отправить через сайт. '+
            '<a href="'+CFG.wa+'?text='+encodeURIComponent(leadText(fd))+'">Отправить в WhatsApp</a>'+
            ' или позвоните <a href="tel:'+CFG.telRaw+'">'+CFG.telText+'</a>.';
        }
        track('form_error',{form:form.dataset.lead});
      })
      .finally(function(){ if(btn){ btn.disabled=false; btn.textContent=label; } });
  });
});
function leadText(fd){
  var out=[];
  fd.forEach(function(v,k){ if(k[0]!=='_' && v) out.push(k+': '+v); });
  return 'Заявка с сайта. '+out.join('. ');
}

/* ---------- FAQ: отчёт о раскрытии, полезно для правки текстов ---------- */
document.querySelectorAll('.faq details').forEach(function(d){
  d.addEventListener('toggle',function(){ if(d.open) track('faq_open',{q:(d.querySelector('summary')||{}).textContent}); });
});

/* ---------- скролл-глубина: показывает, где отваливаются ---------- */
var marks={25:0,50:0,75:0,100:0};
window.addEventListener('scroll',function(){
  var h=document.documentElement;
  var p=(h.scrollTop+window.innerHeight)/h.scrollHeight*100;
  Object.keys(marks).forEach(function(m){
    if(!marks[m] && p>=+m){ marks[m]=1; track('scroll_'+m); }
  });
},{passive:true});
})();
"""
