from fastapi import APIRouter
from fastapi.responses import HTMLResponse


router = APIRouter()


STYLE = """
<style>
*{box-sizing:border-box}
body{
margin:0;
background:#090a0c;
color:#eee;
font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif
}
.shell{
display:grid;
grid-template-columns:220px 1fr;
min-height:100vh
}
.side{
border-right:1px solid #23262a;
padding:18px 12px
}
.brand{
font-size:21px;
font-weight:750;
margin:0 8px 22px
}
.nav{
display:block;
text-decoration:none;
color:#aaa;
padding:9px;
border-radius:7px;
font-size:13px
}
.nav:hover{background:#15171b;color:#fff}
.section{
font-size:10px;
color:#666;
letter-spacing:.08em;
margin:22px 9px 7px;
text-transform:uppercase
}
.main{padding:28px 34px}
h1{font-size:28px;margin:0}
.sub{
color:#8d9299;
max-width:760px;
line-height:1.6;
margin:8px 0 26px
}
.grid{
display:grid;
grid-template-columns:repeat(auto-fill,minmax(250px,1fr));
gap:10px
}
.card{
border:1px solid #272b30;
background:#111317;
border-radius:9px;
padding:15px
}
.title{
font-size:14px;
font-weight:700
}
.meta{
font-size:10px;
color:#727880;
margin:5px 0 10px
}
.desc{
font-size:12px;
line-height:1.55;
color:#a3a8af
}
.status{
display:inline-block;
margin-top:13px;
font-size:9px;
padding:5px 7px;
border:1px solid #31353b;
border-radius:6px
}
.notice{
margin-top:25px;
border:1px solid #34383e;
padding:14px;
border-radius:8px;
color:#9ba1a8;
font-size:11px;
line-height:1.6
}
</style>
"""


NAV = """
<div class="side">

<div class="brand">
FX
</div>

<a class="nav" href="/chat">
Chat
</a>

<a class="nav" href="/markets">
Global Markets
</a>

<div class="section">
Research
</div>

<a class="nav" href="/brains">
Model Council
</a>

<a class="nav" href="/strategies">
Strategies
</a>

<a class="nav" href="/hedge-funds">
Hedge Fund Intelligence
</a>

<div class="section">
Trading
</div>

<a class="nav" href="/chat">
Paper Trading
</a>

</div>
"""


@router.get(
    "/brains",
    response_class=HTMLResponse,
)
async def brains():

    return (
        """
        <!doctype html>
        <html>
        <head>
        <title>FX Brains</title>
        """
        + STYLE
        + """
        </head>
        <body>

        <div class="shell">
        """
        + NAV
        + """
        <main class="main">

        <h1>
        FX Brains
        </h1>

        <div class="sub">
        These are the independent models and analytical methods
        available to FX. Installed does not mean trusted.
        Every predictive model must still be trained and validated.
        </div>

        <div
        id="grid"
        class="grid"
        ></div>

        <div class="notice">
        A complicated model is not automatically better.
        FX keeps simple models as baselines so advanced AI must prove
        that it adds useful information.
        </div>

        </main>
        </div>

        <script>

        fetch("/api/research/brains")
        .then(r=>r.json())
        .then(data=>{

            const grid =
                document.getElementById("grid");

            data.brains.forEach(x=>{

                const d =
                    document.createElement("div");

                d.className="card";

                d.style.cursor="pointer";

                d.onclick=()=>{
                    location.href="/strategy/"+x.id;
                };

                d.innerHTML=`
                <div class="title">
                ${x.name}
                </div>

                <div class="meta">
                ${x.type}
                </div>

                <div class="desc">
                ${x.job}
                </div>

                <div class="status">
                ${x.status}
                </div>
                `;

                grid.appendChild(d);

            });

        });

        </script>

        
<a
 href="/terminal"
 style="
   position:fixed;
   bottom:18px;
   right:18px;
   z-index:9999;
   background:#f3f3f3;
   color:#111;
   padding:9px 13px;
   border-radius:7px;
   text-decoration:none;
   font-size:12px;
   font-weight:700;
   border:1px solid #666;
 "
>
Terminal
</a>

</body>
        </html>
        """
    )


@router.get(
    "/strategies",
    response_class=HTMLResponse,
)
async def strategies():

    return (
        """
        <!doctype html>
        <html>
        <head>
        <title>FX Strategies</title>
        """
        + STYLE
        + """
        </head>

        <body>

        <div class="shell">
        """
        + NAV
        + """
        <main class="main">

        <h1>
        Strategy Library
        </h1>
<div id="fx-paper-fleet-link" style="margin:12px 0 18px;">
  <a href="/strategy-fleet" style="display:inline-block;color:#f4f4f5;text-decoration:none;border:1px solid #343a40;border-radius:6px;padding:8px 11px;font-size:11px;">
    Open Running Paper Strategy Fleet
  </a>
</div>


        <div class="sub">
        These are research frameworks FX can test.
        None should be treated as profitable or live-ready until
        it passes the complete validation process.
        </div>

        <div
        id="grid"
        class="grid"
        ></div>

        <div class="notice">
        Every strategy begins in Research.
        It must pass historical testing, out-of-sample validation,
        robustness tests and Paper Trading before being considered
        for real money.
        </div>

        </main>
        </div>

        <script>

        fetch("/api/research/strategies")
        .then(r=>r.json())
        .then(data=>{

            const grid =
                document.getElementById("grid");

            data.strategies.forEach(x=>{

                const d =
                    document.createElement("div");

                d.className="card";

                d.innerHTML=`
                <div class="title">
                ${x.name}
                </div>

                <div class="meta">
                ${x.family}
                </div>

                <div class="desc">
                ${x.plain_english}
                </div>

                <div class="status">
                ${x.status}
                </div>
                `;

                grid.appendChild(d);

            });

        });

        </script>

        </body>
        </html>
        """
    )


@router.get(
    "/hedge-funds",
    response_class=HTMLResponse,
)
async def hedge_funds():

    return (
        """
        <!doctype html>
        <html>
        <head>
        <title>FX Hedge Fund Intelligence</title>
        """
        + STYLE
        + """
        </head>

        <body>

        <div class="shell">
        """
        + NAV
        + """
        <main class="main">

        <h1>
        Hedge Fund Intelligence
        </h1>

        <div class="sub">
        Public regulatory data that helps FX understand
        institutional positioning, short pressure, activist activity,
        leverage and counterparty risk.

        This information is delayed regulatory evidence.
        It is not a live feed of hedge-fund orders.
        </div>

        <div
        id="grid"
        class="grid"
        ></div>

        <div class="notice">
        FX will always show the source and reporting delay.
        Regulatory positioning should be used as context,
        not as an automatic buy or sell signal.
        </div>

        </main>
        </div>

        <script>

        fetch("/api/research/hedge-funds/sources")
        .then(r=>r.json())
        .then(data=>{

            const grid =
                document.getElementById("grid");

            data.sources.forEach(x=>{

                const d =
                    document.createElement("div");

                d.className="card";

                d.innerHTML=`
                <div class="title">
                ${x.name}
                </div>

                <div class="meta">
                ${x.type} · ${x.frequency}
                </div>

                <div class="desc">
                ${x.limitations}
                </div>

                <div class="status">
                ${x.status}
                </div>
                `;

                grid.appendChild(d);

            });

        });

        </script>

        </body>
        </html>
        """
    )
