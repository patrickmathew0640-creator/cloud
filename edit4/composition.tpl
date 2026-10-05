<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="assets/gsap.min.js"></script>
    <style>
      @font-face { font-family: "Noto Color Emoji"; src: local("Noto Color Emoji"); }
      @font-face { font-family: "Poppins"; font-weight: 500; src: url("assets/fonts/poppins-latin-500-normal.woff2") format("woff2"); }
      @font-face { font-family: "Poppins"; font-weight: 700; src: url("assets/fonts/poppins-latin-700-normal.woff2") format("woff2"); }
      @font-face { font-family: "Poppins"; font-weight: 800; src: url("assets/fonts/poppins-latin-800-normal.woff2") format("woff2"); }
      @font-face { font-family: "Poppins"; font-weight: 900; src: url("assets/fonts/poppins-latin-900-normal.woff2") format("woff2"); }
      :root { --gold: #f2c811; --gold2: #ffe680; --ink: #08090c; --navy: #0d1430; --blue: #2563eb; --sky: #38bdf8;
              --claude: #d97757; --green: #22c55e; --red: #ef4444; }
      * { margin: 0; padding: 0; box-sizing: border-box; }
      html, body { width: 1080px; height: 1920px; overflow: hidden; background: var(--ink); }
      #root { position: relative; width: 1080px; height: 1920px; overflow: hidden; color: #fff;
              font-family: "Poppins", "Noto Color Emoji", sans-serif; }
      .g { position: absolute; }

      /* ---------- footage ---------- */
      #spk { position: absolute; inset: 0; overflow: hidden; z-index: 1; }
      #spkv { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; object-fit: cover; }
      #vig { position: absolute; inset: 0; z-index: 2; pointer-events: none;
             background: radial-gradient(ellipse at 50% 42%, rgba(0,0,0,0) 58%, rgba(0,0,0,.38) 100%),
                         linear-gradient(180deg, rgba(0,0,0,.18) 0%, rgba(0,0,0,0) 14%, rgba(0,0,0,0) 66%, rgba(0,0,0,.5) 100%); }

      /* ---------- shared bits ---------- */
      .glass { background: rgba(10,14,32,.78); border: 2px solid rgba(255,255,255,.14); border-radius: 36px;
               box-shadow: 0 24px 60px rgba(0,0,0,.45), inset 0 1px 0 rgba(255,255,255,.12); }
      .kick { font-size: 28px; font-weight: 800; letter-spacing: .2em; text-transform: uppercase; }
      .lock { display: flex; align-items: center; justify-content: center; gap: 18px; }
      .tile { width: 220px; height: 200px; border-radius: 32px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 10px;
              font-size: 32px; font-weight: 800; box-shadow: 0 16px 40px rgba(0,0,0,.4); }
      .tile i { width: 92px; height: 92px; display: flex; align-items: center; justify-content: center; font-style: normal; }
      .tile i svg { width: 100%; height: 100%; }
      .tile.cl { background: linear-gradient(160deg, #e8875f, #c4603f); }
      .tile.mc { background: linear-gradient(160deg, #2b3a7a, #141c45); border: 3px solid rgba(56,189,248,.7); }
      .tile.pb { background: linear-gradient(160deg, #ffe066, #f2c811); color: #1a1400; }
      .mcpi { font-size: 50px; font-weight: 900; color: var(--sky); letter-spacing: .02em; }
      .lock .plus { font-size: 64px; font-weight: 900; color: var(--gold); text-shadow: 0 4px 0 rgba(0,0,0,.4); }

      /* ---------- brand bug ---------- */
      #brand { position: absolute; left: 36px; top: 62px; z-index: 12; display: flex; align-items: center; gap: 14px; padding: 10px 24px 10px 12px;
               border-radius: 999px; background: rgba(8,9,12,.62); border: 2px solid rgba(242,200,17,.55); font-size: 26px; font-weight: 800; }
      #brand i { width: 46px; height: 46px; border-radius: 50%; background: var(--gold); display: flex; align-items: center; justify-content: center; }
      #brand i svg { width: 30px; height: 30px; }

      /* ---------- hook ---------- */
      #hook { position: absolute; inset: 0; z-index: 8; }
      #hook .band { position: absolute; left: 0; right: 0; bottom: 0; height: 960px;
                    background: linear-gradient(180deg, rgba(8,9,12,0) 0%, rgba(8,9,12,.7) 38%, rgba(8,9,12,.92) 100%); }
      #hook .ln { position: absolute; left: 0; right: 0; text-align: center; font-weight: 900; text-transform: uppercase; }
      #h1 { top: 1095px; font-size: 100px; line-height: 1; text-shadow: 0 8px 0 rgba(0,0,0,.4); }
      #h2 { top: 1240px; } #h2 span { display: inline-block; font-size: 138px; line-height: 1.05; padding: 0 36px; border-radius: 28px;
                                        color: #1a1400; background: linear-gradient(180deg, #ffe066, #f2c811); box-shadow: 0 16px 50px rgba(242,200,17,.55); }
      #h3 { top: 1440px; font-size: 76px; line-height: 1; } #h3 b { color: var(--gold); }
      #h4 { top: 1560px; } #h4 span { display: inline-flex; align-items: center; gap: 14px; font-size: 36px; font-weight: 800; text-transform: none;
                                        padding: 14px 32px; border-radius: 999px; background: rgba(255,255,255,.12); border: 2px solid rgba(255,255,255,.35); }
      #h4 i { width: 40px; height: 40px; border-radius: 50%; background: var(--claude); display: inline-flex; padding: 6px; } #h4 i svg { width: 100%; height: 100%; }

      /* ---------- ipad focus + chips ---------- */
      #focus { position: absolute; left: 370px; top: 660px; width: 690px; height: 850px; z-index: 6; }
      .br { display: none; position: absolute; width: 120px; height: 120px; border: 12px solid var(--gold); filter: drop-shadow(0 0 16px rgba(242,200,17,.8)); }
      .br.tl { left: 0; top: 0; border-right: 0; border-bottom: 0; border-radius: 30px 0 0 0; }
      .br.tr { right: 0; top: 0; border-left: 0; border-bottom: 0; border-radius: 0 30px 0 0; }
      .br.bl { left: 0; bottom: 0; border-right: 0; border-top: 0; border-radius: 0 0 0 30px; }
      .br.brr { right: 0; bottom: 0; border-left: 0; border-top: 0; border-radius: 0 0 30px 0; }
      #ftag { position: absolute; right: 0px; top: -80px; font-size: 40px; padding: 10px 26px; border-radius: 18px; background: var(--gold); color: #1a1400; font-size: 36px; font-weight: 900; }
      #chips { position: absolute; inset: 0; z-index: 9; }
      .chip { position: absolute; display: flex; align-items: center; gap: 16px; padding: 18px 34px; border-radius: 26px; font-size: 44px; font-weight: 800;
              background: rgba(255,255,255,.96); color: var(--ink); box-shadow: 0 16px 40px rgba(0,0,0,.4); white-space: nowrap; }
      .chip .x { position: absolute; right: -36px; top: -34px; width: 96px; height: 96px; } .chip .x svg { width: 100%; height: 100%; }
      #chA { left: 470px; top: 190px; } #chB { left: 560px; top: 330px; }

      /* ---------- data + access -> AI (on the iPad back) ---------- */
      #flow { position: absolute; left: 150px; top: 600px; width: 780px; height: 760px; z-index: 7; }
      #flow .glass { position: absolute; inset: 0; }
      .ft { position: absolute; top: 50px; width: 260px; height: 190px; border-radius: 30px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 4px;
            font-size: 36px; font-weight: 800; background: rgba(255,255,255,.1); border: 3px solid rgba(255,255,255,.3); }
      .ft em { font-style: normal; font-size: 80px; line-height: 1.1; }
      #ftD { left: 70px; } #ftA { right: 70px; }
      #fArrows { position: absolute; left: 0; top: 230px; width: 780px; height: 130px; }
      #ftAI { position: absolute; left: 240px; top: 330px; width: 300px; height: 150px; border-radius: 34px; display: flex; align-items: center; justify-content: center; gap: 18px;
              background: linear-gradient(160deg, #e8875f, #c4603f); font-size: 60px; font-weight: 900; box-shadow: 0 0 60px rgba(217,119,87,.7); }
      #ftAI i { width: 74px; height: 74px; display: flex; } #ftAI i svg { width: 100%; height: 100%; }
      #fBub { position: absolute; left: 50px; right: 50px; top: 520px; padding: 26px 30px; border-radius: 28px 28px 8px 28px; background: #fff; color: var(--ink);
              font-size: 36px; font-weight: 700; line-height: 1.25; min-height: 150px; }
      #fBub .who { display: block; font-size: 24px; font-weight: 800; color: #6b7280; letter-spacing: .12em; margin-bottom: 6px; }
      #fSend { position: absolute; right: 30px; bottom: -36px; width: 84px; height: 84px; border-radius: 50%; background: var(--claude); display: flex; align-items: center; justify-content: center;
               font-size: 44px; color: #fff; box-shadow: 0 10px 30px rgba(217,119,87,.6); }

      /* ---------- laptop b-roll: Claude builds the page ---------- */
      #laptop { position: absolute; inset: 0; z-index: 7; }
      #laptop .dim { position: absolute; inset: 0; background: linear-gradient(180deg, rgba(6,8,16,.82), rgba(6,8,16,.62) 50%, rgba(6,8,16,.85)); }
      #lhead { position: absolute; left: 0; right: 0; top: 170px; text-align: center; }
      #lhead .kick { color: var(--gold); }
      #lhead .t { font-size: 58px; font-weight: 900; line-height: 1.1; margin-top: 8px; }
      .live { display: inline-flex; align-items: center; gap: 10px; margin-left: 14px; padding: 4px 16px; border-radius: 999px; background: var(--red); font-size: 22px; letter-spacing: .1em; color: #fff; vertical-align: middle; }
      .live:before { content: ""; width: 12px; height: 12px; border-radius: 50%; background: #fff; }
      #chat { position: absolute; left: 60px; right: 60px; top: 360px; height: 660px; border-radius: 34px; overflow: hidden; background: #f6f3ee; color: #1f1d1a;
              box-shadow: 0 30px 80px rgba(0,0,0,.6); }
      .wbar { height: 64px; display: flex; align-items: center; gap: 12px; padding: 0 26px; background: #ebe6de; font-size: 24px; font-weight: 700; color: #5d574e; }
      .wbar b { width: 18px; height: 18px; border-radius: 50%; background: #ff5f57; } .wbar b:nth-child(2) { background: #febc2e; } .wbar b:nth-child(3) { background: #28c840; }
      .wbar span { margin-left: 14px; display: flex; align-items: center; gap: 10px; }
      .wbar i { width: 30px; height: 30px; border-radius: 8px; background: var(--claude); display: inline-flex; padding: 4px; } .wbar i svg { width: 100%; height: 100%; }
      #ubub { margin: 28px 28px 0 130px; padding: 22px 28px; border-radius: 26px 26px 6px 26px; background: #fff; font-size: 31px; font-weight: 600; line-height: 1.32; min-height: 100px;
              box-shadow: 0 4px 14px rgba(0,0,0,.08); }
      #ubub .cur, #fBub .cur { display: inline-block; width: 4px; height: 34px; background: var(--claude); vertical-align: -6px; margin-left: 4px; }
      #tools { margin: 26px 28px 0; display: flex; flex-direction: column; gap: 12px; }
      .tool { position: relative; display: flex; align-items: center; gap: 14px; font-family: ui-monospace, "DejaVu Sans Mono", monospace; font-size: 28px; font-weight: 600; color: #6b645a;
              padding: 10px 18px; border-radius: 14px; background: #ece7df; }
      .tool .spin { width: 30px; height: 30px; border-radius: 50%; border: 5px solid #d8cfc2; border-top-color: var(--claude); }
      .tool .tick { position: absolute; left: 18px; width: 30px; height: 30px; } .tool .tick svg { width: 100%; height: 100%; }
      #areply { margin: 22px 28px 0; font-size: 30px; font-weight: 600; line-height: 1.35; } #areply b { color: var(--claude); }
      #pbiwin { position: absolute; left: 40px; right: 40px; top: 1060px; border-radius: 26px; overflow: hidden; background: #fff; box-shadow: 0 30px 90px rgba(0,0,0,.7), 0 0 0 4px rgba(242,200,17,.9); }
      #pbiwin .wbar { background: #1f1f1f; color: #ddd; } #pbiwin .wbar i { background: var(--gold); }
      #pbiwin img { display: block; width: 100%; }
      #rdy { position: absolute; right: 70px; top: 1010px; z-index: 2; display: flex; align-items: center; gap: 12px; padding: 14px 30px; border-radius: 999px; background: var(--green);
             font-size: 34px; font-weight: 900; box-shadow: 0 12px 40px rgba(34,197,94,.6); }
      #rdy svg { width: 40px; height: 40px; }

      /* ---------- building progress (mug shot) ---------- */
      #building { position: absolute; left: 90px; right: 90px; top: 1250px; z-index: 7; padding: 26px 34px; }
      #building .row { display: flex; align-items: center; gap: 18px; font-size: 34px; font-weight: 800; }
      #building .row i { width: 54px; height: 54px; border-radius: 14px; background: var(--claude); padding: 8px; display: flex; } #building .row i svg { width: 100%; height: 100%; }
      #bpct { margin-left: auto; color: var(--gold); font-size: 40px; }
      .track { margin-top: 18px; height: 22px; border-radius: 12px; background: rgba(255,255,255,.15); overflow: hidden; }
      #bfill { height: 100%; width: 100%; border-radius: 12px; background: linear-gradient(90deg, var(--claude), var(--gold)); transform-origin: 0 50%; }
      #bdone { position: absolute; inset: 0; border-radius: 36px; display: flex; align-items: center; justify-content: center; gap: 16px; background: var(--green); font-size: 44px; font-weight: 900; }
      #bdone svg { width: 56px; height: 56px; }

      /* ---------- old way / new way (sofa shot, top band) ---------- */
      #oldway, #newway { position: absolute; left: 0; right: 0; top: 150px; height: 260px; z-index: 7; }
      #oldcard { position: absolute; left: 90px; right: 90px; top: 0; height: 240px; display: flex; align-items: center; gap: 34px; padding: 0 44px;
                 background: rgba(40,8,12,.82); border-color: rgba(239,68,68,.6); }
      #clock { width: 160px; height: 160px; flex: none; } #clock svg { width: 100%; height: 100%; overflow: visible; }
      #oldcard .kick { color: #fca5a5; }
      #oldtxt { position: relative; height: 120px; width: 520px; margin-top: 8px; }
      #oldtxt div { position: absolute; left: 0; top: 0; font-size: 100px; font-weight: 900; line-height: 1.1; color: #fff; }
      #oldD { color: #ff6b6b !important; }
      #lk1 { position: absolute; left: 0; right: 0; top: 0; } #lk1 .tile { width: 210px; height: 180px; }
      #mins { position: absolute; left: 0; right: 0; top: 10px; text-align: center; }
      #mins .big { display: inline-block; font-size: 150px; font-weight: 900; line-height: 1; color: var(--gold); padding: 6px 34px; border-radius: 34px; background: rgba(8,9,12,.62);
                   text-shadow: 0 10px 0 rgba(0,0,0,.35), 0 0 50px rgba(242,200,17,.5); }
      #mins .big small { font-size: 72px; }
      #mins .sub { display: inline-flex; align-items: center; gap: 18px; margin-top: 18px; font-size: 38px; font-weight: 900; padding: 8px 30px; border-radius: 18px; background: rgba(8,9,12,.75); }
      #mins .sub s { color: #ff6b6b; text-decoration-thickness: 6px; }

      /* ---------- stages panel (selfie, lower band) ---------- */
      #stages { position: absolute; left: 40px; right: 40px; top: 1175px; height: 345px; z-index: 7; }
      #stages > .glass { position: absolute; inset: 0; }
      #stA, #stB, #stC { position: absolute; inset: 0; padding: 30px 34px; }
      #stA .kick { color: #fca5a5; text-align: center; }
      .sgrid { margin-top: 12px; display: flex; flex-wrap: wrap; justify-content: center; gap: 14px; }
      .stg { display: flex; align-items: center; gap: 8px; padding: 10px 18px; border-radius: 18px; font-size: 30px; font-weight: 800; background: rgba(255,255,255,.12); border: 2px solid rgba(255,255,255,.28); }
      .stg em { font-style: normal; font-size: 30px; }
      #tbar { position: absolute; left: 34px; right: 34px; bottom: 22px; height: 60px; border-radius: 20px; background: rgba(255,255,255,.1); overflow: hidden; }
      #tfill { position: absolute; inset: 0; background: linear-gradient(90deg, #f97316, var(--red)); transform-origin: 0 50%; }
      #tlab { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; gap: 18px; font-size: 36px; font-weight: 900; letter-spacing: .04em; }
      #auto { margin: 0 auto; width: 900px; height: 110px; border-radius: 28px; display: flex; align-items: center; justify-content: center; gap: 18px; font-size: 64px; font-weight: 900;
              color: #1a1400; background: linear-gradient(90deg, #ffe066, #f2c811, #ffb703); box-shadow: 0 0 50px rgba(242,200,17,.6); }
      #lk2 { margin-top: 14px; transform: scale(.66); transform-origin: 50% 0; }
      #stC { display: flex; flex-direction: column; gap: 22px; justify-content: center; }
      #acc { align-self: flex-start; display: flex; align-items: center; gap: 14px; padding: 12px 28px; border-radius: 999px; background: rgba(34,197,94,.2); border: 3px solid var(--green);
             font-size: 36px; font-weight: 800; }
      #acc svg { width: 40px; height: 40px; }
      #pbub { padding: 22px 28px; border-radius: 26px 26px 6px 26px; background: #fff; color: var(--ink); font-size: 36px; font-weight: 700; line-height: 1.3; min-height: 120px; }

      /* ---------- dashboards-ready showcase (full screen) ---------- */
      #show { position: absolute; inset: 0; z-index: 9; overflow: hidden; background: radial-gradient(circle at 50% 30%, #1d2a66 0%, #0c1230 55%, #06080f 100%); }
      #show .grid { position: absolute; inset: -80px; opacity: .14;
                    background-image: linear-gradient(rgba(255,255,255,.3) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.3) 1px, transparent 1px); background-size: 80px 80px; }
      #stitle { position: absolute; left: 0; right: 0; top: 150px; text-align: center; }
      #stitle .kick { color: var(--sky); }
      #stitle .big { margin-top: 24px; font-size: 170px; font-weight: 900; line-height: 1; color: var(--gold); text-shadow: 0 0 60px rgba(242,200,17,.5), 0 10px 0 rgba(0,0,0,.35); }
      #stitle .big small { font-size: 80px; }
      .reel { position: absolute; left: 0; display: flex; gap: 34px; transform: rotate(-6deg); }
      #reel1 { top: 560px; } #reel2 { top: 960px; }
      .rc { width: 620px; height: 349px; flex: none; border-radius: 22px; overflow: hidden; background: #fff; box-shadow: 0 24px 60px rgba(0,0,0,.6), 0 0 0 3px rgba(255,255,255,.25); }
      .rc img { width: 100%; height: 100%; display: block; }
      #stamp { position: absolute; left: 0; right: 0; top: 1320px; text-align: center; }
      #stamp span { display: inline-flex; align-items: center; gap: 18px; padding: 18px 46px; border-radius: 26px; background: var(--green); font-size: 60px; font-weight: 900;
                    box-shadow: 0 16px 50px rgba(34,197,94,.6); transform: rotate(-4deg); }
      #stamp svg { width: 70px; height: 70px; }

      /* ---------- guide ---------- */
      #guide { position: absolute; left: 50px; right: 50px; top: 1190px; height: 330px; z-index: 7; }
      #guide > .glass { position: absolute; inset: 0; }
      #book { position: absolute; left: 40px; top: -40px; width: 270px; height: 360px; border-radius: 10px 24px 24px 10px; padding: 34px 26px; perspective: 600px;
              background: linear-gradient(160deg, #1d2a66, #0b1028); border: 3px solid rgba(242,200,17,.8); box-shadow: -14px 20px 50px rgba(0,0,0,.6), inset 14px 0 0 rgba(255,255,255,.08);
              transform: rotate(-7deg); }
      #book .bt { font-size: 30px; font-weight: 900; line-height: 1.1; } #book .bt b { color: var(--gold); display: block; font-size: 46px; }
      #book .bs { margin-top: 18px; display: inline-block; padding: 6px 16px; border-radius: 10px; background: var(--gold); color: #1a1400; font-size: 26px; font-weight: 900; }
      #book .bp { position: absolute; left: 26px; bottom: 26px; font-size: 64px; font-weight: 900; color: var(--red); background: #fff; padding: 0 16px; border-radius: 12px; line-height: 1.2; }
      #book .bi { position: absolute; right: 22px; bottom: 26px; width: 70px; height: 70px; border-radius: 16px; background: var(--gold); padding: 10px; } #book .bi svg { width: 100%; height: 100%; }
      #glist { position: absolute; left: 345px; top: 28px; right: 30px; display: flex; flex-direction: column; gap: 16px; }
      #glist div { display: flex; align-items: center; gap: 14px; font-size: 34px; font-weight: 800; } #glist svg { width: 50px; height: 50px; flex: none; }
      #atoz { position: absolute; right: 30px; bottom: 20px; padding: 8px 26px; border-radius: 18px; background: var(--gold); color: #1a1400; font-size: 48px; font-weight: 900; }

      /* ---------- price ---------- */
      #price { position: absolute; left: 50px; right: 50px; top: 1165px; height: 360px; z-index: 7; }
      #price > .glass { position: absolute; inset: 0; border-color: rgba(242,200,17,.6); }
      #pk { position: absolute; left: 0; right: 0; top: 26px; text-align: center; color: var(--gold); }
      #pnum { position: absolute; left: 0; right: 0; top: 62px; text-align: center; font-size: 200px; font-weight: 900; line-height: 1; letter-spacing: -.02em;
              background: linear-gradient(180deg, #fff6c2 0%, #f2c811 55%, #c99a00 100%); -webkit-background-clip: text; background-clip: text; color: transparent;
              filter: drop-shadow(0 10px 0 rgba(0,0,0,.35)) drop-shadow(0 0 40px rgba(242,200,17,.45)); }
      #psub { position: absolute; left: 0; right: 0; bottom: 22px; text-align: center; font-size: 36px; font-weight: 800; }
      #psub span { display: inline-block; margin: 0 8px; padding: 6px 20px; border-radius: 14px; background: rgba(255,255,255,.12); }
      #shine { position: absolute; top: 0; bottom: 0; width: 160px; left: -200px; background: linear-gradient(90deg, rgba(255,255,255,0), rgba(255,255,255,.35), rgba(255,255,255,0)); transform: skewX(-18deg); }
      #pclip { position: absolute; inset: 0; overflow: hidden; border-radius: 36px; }
      .coin { position: absolute; left: 468px; top: 160px; width: 44px; height: 44px; border-radius: 50%; background: radial-gradient(circle at 35% 30%, #fff6c2, #f2c811 55%, #b88a00);
              box-shadow: 0 0 14px rgba(242,200,17,.8); display: flex; align-items: center; justify-content: center; font-size: 24px; font-weight: 900; color: #7a5a00; }

      /* ---------- comment CTA ---------- */
      #cta { position: absolute; left: 50px; right: 50px; top: 1290px; height: 600px; z-index: 7; }
      #cbox { position: absolute; left: 0; right: 0; top: 0; padding: 26px 30px; border-radius: 34px; background: #fff; color: var(--ink); box-shadow: 0 24px 60px rgba(0,0,0,.45); }
      #cbox .hd { font-size: 30px; font-weight: 800; color: #6b7280; }
      .crow { margin-top: 16px; display: flex; align-items: center; gap: 18px; }
      .av { width: 74px; height: 74px; border-radius: 50%; flex: none; background: linear-gradient(160deg, var(--sky), var(--blue)); }
      #cin { flex: 1; height: 86px; border-radius: 43px; border: 3px solid #e5e7eb; display: flex; align-items: center; padding: 0 28px; font-size: 46px; font-weight: 900; color: var(--ink); }
      #cin .ph { color: #9ca3af; font-weight: 600; font-size: 32px; }
      #cpost { padding: 16px 30px; border-radius: 22px; background: var(--blue); color: #fff; font-size: 34px; font-weight: 900; }
      #finger { position: absolute; left: -10px; top: -120px; font-size: 96px; line-height: 1; }
      #url { position: absolute; left: 0; right: 0; top: 470px; text-align: center; }
      #url span { display: inline-flex; align-items: center; gap: 14px; padding: 16px 38px; border-radius: 999px; background: var(--gold); color: #1a1400; font-size: 44px; font-weight: 900;
                  box-shadow: 0 14px 40px rgba(242,200,17,.5); }

      /* ---------- end card ---------- */
      #end { position: absolute; inset: 0; z-index: 14; overflow: hidden; background: #06080f; }
      #wall { position: absolute; left: -300px; top: -300px; width: 1900px; display: flex; flex-wrap: wrap; gap: 30px; transform: rotate(-12deg); opacity: .32; }
      #wall img { width: 440px; height: 248px; border-radius: 16px; }
      #end .shade { position: absolute; inset: 0; background: radial-gradient(circle at 50% 45%, rgba(13,20,48,.55) 0%, rgba(6,8,15,.92) 70%); }
      #ec { position: absolute; left: 60px; right: 60px; top: 300px; text-align: center; }
      #elogo { margin: 0 auto; width: 170px; height: 170px; border-radius: 44px; background: linear-gradient(160deg, #ffe066, #f2c811); padding: 34px;
               box-shadow: 0 0 80px rgba(242,200,17,.55); }
      #elogo svg { width: 100%; height: 100%; }
      #etitle { margin-top: 40px; font-size: 92px; font-weight: 900; line-height: 1.02; } #etitle b { color: var(--gold); }
      #etag { margin-top: 20px; font-size: 40px; font-weight: 600; opacity: .9; }
      #efeat { margin-top: 46px; display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }
      #efeat div { padding: 20px 10px; border-radius: 22px; background: rgba(255,255,255,.08); border: 2px solid rgba(255,255,255,.18); font-size: 30px; font-weight: 700; }
      #efeat b { display: block; font-size: 56px; font-weight: 900; color: var(--gold); line-height: 1.1; }
      #eprice { margin-top: 46px; font-size: 44px; font-weight: 800; } #eprice b { font-size: 110px; font-weight: 900; color: var(--gold); vertical-align: -10px; margin-right: 10px; }
      #ebtn { margin: 36px auto 0; display: inline-flex; align-items: center; gap: 18px; padding: 30px 70px; border-radius: 999px; font-size: 56px; font-weight: 900;
              background: linear-gradient(90deg, #ffe066, #f2c811); color: #1a1400; box-shadow: 0 18px 60px rgba(242,200,17,.55); }
      #eurl { margin-top: 30px; font-size: 42px; font-weight: 800; color: var(--sky); }
      #ecom { margin-top: 18px; font-size: 32px; font-weight: 700; opacity: .85; }

      /* ---------- captions + fx ---------- */
      #capwrap { position: absolute; left: 0; top: 1545px; width: 1080px; z-index: 16; }
      .cap { position: absolute; left: 40px; right: 40px; top: 0; display: flex; justify-content: center; }
      .capbox { text-align: center; font-weight: 900; font-size: 62px; line-height: 1.16; text-transform: uppercase;
                -webkit-text-stroke: 3px #000; paint-order: stroke fill; text-shadow: 0 6px 0 rgba(0,0,0,.6), 0 0 26px rgba(0,0,0,.6); }
      .w { display: inline-block; } .hl { color: var(--gold); }
      #leak { position: absolute; top: -200px; left: -900px; width: 900px; height: 2400px; z-index: 18; pointer-events: none; mix-blend-mode: screen; opacity: 0;
              background: linear-gradient(90deg, rgba(255,140,40,0), rgba(255,170,60,.75), rgba(255,230,140,.9), rgba(255,120,40,.6), rgba(255,140,40,0)); transform: rotate(14deg); filter: blur(30px); }
      #flash { position: absolute; inset: 0; background: #fff; z-index: 19; pointer-events: none; opacity: 0; }
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{{DURATION}}" data-width="1080" data-height="1920">
      <div id="spk" data-layout-allow-overflow>
        <video id="spkv" src="assets/speaker.mp4" muted playsinline data-start="0" data-duration="{{SPK}}" data-track-index="0"></video>
      </div>
      <div id="vig" class="clip" data-start="0" data-duration="{{SPK}}" data-track-index="1"></div>

      <!-- brand bug -->
      <div id="brand" class="clip" {{BRAND}} data-track-index="2"><i>{{PBI}}</i>Power BI MCP for Claude</div>

      <!-- hook -->
      <div id="hook" class="clip" {{HOOK}} data-track-index="3">
        <div class="band"></div>
        <div class="ln" id="h1">Build Power BI</div>
        <div class="ln" id="h2"><span>Dashboards</span></div>
        <div class="ln" id="h3">with <b>AI</b> in <b>minutes</b> ⚡</div>
        <div class="ln" id="h4"><span><i>{{CLAUDE}}</i>Claude + Power BI MCP</span></div>
      </div>

      <!-- ipad focus brackets -->
      <div id="focus" class="clip" {{FOCUS}} data-track-index="4">
        <div class="br tl"></div><div class="br tr"></div><div class="br bl"></div><div class="br brr"></div>
        <div id="ftag">THIS ONE 👀</div>
      </div>

      <!-- who builds it? -->
      <div id="chips" class="clip" {{CHIPS}} data-track-index="5">
        <div class="chip" id="chA">👨‍💻 Power BI Developer?<div class="x" id="xA">{{CROSS}}</div></div>
        <div class="chip" id="chB">📊 Data Analyst?<div class="x" id="xB">{{CROSS}}</div></div>
      </div>

      <!-- data + access -> AI -->
      <div id="flow" class="clip" {{FLOW}} data-track-index="6">
        <div class="glass"></div>
        <div class="ft" id="ftD"><em>🗄️</em>Your data</div>
        <div class="ft" id="ftA"><em>🔑</em>Access</div>
        <svg id="fArrows" viewBox="0 0 780 130"><path id="fa1" d="M200 10 C 220 90, 300 110, 360 120" stroke="#f2c811" stroke-width="10" fill="none" stroke-linecap="round"/>
          <path id="fa2" d="M580 10 C 560 90, 480 110, 420 120" stroke="#f2c811" stroke-width="10" fill="none" stroke-linecap="round"/></svg>
        <div id="ftAI"><i>{{CLAUDE}}</i>AI</div>
        <div id="fBub"><span class="who">YOU</span><span id="fTxt" data-text="{{PROMPT2}}"></span><span class="cur"></span><div id="fSend">➤</div></div>
      </div>

      <!-- laptop b-roll -->
      <div id="laptop" class="clip" {{LAPTOP}} data-track-index="7">
        <div class="dim"></div>
        <div id="lhead"><div class="kick">Claude + Power BI MCP <span class="live">LIVE</span></div><div class="t">You ask. Claude builds.</div></div>
        <div id="chat">
          <div class="wbar"><b></b><b></b><b></b><span><i>{{CLAUDE}}</i>Claude Desktop</span></div>
          <div id="ubub"><span id="uTxt" data-text="{{PROMPT1}}"></span><span class="cur"></span></div>
          <div id="tools">{{TOOLS}}</div>
          <div id="areply">Done. Your <b>Sales overview</b> page is ready: 3 cards, 2 slicers, 4 charts, 1 table.</div>
        </div>
        <div id="rdy">{{CHECK}} Built in Power BI</div>
        <div id="pbiwin"><div class="wbar"><b></b><b></b><b></b><span><i>{{PBI}}</i>Power BI Desktop · Sales.pbip</span></div><img src="assets/01-sales.webp" /></div>
      </div>

      <!-- building progress -->
      <div id="building" class="clip glass" {{BUILDING}} data-track-index="8">
        <div class="row"><i>{{CLAUDE}}</i>Claude is building your dashboard<span id="bpct">0%</span></div>
        <div class="track"><div id="bfill"></div></div>
        <div id="bdone">{{CHECK}} Dashboard ready!</div>
      </div>

      <!-- old way -->
      <div id="oldway" class="clip" {{OLDWAY}} data-track-index="9">
        <div id="oldcard" class="glass">
          <div id="clock"><svg viewBox="0 0 200 200"><circle cx="100" cy="100" r="86" fill="#fff" stroke="#ef4444" stroke-width="12"/>
            <g id="hrH"><path d="M100 100V54" stroke="#08090c" stroke-width="12" stroke-linecap="round"/></g>
            <g id="mnH"><path d="M100 100V30" stroke="#ef4444" stroke-width="8" stroke-linecap="round"/></g><circle cx="100" cy="100" r="10" fill="#08090c"/></svg></div>
          <div><div class="kick">The old way</div><div id="oldtxt"><div id="oldH">HOURS</div><div id="oldD">DAYS!</div></div></div>
        </div>
      </div>

      <!-- new way -->
      <div id="newway" class="clip" {{NEWWAY}} data-track-index="10">
        {{LOCK1}}
        <div id="mins"><div class="big">10–15 <small>MIN</small></div><br /><div class="sub"><s>Days</s> → <span style="color:#f2c811">Minutes</span> ⚡</div></div>
      </div>

      <!-- stages / automated / prompt -->
      <div id="stages" class="clip" {{STAGES}} data-track-index="11">
        <div class="glass" id="stGlass"></div>
        <div id="stA"><div class="kick">The old way · 7 stages</div><div class="sgrid">{{STAGE_PILLS}}</div>
          <div id="tbar"><div id="tfill"></div><div id="tlab">⏱ HOURS → DAYS</div></div></div>
        <div id="stB"><div id="auto">⚡ AUTOMATED</div>{{LOCK2}}</div>
        <div id="stC"><div id="acc">{{CHECK}} Access given</div><div id="pbub"><span id="pTxt" data-text="I want a sales dashboard like this."></span></div></div>
      </div>

      <!-- ready showcase -->
      <div id="show" class="clip" {{SHOW}} data-track-index="12">
        <div class="grid"></div>
        <div id="stitle"><div class="kick">Claude + Power BI MCP</div><div class="big">10–15 <small>MIN</small></div></div>
        <div class="reel" id="reel1">{{REEL}}</div>
        <div class="reel" id="reel2">{{REEL}}</div>
        <div id="stamp"><span>{{CHECK}} DASHBOARD READY</span></div>
      </div>

      <!-- guide -->
      <div id="guide" class="clip" {{GUIDE}} data-track-index="13">
        <div class="glass"></div>
        <div id="book"><div class="bt">Power BI MCP<b>for Claude</b></div><div class="bs">A–Z SETUP GUIDE</div><div class="bp">PDF</div><div class="bi">{{PBI}}</div></div>
        <div id="glist"><div id="g1">{{CHECK}} One-click installation</div><div id="g2">{{CHECK}} Connect Claude ↔ Power BI</div><div id="g3">{{CHECK}} Dashboard creation</div></div>
        <div id="atoz">A → Z</div>
      </div>

      <!-- price -->
      <div id="price" class="clip" {{PRICE}} data-track-index="14">
        <div class="glass"></div>
        <div id="pclip"><div id="shine"></div></div>
        <div id="pk" class="kick">Complete guide + setup kit</div>
        <div id="pnum">₹299</div>
        <div id="psub"><span>One-time</span><span>Instant download</span></div>
        <div id="coins"></div>
      </div>

      <!-- comment CTA -->
      <div id="cta" class="clip" {{CTA}} data-track-index="15">
        <div id="finger">👇</div>
        <div id="cbox"><div class="hd">💬 Add a comment…</div>
          <div class="crow"><div class="av"></div><div id="cin"><span class="ph" id="cph">Comment here</span><span id="cTxt"></span></div><div id="cpost">Post</div></div></div>
        <div id="url"><span>🌐 powerbi.growora.live</span></div>
      </div>

      <!-- end card -->
      <div id="end" class="clip" {{END}} data-track-index="16">
        <div id="wall">{{WALL}}</div>
        <div class="shade"></div>
        <div id="ec">
          <div id="elogo">{{PBI}}</div>
          <div id="etitle">Power BI MCP<br /><b>for Claude</b></div>
          <div id="etag">Talk to your report. Claude builds the dashboard.</div>
          <div id="efeat"><div id="ef1"><b>14</b>tools for Claude</div><div id="ef2"><b>~10 min</b>one-time setup</div>
            <div id="ef3"><b>10</b>sample dashboards</div><div id="ef4"><b>8</b>designer themes</div></div>
          <div id="eprice"><b>₹299</b>one-time</div>
          <div id="ebtn">GET IT NOW →</div>
          <div id="eurl">powerbi.growora.live</div>
          <div id="ecom">or comment “LINK” 👇</div>
        </div>
      </div>

      <div id="capwrap" class="clip" data-start="0" data-duration="{{SPK}}" data-track-index="17">
      {{CAPTIONS}}
      </div>
      <div id="leak" class="clip" data-start="0" data-duration="{{DURATION}}" data-track-index="18"></div>
      <div id="flash" class="clip" data-start="0" data-duration="{{DURATION}}" data-track-index="19"></div>
    </div>

    <script>
      const tl = gsap.timeline({ paused: true });
      const D = {{DURATION}}, SPK = {{SPK}};
      const T = {{T_JS}}, CAPS = {{CAPS_JS}};
      const [C1, C2, C3, C4, C5] = {{CUTS_JS}};
      const q = (s) => document.querySelector(s);

      // typing helper: reveals data-text character by character (seek-safe: text derived from tween progress)
      function type(sel, t, dur) {
        const el = q(sel), txt = el.dataset.text, st = { n: 0 };
        tl.fromTo(st, { n: 0 }, { n: txt.length, duration: dur, ease: "none", onUpdate() { el.textContent = txt.slice(0, Math.round(st.n)); } }, t);
      }
      function flash(t, a = 0.7) { tl.fromTo("#flash", { opacity: 0 }, { opacity: a, duration: 0.05, yoyo: true, repeat: 1, immediateRender: false }, t); }
      function leak(t) { tl.fromTo("#leak", { x: 0, opacity: 0.95 }, { x: 2300, opacity: 0.95, duration: 0.55, ease: "power2.inOut", immediateRender: false }, t);
                         tl.set("#leak", { opacity: 0 }, t + 0.56); }

      // ---------- footage zoom track: [start, end, fromScale, toScale, ease, origin]
      const Z = [
        [0, 2.0, 1.2, 1.04, "power2.out", "50% 45%"], [2.0, T.like_this, 1.04, 1.07, "none"],
        [T.like_this, T.like_this + 0.25, 1.07, 1.12, "power3.out"], [T.like_this + 0.25, C1, 1.12, 1.09, "none"],
        [C1, C1 + 0.35, 1.25, 1.05, "power3.out", "50% 30%"], [C1 + 0.35, T.neither, 1.05, 1.06, "none"],
        [T.neither, T.neither + 0.2, 1.06, 1.15, "power3.out"], [T.neither + 0.2, C2, 1.15, 1.08, "none"],
        [C2, C3, 1.0, 1.1, "none", "50% 50%"],
        [C3, C3 + 0.3, 1.22, 1.05, "power3.out", "50% 28%"], [C3 + 0.3, C4, 1.05, 1.1, "none"],
        [C4, C4 + 0.4, 1.4, 1.12, "power3.out", "50% 20%"], [C4 + 0.4, T.hours, 1.12, 1.18, "none"],
        [T.hours, T.days, 1.18, 1.2, "none"], [T.days, T.days + 0.2, 1.2, 1.3, "power3.out"], [T.days + 0.2, T.but, 1.3, 1.28, "none"],
        [T.but, T.but + 0.3, 1.28, 1.12, "power3.out"], [T.but + 0.3, T.min, 1.12, 1.17, "none"],
        [T.min, T.min + 0.2, 1.17, 1.3, "power3.out"], [T.min + 0.2, C5, 1.3, 1.26, "none"],
        [C5, C5 + 0.35, 1.2, 1.0, "power3.out", "50% 25%"], [C5 + 0.35, T.many, 1.0, 1.05, "none"],
        [T.many, T.many + 0.2, 1.05, 1.1, "power3.out"], [T.many + 0.2, T.but2, 1.1, 1.06, "none"],
        [T.but2, T.but2 + 0.25, 1.15, 1.02, "power3.out"], [T.but2 + 0.25, T.just, 1.02, 1.08, "none"],
        [T.just, T.install, 1.0, 1.0, "none"], [T.install, T.price, 1.0, 1.04, "none"],
        [T.price, T.price + 0.2, 1.04, 1.1, "power3.out"], [T.price + 0.2, T.learn, 1.1, 1.06, "none"],
        [T.learn, T.link, 1.06, 1.02, "none"], [T.link, T.link + 0.2, 1.02, 1.09, "power3.out"], [T.link + 0.2, SPK, 1.09, 1.06, "none"],
      ];
      Z.forEach(([s, e, a, b, ease, org]) => {
        if (org) tl.set("#spkv", { transformOrigin: org }, s);
        tl.fromTo("#spkv", { scale: a }, { scale: b, duration: Math.max(e - s, 0.01), ease, immediateRender: s === 0 }, s);
      });

      // ---------- transitions on cuts
      flash(0, 0.9); flash(C1 - 0.02, 0.55); flash(C3 - 0.02, 0.5); flash(C4 - 0.02, 0.6);
      leak(C2 - 0.25); leak(C5 - 0.3); leak(T.but2 - 0.2); leak(SPK - 0.25);
      flash(T.neither, 0.35); flash(T.min, 0.45); flash(T.price, 0.5);

      // ---------- captions
      CAPS.forEach(([sel, s, e]) => {
        tl.from(sel + " .w", { autoAlpha: 0, y: 34, scale: 0.55, duration: 0.2, ease: "back.out(2.6)", stagger: 0.05 }, s);
        tl.to(sel, { opacity: 0, duration: 0.08 }, e - 0.08);
      });

      // ---------- brand bug
      tl.from("#brand", { opacity: 0, x: -60, duration: 0.4, ease: "back.out(2)" }, 3.6);

      // ---------- hook
      tl.from("#hook .band", { opacity: 0, duration: 0.3 }, 0);
      tl.from("#h1", { autoAlpha: 0, scale: 2.2, filter: "blur(20px)", duration: 0.35, ease: "expo.out" }, 0.04);
      tl.from("#h2 span", { autoAlpha: 0, scale: 0.2, rotation: -10, duration: 0.42, ease: "back.out(2.4)" }, 0.42);
      tl.from("#h3", { autoAlpha: 0, y: 50, duration: 0.35, ease: "back.out(2)" }, 0.82);
      tl.from("#h4", { autoAlpha: 0, y: 40, scale: 0.8, duration: 0.35, ease: "back.out(2)" }, 1.3);
      tl.to("#h2 span", { scale: 1.06, duration: 1.4, ease: "sine.inOut" }, 0.9);
      tl.to(["#h1", "#h2", "#h3", "#h4"], { autoAlpha: 0, y: 120, duration: 0.3, ease: "power2.in", stagger: 0.04 }, 3.35);
      tl.to("#hook .band", { opacity: 0, duration: 0.35 }, 3.45);

      // ---------- focus brackets on the iPad
      tl.from(".br", { autoAlpha: 0, scale: 1.6, duration: 0.35, ease: "back.out(2)", stagger: 0.04 }, T.like_this - 0.1);
      tl.from("#ftag", { autoAlpha: 0, y: 30, scale: 0.5, duration: 0.3, ease: "back.out(2.5)" }, T.like_this + 0.2);
      tl.to(".br", { opacity: 0.55, duration: 0.5, yoyo: true, repeat: 3, ease: "sine.inOut" }, T.like_this + 0.5);
      tl.to("#focus", { opacity: 0, scale: 1.1, duration: 0.25 }, C1 - 0.3);

      // ---------- who builds it? chips -> stamped out
      tl.set(["#xA", "#xB"], { autoAlpha: 0 }, 0);
      tl.from("#chA", { autoAlpha: 0, x: 200, rotation: 6, duration: 0.4, ease: "back.out(2)" }, T.dev);
      tl.from("#chB", { autoAlpha: 0, x: 200, rotation: 6, duration: 0.4, ease: "back.out(2)" }, T.analyst - 0.4);
      tl.to("#chA", { x: -270, y: 570, rotation: -3, duration: 0.4, ease: "power3.inOut" }, C1 - 0.15);
      tl.to("#chB", { x: -260, y: 570, rotation: 3, duration: 0.4, ease: "power3.inOut" }, C1 - 0.1);
      tl.fromTo("#xA", { autoAlpha: 0, scale: 3 }, { autoAlpha: 1, scale: 1, duration: 0.2, ease: "power4.in", immediateRender: false }, T.neither);
      tl.fromTo("#xB", { autoAlpha: 0, scale: 3 }, { autoAlpha: 1, scale: 1, duration: 0.2, ease: "power4.in", immediateRender: false }, T.neither + 0.16);
      tl.to(["#chA", "#chB"], { x: -8, duration: 0.04, yoyo: true, repeat: 5 }, T.neither + 0.2);
      tl.to("#chA", { y: 1470, rotation: -25, autoAlpha: 0, duration: 0.45, ease: "power2.in" }, T.neither + 0.5);
      tl.to("#chB", { y: 1470, rotation: 25, autoAlpha: 0, duration: 0.45, ease: "power2.in" }, T.neither + 0.58);

      // ---------- data + access -> AI
      tl.set(["#fa1", "#fa2"], { strokeDasharray: 260, strokeDashoffset: 260 }, 0);
      tl.from("#flow .glass", { autoAlpha: 0, scale: 0.85, duration: 0.35, ease: "back.out(1.6)" }, T.data - 0.1);
      tl.from("#ftD", { autoAlpha: 0, scale: 0.3, duration: 0.35, ease: "back.out(2.4)" }, T.data);
      tl.from("#ftA", { autoAlpha: 0, scale: 0.3, duration: 0.35, ease: "back.out(2.4)" }, T.access);
      tl.to(["#fa1", "#fa2"], { strokeDashoffset: 0, duration: 0.35, ease: "power2.out" }, T.ai - 0.3);
      tl.from("#ftAI", { autoAlpha: 0, scale: 0.2, duration: 0.4, ease: "back.out(2.6)" }, T.ai);
      tl.fromTo("#ftAI i", { rotation: 0 }, { rotation: 360, duration: 3.5, ease: "none" }, T.ai);
      tl.from("#fBub", { autoAlpha: 0, y: 40, duration: 0.3, ease: "power3.out" }, T.ask - 0.2);
      type("#fTxt", T.ask, 1.6);
      tl.fromTo("#fSend", { scale: 1 }, { scale: 1.3, duration: 0.12, yoyo: true, repeat: 1 }, T.send + 0.1);
      tl.to("#flow", { opacity: 0, scale: 0.6, y: -200, duration: 0.3, ease: "power3.in" }, C2 - 0.3);

      // ---------- laptop b-roll: chat -> tools -> dashboard
      tl.from("#laptop .dim", { opacity: 0, duration: 0.25 }, C2);
      tl.from("#lhead", { autoAlpha: 0, y: -40, duration: 0.35, ease: "back.out(2)" }, C2);
      tl.from("#chat", { autoAlpha: 0, y: 120, scale: 0.9, duration: 0.4, ease: "back.out(1.4)" }, C2 + 0.05);
      type("#uTxt", C2 + 0.35, 1.45);
      tl.set(".tool .tick", { autoAlpha: 0 }, 0);
      [0, 1, 2, 3].forEach((i) => {
        const t = C2 + 2.0 + i * 0.32;
        tl.from("#tool" + i, { autoAlpha: 0, x: -40, duration: 0.2, ease: "power2.out" }, t);
        tl.fromTo("#tool" + i + " .spin", { rotation: 0 }, { rotation: 540, duration: 0.3, ease: "none" }, t);
        tl.set("#tool" + i + " .spin", { autoAlpha: 0 }, t + 0.3);
        tl.set("#tool" + i + " .tick", { autoAlpha: 1 }, t + 0.3);
      });
      tl.from("#areply", { autoAlpha: 0, y: 20, duration: 0.3 }, C2 + 3.35);
      tl.from("#pbiwin", { autoAlpha: 0, y: 300, scale: 0.5, rotation: -4, duration: 0.5, ease: "back.out(1.4)" }, C2 + 3.45);
      tl.to("#pbiwin", { scale: 1.04, duration: 1.8, ease: "none" }, C2 + 3.95);
      tl.from("#rdy", { autoAlpha: 0, scale: 0.3, duration: 0.35, ease: "back.out(2.6)" }, C2 + 4.15);
      tl.to("#chat", { opacity: 0.35, duration: 0.4 }, C2 + 3.6);

      // ---------- building progress (mug)
      const bp = { v: 0 };
      tl.from("#building", { opacity: 0, y: 60, duration: 0.35, ease: "back.out(2)" }, C3 + 0.3);
      tl.fromTo("#bfill", { scaleX: 0 }, { scaleX: 1, duration: 2.1, ease: "power1.inOut" }, C3 + 0.5);
      tl.fromTo(bp, { v: 0 }, { v: 100, duration: 2.1, ease: "power1.inOut", onUpdate() { q("#bpct").textContent = Math.round(bp.v) + "%"; } }, C3 + 0.5);
      tl.fromTo("#bdone", { autoAlpha: 0, scale: 0.9 }, { autoAlpha: 1, scale: 1, duration: 0.25, ease: "back.out(2)" }, C4 - 0.5);

      // ---------- old way: hours -> days
      tl.from("#oldcard", { autoAlpha: 0, y: -80, duration: 0.4, ease: "back.out(1.8)" }, T.hours - 2.6);
      tl.set("#oldD", { autoAlpha: 0 }, 0);
      tl.from("#oldH", { autoAlpha: 0, scale: 0.4, duration: 0.3, ease: "back.out(2.6)" }, T.hours);
      tl.fromTo("#mnH", { rotation: 0, svgOrigin: "100 100" }, { rotation: 360 * 6, svgOrigin: "100 100", duration: T.but - T.hours + 2.4, ease: "power1.in" }, T.hours - 2.4);
      tl.fromTo("#hrH", { rotation: 0, svgOrigin: "100 100" }, { rotation: 180, svgOrigin: "100 100", duration: T.but - T.hours + 2.4, ease: "power1.in" }, T.hours - 2.4);
      tl.to("#oldH", { autoAlpha: 0, y: -60, duration: 0.15 }, T.days - 0.05);
      tl.fromTo("#oldD", { autoAlpha: 0, scale: 2 }, { autoAlpha: 1, scale: 1, duration: 0.25, ease: "power4.in", immediateRender: false }, T.days);
      tl.to("#oldcard", { x: 10, duration: 0.04, yoyo: true, repeat: 7 }, T.days + 0.25);
      tl.to("#oldcard", { autoAlpha: 0, y: -100, scale: 0.8, duration: 0.3, ease: "power3.in" }, T.but - 0.05);

      // ---------- new way: Claude + MCP + Power BI -> 10-15 min
      tl.from("#lk1a", { autoAlpha: 0, y: -80, scale: 0.4, duration: 0.4, ease: "back.out(2.2)" }, T.claude);
      tl.from("#lk1p1", { autoAlpha: 0, scale: 0, duration: 0.25 }, T.mcp - 0.15);
      tl.from("#lk1b", { autoAlpha: 0, y: -80, scale: 0.4, duration: 0.4, ease: "back.out(2.2)" }, T.mcp);
      tl.from("#lk1p2", { autoAlpha: 0, scale: 0, duration: 0.25 }, T.pbi - 0.15);
      tl.from("#lk1c", { autoAlpha: 0, y: -80, scale: 0.4, duration: 0.4, ease: "back.out(2.2)" }, T.pbi);
      tl.to("#lk1", { autoAlpha: 0, scale: 0.6, y: -60, duration: 0.3, ease: "power3.in" }, T.min - 0.35);
      tl.from("#mins .big", { autoAlpha: 0, scale: 3, filter: "blur(24px)", duration: 0.4, ease: "expo.out" }, T.min);
      tl.from("#mins .sub", { autoAlpha: 0, y: 40, duration: 0.3, ease: "back.out(2)" }, T.min + 0.6);
      tl.to("#mins .big", { scale: 1.06, duration: 1.5, ease: "sine.inOut" }, T.min + 0.4);
      tl.to("#newway", { opacity: 0, duration: 0.2 }, C5 - 0.2);

      // ---------- stages -> automated -> prompt
      tl.set(["#stB", "#stC"], { autoAlpha: 0 }, 0);
      tl.from("#stGlass", { autoAlpha: 0, y: 80, duration: 0.4, ease: "back.out(1.6)" }, C5 + 0.3);
      tl.from("#stA .kick", { autoAlpha: 0, y: 20, duration: 0.3 }, C5 + 0.45);
      T.stages.forEach((t, i) => tl.from("#stg" + i, { autoAlpha: 0, scale: 0.3, y: 30, duration: 0.3, ease: "back.out(2.6)" }, t));
      tl.from("#tbar", { autoAlpha: 0, duration: 0.25 }, T.many - 0.2);
      tl.to(".stg", { x: 5, duration: 0.05, yoyo: true, repeat: 5, stagger: 0.02 }, T.many);
      tl.fromTo("#tfill", { scaleX: 0 }, { scaleX: 1, duration: T.d2 - T.many, ease: "power1.in" }, T.many);
      tl.to("#tbar", { scale: 1.05, duration: 0.12, yoyo: true, repeat: 3 }, T.d2);
      tl.to(".stg", { x: 0, y: 0, scale: 0.2, autoAlpha: 0, duration: 0.35, ease: "power3.in", stagger: 0.025 }, T.but2 - 0.05);
      tl.to(["#stA .kick", "#tbar"], { autoAlpha: 0, duration: 0.2 }, T.but2);
      tl.fromTo("#stB", { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.01, immediateRender: false }, T.but2 + 0.3);
      tl.from("#auto", { scale: 0.2, filter: "blur(16px)", duration: 0.45, ease: "expo.out" }, T.but2 + 0.3);
      tl.to("#stGlass", { borderColor: "rgba(242,200,17,.8)", duration: 0.3 }, T.but2 + 0.3);
      tl.from(["#lk2a", "#lk2p1", "#lk2b", "#lk2p2", "#lk2c"], { autoAlpha: 0, y: 40, scale: 0.4, duration: 0.35, ease: "back.out(2.2)", stagger: 0.12 }, T.claude2);
      tl.to("#auto", { scale: 1.05, duration: 0.15, yoyo: true, repeat: 1 }, T.automate);
      tl.to("#stB", { autoAlpha: 0, y: -40, duration: 0.25 }, T.access2 - 0.35);
      tl.fromTo("#stC", { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.01, immediateRender: false }, T.access2 - 0.1);
      tl.from("#acc", { autoAlpha: 0, x: -60, duration: 0.3, ease: "back.out(2)" }, T.access2);
      tl.from("#pbub", { autoAlpha: 0, y: 30, duration: 0.3 }, T.what - 0.2);
      type("#pTxt", T.what, 1.1);
      tl.to("#stages", { opacity: 0, scale: 0.9, duration: 0.2 }, T.just - 0.2);

      // ---------- dashboards ready showcase
      tl.from("#show", { clipPath: "circle(0% at 50% 50%)", duration: 0.45, ease: "power3.out" }, T.just);
      tl.from("#stitle .big", { scale: 2.6, filter: "blur(20px)", autoAlpha: 0, duration: 0.45, ease: "expo.out" }, T.just + 0.1);
      tl.from("#stitle .kick", { autoAlpha: 0, y: -20, duration: 0.3 }, T.just + 0.3);
      tl.fromTo("#reel1", { x: 200 }, { x: -2900, duration: T.install - T.just, ease: "none" }, T.just);
      tl.fromTo("#reel2", { x: -3800 }, { x: -700, duration: T.install - T.just, ease: "none" }, T.just);
      tl.to("#show .grid", { y: 80, duration: T.install - T.just, ease: "none" }, T.just);
      tl.from("#stamp span", { autoAlpha: 0, scale: 2.5, duration: 0.3, ease: "power4.in" }, T.ready);
      tl.to("#show", { opacity: 0, duration: 0.2 }, T.install - 0.2);

      // ---------- guide
      tl.from("#guide .glass", { autoAlpha: 0, y: 80, duration: 0.4, ease: "back.out(1.6)" }, T.install);
      tl.from("#book", { autoAlpha: 0, x: -200, rotation: -30, duration: 0.5, ease: "back.out(1.6)" }, T.install + 0.15);
      tl.to("#book", { rotation: -3, y: -10, duration: 4, ease: "sine.inOut" }, T.install + 0.65);
      tl.from("#g1", { autoAlpha: 0, x: 60, duration: 0.3, ease: "back.out(2)" }, T.install + 0.3);
      tl.from("#g2", { autoAlpha: 0, x: 60, duration: 0.3, ease: "back.out(2)" }, T.install + 0.75);
      tl.from("#g3", { autoAlpha: 0, x: 60, duration: 0.3, ease: "back.out(2)" }, T.creation);
      tl.from("#atoz", { autoAlpha: 0, scale: 2.5, rotation: 20, duration: 0.3, ease: "power4.in" }, T.atoz);
      tl.to("#book", { scale: 1.08, duration: 0.15, yoyo: true, repeat: 1 }, T.pdf);
      tl.to("#guide", { opacity: 0, y: 40, duration: 0.2 }, T.guide_end - 0.2);

      // ---------- price
      tl.from("#price .glass", { autoAlpha: 0, scale: 0.85, duration: 0.35, ease: "back.out(1.6)" }, T.guide_end);
      tl.from("#pk", { autoAlpha: 0, y: -20, duration: 0.3 }, T.guide_end + 0.15);
      tl.from("#pnum", { autoAlpha: 0, scale: 3, filter: "blur(24px)", duration: 0.35, ease: "expo.out" }, T.price);
      tl.fromTo("#shine", { x: 0 }, { x: 1400, duration: 0.7, ease: "power2.inOut" }, T.price + 0.3);
      tl.from("#psub span", { autoAlpha: 0, y: 30, duration: 0.3, stagger: 0.12, ease: "back.out(2)" }, T.download - 0.2);
      tl.to("#pnum", { scale: 1.05, duration: 0.8, yoyo: true, repeat: 1, ease: "sine.inOut" }, T.price + 0.4);
      const coins = q("#coins");
      for (let i = 0; i < 16; i++) {
        const c = document.createElement("div"); c.className = "coin"; c.textContent = "₹"; coins.appendChild(c);
        const a = (i / 16) * Math.PI * 2 + (i % 3) * 0.2, r = 330 + (i % 4) * 60;
        tl.fromTo(c, { x: 0, y: 0, scale: 0.3, autoAlpha: 0 },
          { keyframes: [{ x: Math.cos(a) * r * 0.6, y: Math.sin(a) * r * 0.45 - 60, scale: 1.1, autoAlpha: 1, duration: 0.35, ease: "power2.out" },
                        { x: Math.cos(a) * r, y: Math.sin(a) * r * 0.6 + 260, scale: 0.8, autoAlpha: 0, duration: 0.6, ease: "power1.in" }], immediateRender: false }, T.price + 0.02);
      }
      tl.to("#price", { opacity: 0, y: 40, duration: 0.2 }, T.learn - 0.2);

      // ---------- comment CTA
      tl.from("#cbox", { autoAlpha: 0, y: 80, duration: 0.4, ease: "back.out(1.8)" }, T.learn);
      tl.from("#finger", { autoAlpha: 0, y: -40, duration: 0.3 }, T.learn + 0.4);
      tl.to("#finger", { y: 26, duration: 0.3, yoyo: true, repeat: 9, ease: "sine.inOut" }, T.learn + 0.7);
      tl.set("#cph", { display: "none" }, T.link - 0.35);
      const ct = { n: 0 }, CT = "LINK";
      tl.fromTo(ct, { n: 0 }, { n: 4, duration: 0.3, ease: "none", onUpdate() { q("#cTxt").textContent = CT.slice(0, Math.round(ct.n)); } }, T.link - 0.35);
      tl.to("#cin", { borderColor: "#2563eb", duration: 0.2 }, T.link - 0.35);
      tl.to("#cpost", { scale: 0.88, duration: 0.08, yoyo: true, repeat: 1 }, T.comment);
      tl.to("#cpost", { backgroundColor: "#22c55e", duration: 0.2 }, T.comment + 0.15);
      tl.from("#url", { autoAlpha: 0, y: 40, scale: 0.6, duration: 0.35, ease: "back.out(2.4)" }, T.share - 0.2);
      tl.to("#url span", { scale: 1.06, duration: 0.3, yoyo: true, repeat: 3, ease: "sine.inOut" }, T.share + 0.2);

      // ---------- end card
      tl.from("#end", { clipPath: "circle(0% at 50% 50%)", duration: 0.5, ease: "power3.out" }, SPK - 0.05);
      tl.fromTo("#wall", { x: 0, y: 0 }, { x: -260, y: -140, duration: 4.4, ease: "none" }, SPK - 0.05);
      tl.from("#elogo", { autoAlpha: 0, scale: 0.2, rotation: -40, duration: 0.5, ease: "back.out(2.2)" }, SPK + 0.05);
      tl.from("#etitle", { autoAlpha: 0, y: 40, scale: 0.8, duration: 0.4, ease: "back.out(2)" }, SPK + 0.3);
      tl.from("#etag", { autoAlpha: 0, y: 20, duration: 0.3 }, SPK + 0.55);
      tl.from(["#ef1", "#ef2", "#ef3", "#ef4"], { autoAlpha: 0, scale: 0.5, duration: 0.3, ease: "back.out(2.4)", stagger: 0.25 }, SPK + 0.75);
      tl.from("#eprice", { autoAlpha: 0, scale: 2, duration: 0.35, ease: "expo.out" }, SPK + 1.7);
      tl.from("#ebtn", { autoAlpha: 0, y: 40, scale: 0.6, duration: 0.35, ease: "back.out(2.4)" }, SPK + 2.0);
      tl.to("#ebtn", { scale: 0.92, duration: 0.09, yoyo: true, repeat: 1 }, SPK + 2.4);
      tl.to("#ebtn", { scale: 1.06, duration: 0.4, yoyo: true, repeat: 3, ease: "sine.inOut" }, SPK + 2.6);
      tl.from(["#eurl", "#ecom"], { autoAlpha: 0, y: 20, duration: 0.3, stagger: 0.15 }, SPK + 2.2);

      window.__timelines = window.__timelines || {};
      window.__timelines["main"] = tl;
      tl.seek(0);
    </script>
  </body>
</html>
