# -*- coding: utf-8 -*-
"""Критический CSS лендинга. Встраивается в <head> целиком — ни одного
блокирующего запроса. Токены __ACCENT__ и т.п. подставляет build.py."""

CSS = r"""
*,*::before,*::after{box-sizing:border-box}
html{-webkit-text-size-adjust:100%;scroll-behavior:smooth}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}
*,*::before,*::after{animation-duration:.01ms!important;transition-duration:.01ms!important}}
body{margin:0;font:400 17px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
color:#16202b;background:#fff;text-rendering:optimizeLegibility}
img,svg{max-width:100%;height:auto;display:block}
a{color:__ACCENT_DK__}
h1,h2,h3{margin:0 0 .5em;line-height:1.18;letter-spacing:-.02em;font-weight:800}
h1{font-size:clamp(28px,6.4vw,50px)}
h2{font-size:clamp(24px,4.6vw,36px)}
h3{font-size:clamp(18px,2.6vw,21px);font-weight:700}
p{margin:0 0 1em}
:focus-visible{outline:3px solid __ACCENT__;outline-offset:2px;border-radius:4px}
.wrap{width:100%;max-width:1140px;margin:0 auto;padding-inline:20px}
.sec{padding-block:clamp(44px,7vw,84px)}
.sec--alt{background:__TINT__}
.lead{font-size:clamp(17px,2.2vw,20px);color:#42505f;max-width:62ch}
.eyebrow{display:inline-block;font-size:13px;font-weight:700;letter-spacing:.09em;text-transform:uppercase;
color:__ACCENT_DK__;background:__TINT2__;padding:6px 12px;border-radius:99px;margin-bottom:14px}
.skip{position:absolute;left:-9999px}
.skip:focus{left:12px;top:12px;z-index:99;background:#fff;padding:12px 18px;border-radius:8px;box-shadow:0 6px 24px rgba(0,0,0,.2)}

/* ---------- кнопки: тач-таргет >=48px, контраст AA ---------- */
.btn{display:inline-flex;align-items:center;justify-content:center;gap:9px;min-height:54px;padding:14px 26px;
border-radius:12px;font-size:17px;font-weight:700;text-decoration:none;border:2px solid transparent;cursor:pointer;
font-family:inherit;transition:transform .12s,box-shadow .12s,background .12s;white-space:nowrap}
.btn:active{transform:translateY(1px)}
.btn--main{background:__CTA__;color:#fff;box-shadow:0 6px 18px __CTA_SH__}
.btn--main:hover{background:__CTA_DK__}
.btn--ghost{background:#fff;color:__ACCENT_DK__;border-color:__BORDER__}
.btn--ghost:hover{background:__TINT__}
.btn--wide{width:100%}
.btn--wa{background:#25a24a;color:#fff}
.btn--wa:hover{background:#1d8a3d}
.btn-row{display:flex;flex-wrap:wrap;gap:12px;margin-top:26px}
@media (max-width:520px){.btn-row{flex-direction:column}.btn{width:100%}}

/* ---------- шапка ---------- */
.hdr{position:sticky;top:env(safe-area-inset-top,0px);z-index:40;background:rgba(255,255,255,.94);backdrop-filter:blur(8px);
border-bottom:1px solid __BORDER__}
.hdr__in{display:flex;align-items:center;gap:18px;min-height:66px}
.logo{display:flex;align-items:center;gap:10px;min-height:44px;font-weight:800;font-size:19px;color:#16202b;text-decoration:none;letter-spacing:-.03em;white-space:nowrap}
@media (max-width:420px){.logo{font-size:16px;gap:7px}.logo svg{width:22px;height:22px}.hdr__tel b{font-size:16.5px}}
.logo svg{flex:0 0 auto}
.nav{display:none;margin-left:auto;gap:22px}
.nav a{color:#42505f;text-decoration:none;font-size:15.5px;font-weight:600}
.nav a:hover{color:__ACCENT_DK__}
.hdr__tel{margin-left:auto;display:flex;flex-direction:column;align-items:flex-end;justify-content:center;min-height:46px;padding-left:8px;text-decoration:none;color:#16202b}
.hdr__tel b{font-size:18px;font-weight:800;letter-spacing:-.01em;white-space:nowrap}
.hdr__tel span{font-size:12.5px;color:#6a7686}
.hdr .btn{display:none}
@media (min-width:900px){.nav{display:flex}.hdr__tel{margin-left:24px}.hdr .btn{display:inline-flex;min-height:46px;padding:10px 20px;font-size:15.5px}}
@media (max-width:899px){.hdr__tel span{display:none}}

/* ---------- первый экран ---------- */
.hero{position:relative;background:linear-gradient(170deg,__HERO_A__ 0%,__HERO_B__ 100%);color:#fff;overflow:hidden}
.hero__grid{display:grid;gap:30px;padding-block:clamp(34px,5vw,64px)}
.hero h1{color:#fff}
.hero .lead{color:rgba(255,255,255,.88)}
.price-anchor{display:inline-flex;align-items:baseline;gap:10px;background:rgba(255,255,255,.14);
border:1px solid rgba(255,255,255,.26);border-radius:14px;padding:12px 18px;margin:4px 0 6px}
.price-anchor b{font-size:clamp(24px,4.4vw,32px);font-weight:800;letter-spacing:-.02em;white-space:nowrap}
.price-anchor span{font-size:14px;color:rgba(255,255,255,.82)}
@media (max-width:560px){.price-anchor{flex-direction:column;align-items:flex-start;gap:2px}}
.trust{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin-top:28px;padding:0;list-style:none}
.trust li{display:flex;gap:9px;align-items:flex-start;font-size:14.5px;line-height:1.35;color:rgba(255,255,255,.93)}
.trust svg{flex:0 0 auto;margin-top:1px}
.hero-media{position:relative;border-radius:18px;overflow:hidden;background:
linear-gradient(135deg,rgba(255,255,255,.22),rgba(255,255,255,.06));aspect-ratio:4/3;box-shadow:0 18px 44px rgba(0,0,0,.26)}
.hero-media img{width:100%;height:100%;object-fit:cover}
.hero-media.no-img img{display:none}
.hero-media.no-img::after{content:"фото объекта";position:absolute;inset:0;display:grid;place-items:center;
font-size:14px;color:rgba(255,255,255,.7)}
@media (min-width:900px){.hero__grid{grid-template-columns:1.05fr .95fr;align-items:center;gap:52px}
.trust{grid-template-columns:repeat(2,1fr)}}
@media (max-width:480px){.trust{grid-template-columns:1fr}}

/* ---------- калькулятор ---------- */
.calc{background:#fff;border:1px solid __BORDER__;border-radius:18px;padding:clamp(20px,3.4vw,32px);
box-shadow:0 10px 34px rgba(16,32,48,.07)}
.calc__row{margin-bottom:22px}
.calc__lab{display:flex;justify-content:space-between;align-items:baseline;gap:12px;font-weight:700;margin-bottom:10px;font-size:16px}
.calc__val{font-variant-numeric:tabular-nums;color:__ACCENT_DK__;font-size:19px;font-weight:800}
input[type=range]{width:100%;height:40px;accent-color:__CTA__;background:transparent;cursor:pointer}
.chips{display:flex;flex-wrap:wrap;gap:10px}
.chip{position:relative}
.chip input{position:absolute;opacity:0;width:1px;height:1px}
.chip span{display:block;min-height:48px;display:flex;align-items:center;padding:12px 18px;border:2px solid __BORDER__;
border-radius:12px;font-weight:600;font-size:15.5px;cursor:pointer;background:#fff;transition:border-color .12s,background .12s}
.nw{white-space:nowrap;font-style:normal}
.chip input:checked+span{border-color:__CTA__;background:__TINT2__;color:__ACCENT_DK__}
.chip input:focus-visible+span{outline:3px solid __ACCENT__;outline-offset:2px}
.calc__out{margin-top:8px;padding:20px;border-radius:14px;background:__TINT2__;border:1px dashed __ACCENT__}
.calc__sum{font-size:clamp(28px,5.4vw,40px);font-weight:800;letter-spacing:-.025em;color:__ACCENT_DK__;
font-variant-numeric:tabular-nums;line-height:1.1}
.calc__note{font-size:13.5px;color:#5a6875;margin:8px 0 0}
.calc__break{margin:14px 0 0;padding:0;list-style:none;font-size:14.5px;color:#42505f}
.calc__break li{display:flex;justify-content:space-between;gap:14px;padding:7px 0;border-bottom:1px solid __BORDER__}
.calc__break li:last-child{border:0}
.calc__break b{font-variant-numeric:tabular-nums;white-space:nowrap}

/* ---------- карточки ---------- */
.cards{display:grid;gap:18px;grid-template-columns:1fr}
@media (min-width:700px){.cards{grid-template-columns:repeat(2,1fr)}}
@media (min-width:1000px){.cards--3{grid-template-columns:repeat(3,1fr)}}
.card{background:#fff;border:1px solid __BORDER__;border-radius:16px;padding:24px;display:flex;flex-direction:column}
.card__scheme{margin:-4px 0 16px}
.card__price{margin-top:auto;padding-top:16px;font-weight:800;font-size:19px;color:__ACCENT_DK__}
.card ul{margin:0 0 14px;padding-left:20px;color:#42505f;font-size:15.5px}
.card li{margin-bottom:6px}

/* ---------- этапы ---------- */
.steps{counter-reset:s;list-style:none;margin:0;padding:0;display:grid;gap:14px}
@media (min-width:860px){.steps{grid-template-columns:repeat(5,1fr)}}
.steps li{counter-increment:s;position:relative;background:#fff;border:1px solid __BORDER__;border-radius:14px;padding:22px 18px 18px}
.steps li::before{content:counter(s);position:absolute;top:-13px;left:18px;width:28px;height:28px;border-radius:50%;
background:__CTA__;color:#fff;display:grid;place-items:center;font-size:14px;font-weight:800}
.steps b{display:block;margin-bottom:5px;font-size:16px}
.steps span{font-size:14.5px;color:#54616f;line-height:1.45}

/* ---------- галерея ---------- */
.gal{display:grid;gap:12px;grid-template-columns:repeat(2,1fr)}
@media (min-width:820px){.gal{grid-template-columns:repeat(3,1fr)}.gal figure:first-child{grid-column:span 2;grid-row:span 2}}
.gal figure{margin:0;position:relative;border-radius:14px;overflow:hidden;background:__TINT__;aspect-ratio:4/3}
.gal figure:first-child{aspect-ratio:auto;min-height:220px}
.gal img{width:100%;height:100%;object-fit:cover}
.gal figcaption{position:absolute;left:0;right:0;bottom:0;padding:22px 14px 11px;color:#fff;font-size:13.5px;
background:linear-gradient(transparent,rgba(8,16,24,.82))}

/* ---------- отзывы ---------- */
.rev{background:#fff;border:1px solid __BORDER__;border-radius:16px;padding:24px}
.rev blockquote{margin:0 0 14px;font-size:16.5px;line-height:1.55;color:#22303d}
.rev figcaption{font-size:14px;color:#6a7686}
.rev figcaption b{color:#16202b;display:block;font-size:15px}
.src{display:inline-flex;align-items:center;gap:6px;margin-top:18px;font-size:14px}

/* ---------- квиз ---------- */
.quiz{background:#fff;border:1px solid __BORDER__;border-radius:18px;padding:clamp(20px,3.4vw,32px);
box-shadow:0 10px 34px rgba(16,32,48,.07);max-width:660px;margin-inline:auto}
.quiz__bar{height:6px;border-radius:99px;background:__BORDER__;overflow:hidden;margin-bottom:8px}
.quiz__bar i{display:block;height:100%;background:__CTA__;width:25%;transition:width .25s}
.quiz__cnt{font-size:13px;color:#6a7686;margin-bottom:18px}
.quiz__step[hidden]{display:none}
.quiz__nav{display:flex;gap:12px;margin-top:22px;flex-wrap:wrap}
.quiz__back{background:none;border:0;color:#6a7686;font:inherit;font-weight:600;cursor:pointer;min-height:48px;padding:0 6px}

/* ---------- формы ---------- */
.fld{margin-bottom:16px}
.fld label{display:block;font-weight:700;margin-bottom:7px;font-size:15.5px}
.fld input,.fld textarea{width:100%;min-height:54px;padding:14px 16px;border:2px solid __BORDER__;border-radius:12px;
font:inherit;font-size:17px;background:#fff;color:#16202b}
.fld textarea{min-height:96px;resize:vertical}
.fld input:focus,.fld textarea:focus{outline:none;border-color:__CTA__}
.fld input[aria-invalid=true]{border-color:#d33a2c;background:#fff6f5}
.fld .err{display:none;color:#c02b1d;font-size:14px;margin-top:6px;font-weight:600}
.fld input[aria-invalid=true]~.err{display:block}
.hp{position:absolute;left:-9999px;width:1px;height:1px;overflow:hidden}
.consent{font-size:13px;color:#6a7686;margin:14px 0 0}
.consent a{color:#6a7686}
.formmsg{margin-top:16px;padding:16px 18px;border-radius:12px;font-weight:600;display:none}
.formmsg--ok{display:block;background:#e9f8ee;border:1px solid #9bd8ae;color:#166534}
.formmsg--err{display:block;background:#fff1f0;border:1px solid #f0b3ac;color:#9e2114}

/* ---------- FAQ ---------- */
.faq{max-width:820px}
.faq details{border:1px solid __BORDER__;border-radius:12px;margin-bottom:10px;background:#fff}
.faq summary{padding:17px 52px 17px 20px;font-weight:700;cursor:pointer;position:relative;list-style:none;min-height:56px;
display:flex;align-items:center;font-size:16.5px}
.faq summary::-webkit-details-marker{display:none}
.faq summary::after{content:"";position:absolute;right:20px;top:50%;width:11px;height:11px;margin-top:-6px;
border-right:2.5px solid __ACCENT_DK__;border-bottom:2.5px solid __ACCENT_DK__;transform:rotate(45deg);transition:transform .18s}
.faq details[open] summary::after{transform:rotate(-135deg);margin-top:-2px}
.faq .faq__a{padding:0 20px 18px;color:#42505f}

/* ---------- контакты / подвал ---------- */
.contacts{display:grid;gap:26px}
@media (min-width:860px){.contacts{grid-template-columns:1fr 1fr}}
.dl{margin:0;display:grid;gap:14px}
.dl div{display:flex;gap:12px;align-items:flex-start}
.dl dt{font-size:14px;color:#6a7686;min-width:96px}
.dl dd{margin:0;font-weight:600}
.dl a{text-decoration:none;display:inline-flex;align-items:center;min-height:44px}
.ftr{background:#101a24;color:#9aa8b6;padding-block:34px;font-size:14.5px}
.ftr a{color:#cdd8e3;display:inline-flex;align-items:center;min-height:44px}
.ftr__in{display:grid;gap:14px}
@media (min-width:760px){.ftr__in{grid-template-columns:1.4fr 1fr;align-items:start}}

/* ---------- закреплённая мобильная панель: главный драйвер звонков ---------- */
.dock{position:fixed;left:0;right:0;bottom:0;z-index:50;display:flex;gap:8px;padding:8px 10px;
padding-bottom:calc(8px + env(safe-area-inset-bottom));background:rgba(255,255,255,.97);
border-top:1px solid __BORDER__;box-shadow:0 -6px 22px rgba(16,32,48,.12)}
.dock .btn{flex:1;min-height:52px;padding:12px 10px;font-size:16px;border-radius:11px}
@media (min-width:900px){.dock{display:none}}
@media (max-width:899px){body{padding-bottom:78px}}

/* ---------- демо-плашка: удалить одной строкой при запуске ---------- */
.demo{background:#fff6e0;border-bottom:1px solid #f0d79b;color:#6b4c07;font-size:13.5px;padding:9px 0;text-align:center}
.demo b{font-weight:800}

/* ниже первого экрана браузер может не считать раскладку заранее */
.sec--lazy{content-visibility:auto;contain-intrinsic-size:auto 640px}
"""
