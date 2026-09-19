(function(){
  var rub=function(n){return Math.round(n).toLocaleString('ru-RU')+' ₽';};
  var $=function(id){return document.getElementById(id);};

  /* форма заявки — та же логика, что на главной */
  var form=$('lead-form');
  if(form){
    var opened=Date.now(),status=$('form-status'),phone=$('phone');
    var fmt=function(v){var d=v.replace(/\D/g,'');if(!d)return'';if(d[0]==='8')d='7'+d.slice(1);if(d[0]!=='7')d='7'+d;d=d.slice(0,11);var s='+7';if(d.length>1)s+=' ('+d.slice(1,4);if(d.length>=5)s+=') '+d.slice(4,7);if(d.length>=8)s+='-'+d.slice(7,9);if(d.length>=10)s+='-'+d.slice(9,11);return s;};
    phone.addEventListener('input',function(){var end=phone.selectionStart===phone.value.length,next=fmt(phone.value);if(end||next.length<phone.value.length)phone.value=next;});
    var say=function(kind,text){status.className=kind;status.textContent=text;};
    form.addEventListener('submit',function(e){
      e.preventDefault();
      if(phone.value.replace(/\D/g,'').length!==11){say('bad','Введите номер полностью: +7 и 10 цифр.');phone.focus();return;}
      var data=new FormData(form),button=form.querySelector('[type=submit]');
      data.append('_elapsed',String(Math.round((Date.now()-opened)/1000)));
      button.disabled=true;say('','');
      fetch('/send.php',{method:'POST',body:data}).then(function(r){return r.json().then(function(j){if(!r.ok||!j.ok)throw new Error();});})
        .then(function(){form.reset();say('ok','Заявка принята. Перезвоним в ближайший рабочий день.');})
        .catch(function(){say('bad','Не получилось отправить. Проверьте интернет и нажмите ещё раз — данные в форме сохранились.');})
        .then(function(){button.disabled=false;});
    });
  }
  /* кнопка под виджетом переносит расчёт в поле «Задача» */
  function carry(btn,text){
    if(!btn)return;
    btn.addEventListener('click',function(){var m=$('message');if(m)m.value=text();});
  }

  /* цена заявки: сколько стоит заявка сейчас и сколько будет при другой конверсии сайта */
  if($('cpl')){
    var cplText='';
    var cpl=function(){
      var budget=+$('cpl-budget').value||0,clicks=+$('cpl-clicks').value||0,leads=+$('cpl-leads').value||0,
          deal=(+$('cpl-deal').value||0)/100,target=+$('cpl-target').value;
      var cr=clicks?leads/clicks*100:0;
      $('cpl-target-out').textContent=target.toFixed(1).replace('.',',')+'%';
      $('cpl-cr').textContent=cr?cr.toFixed(1).replace('.',',')+'%':'—';
      $('cpl-now').textContent=leads?rub(budget/leads):'—';
      $('cpl-client').textContent=leads&&deal?rub(budget/(leads*deal)):'—';
      var newLeads=clicks*target/100;
      $('cpl-new-leads').textContent=clicks?Math.round(newLeads)+' в месяц':'—';
      $('cpl-new').textContent=newLeads?rub(budget/newLeads):'—';
      var diff=Math.round(newLeads-leads);
      $('cpl-verdict').textContent=!clicks||!leads?'Заполните расход, клики и заявки — посчитаем.':
        diff>0?'Те же '+rub(budget)+' в месяц, но на '+diff+' заявок больше. Реклама не менялась — изменился только сайт.':
        'У вашего сайта конверсия уже не ниже выбранной. Узкое место, скорее всего, в самой рекламе — посмотрим кампании.';
      cplText='Считал на сайте: бюджет '+rub(budget)+', кликов '+clicks+', заявок '+leads+', конверсия сайта '+cr.toFixed(1)+'%.';
    };
    ['cpl-budget','cpl-clicks','cpl-leads','cpl-deal','cpl-target'].forEach(function(id){$(id).addEventListener('input',cpl);});
    cpl();carry($('cpl-go'),function(){return cplText;});
  }

  /* пример калькулятора: забор */
  if($('ex')){
    var exText='';
    var ex=function(){
      var rate=+$('ex-type').value,len=+$('ex-len').value,sum=rate*len;
      if($('ex-gate').checked)sum+=38000;
      if($('ex-wicket').checked)sum+=14000;
      $('ex-len-out').textContent=len+' м';
      $('ex-sum').textContent='≈ '+rub(sum);
      $('ex-per').textContent=rub(sum/len)+' за метр с учётом ворот и калитки';
      exText='Хочу такой калькулятор на свой сайт. Смотрел пример: '+$('ex-type').selectedOptions[0].text+', '+len+' м.';
    };
    ['ex-type','ex-len','ex-gate','ex-wicket'].forEach(function(id){$(id).addEventListener('input',ex);});
    ex();carry($('ex-go'),function(){return exText;});
  }

  /* пример квиза: три вопроса, телефон — только в конце */
  if($('qz')){
    var steps=[
      {q:'Что нужно сделать?',a:['Скважину на воду','Септик','Забор','Кровлю']},
      {q:'Что с участком?',a:['Дом уже стоит','Идёт стройка','Пока только участок']},
      {q:'Когда планируете работы?',a:['В этом месяце','В этом сезоне','Пока прицениваюсь']}
    ],pick=[],box=$('qz-body'),bar=$('qz-bar');
    var draw=function(){
      var i=pick.length;
      bar.style.width=(i/steps.length*100)+'%';
      if(i<steps.length){
        box.innerHTML='<p class="qz-step">Вопрос '+(i+1)+' из '+steps.length+'</p><h3>'+steps[i].q+'</h3><div class="qz-opts">'+
          steps[i].a.map(function(t){return '<button type="button">'+t+'</button>';}).join('')+'</div>';
        box.querySelectorAll('button').forEach(function(b){b.addEventListener('click',function(){pick.push(b.textContent);draw();});});
      }else{
        box.innerHTML='<p class="qz-step">Готово</p><h3>Вот здесь — и только здесь — квиз просит телефон.</h3>'+
          '<p>Человек уже ответил на три вопроса и ждёт результат, поэтому номер оставляет охотнее, чем в форме на первом экране. А вы получаете заявку с ответами: «'+pick.join(' · ')+'».</p>'+
          '<div class="qz-opts"><a class="button button--sm" href="#request" id="qz-go">Хочу такой квиз</a><button type="button" id="qz-again">Пройти ещё раз</button></div>';
        $('qz-again').addEventListener('click',function(){pick=[];draw();});
        carry($('qz-go'),function(){return 'Хочу квиз на свой сайт. В примере выбрал: '+pick.join(', ')+'.';});
      }
    };
    draw();
  }
})();
