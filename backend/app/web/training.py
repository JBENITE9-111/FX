from fastapi import (
    APIRouter,
)

from fastapi.responses import (
    HTMLResponse,
    RedirectResponse,
)


router = APIRouter()


@router.get(
    "/training",
    response_class=HTMLResponse,
)
async def training():

    return RedirectResponse(
        url="/terminal?panel=learning",
        status_code=307,
    )

    return r"""
<!doctype html>

<html>

<head>

<title>
FX Training Center
</title>

<style>

body{
margin:0;
background:#090a0c;
color:#eee;
font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif
}

main{
max-width:1100px;
margin:auto;
padding:32px
}

a{
color:#999;
text-decoration:none
}

h1{
font-size:30px;
margin-bottom:5px
}

.subtitle{
color:#92979f;
max-width:800px;
line-height:1.6
}

.controls{
margin-top:25px;
display:flex;
gap:8px;
flex-wrap:wrap
}

input,select{
background:#14161a;
color:#fff;
border:1px solid #30343a;
border-radius:8px;
padding:11px
}

button{
border:0;
border-radius:8px;
padding:11px 16px;
font-weight:700;
cursor:pointer
}

.primary{
background:#eee;
color:#111
}

.grid{
display:grid;
grid-template-columns:
repeat(
auto-fit,
minmax(280px,1fr)
);
gap:10px;
margin-top:25px
}

.card{
border:1px solid #292d32;
background:#111317;
border-radius:10px;
padding:16px
}

.title{
font-weight:750
}

.status{
display:inline-block;
margin-top:12px;
border:1px solid #35393f;
border-radius:6px;
padding:5px 7px;
font-size:9px
}

.metric{
font-size:11px;
color:#9da3aa;
line-height:1.7;
margin-top:10px
}

.notice{
margin-top:25px;
border-top:1px solid #272a2f;
padding-top:15px;
color:#8b9198;
font-size:11px;
line-height:1.6
}

#progress{
margin-top:18px;
color:#bbb
}

</style>

</head>

<body>

<main>

<a href="/brains">
← FX Brains
</a>

<h1>
Model Training Center
</h1>

<div class="subtitle">

Choose a market and timeframe.

FX will train every machine-learning brain that requires training,
then test it on later data it was not allowed to see during training.

Models that fail remain failed.
FX does not automatically promote them.

</div>

<div class="controls">

<input
id="symbol"
value="AAPL"
placeholder="AAPL, BTC/USD, XAU/USD..."
>

<select id="timeframe">

<option value="1d">
Daily
</option>

<option value="4h">
4 Hours
</option>

<option value="1h">
1 Hour
</option>

</select>

<select id="horizon">

<option value="1">
Predict next period
</option>

<option value="3">
Next 3 periods
</option>

<option
value="5"
selected
>
Next 5 periods
</option>

<option value="10">
Next 10 periods
</option>

</select>

<button
class="primary"
onclick="trainAll()"
>
Train All Trainable Brains
</button>

</div>

<div id="progress">
Ready.
</div>

<div
id="grid"
class="grid"
></div>

<div class="notice">

TRAINED means the model learned from historical information.

OUT-OF-SAMPLE means FX tested it on later data that the model did not see during training.

WALK-FORWARD means FX repeatedly trained on the past and tested on the next unseen period.

None of these statuses automatically authorize real-money trading.

</div>

</main>

<script>

function pct(value){

    if(
        value === null
        || value === undefined
    ){
        return "—";
    }

    return (
        Number(value)
        * 100
    ).toFixed(2)
    + "%";
}


async function trainAll(){

    const symbol =
        document
        .getElementById(
            "symbol"
        )
        .value
        .trim();

    const timeframe =
        document
        .getElementById(
            "timeframe"
        )
        .value;

    const horizon =
        Number(
            document
            .getElementById(
                "horizon"
            )
            .value
        );

    const progress =
        document
        .getElementById(
            "progress"
        );

    progress.textContent =
        "Training and validating all trainable models. This may take several minutes on your Intel Mac.";

    document
        .getElementById(
            "grid"
        )
        .innerHTML = "";

    try{

        const response =
            await fetch(
                "/api/training/train-all",
                {
                    method:"POST",

                    headers:{
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify({
                            symbol,
                            timeframe,
                            horizon
                        })
                }
            );

        const data =
            await response.json();

        if(!data.ok){

            progress.textContent =
                data.message;

            return;
        }

        progress.textContent =
            "Training complete in "
            + data.result.elapsed_seconds
            + " seconds.";

        render(
            data.result.models
        );

    }

    catch{

        progress.textContent =
            "FX could not finish training. No trade was sent.";

    }

}


function render(models){

    const grid =
        document
        .getElementById(
            "grid"
        );

    models.forEach(
        model => {

            const card =
                document
                .createElement(
                    "div"
                );

            card.className =
                "card";

            const test =
                model.test_metrics;

            const walk =
                model.walk_forward;

            card.innerHTML = `

            <div class="title">
            ${model.model
                .replaceAll("_"," ")
                .toUpperCase()}
            </div>

            <div class="status">
            ${model.status}
            </div>

            <div class="metric">

            Unseen-data accuracy:
            ${pct(test.accuracy)}

            <br>

            Balanced accuracy:
            ${pct(
                test.balanced_accuracy
            )}

            <br>

            AUC:
            ${
                test.auc === null
                ? "—"
                : Number(
                    test.auc
                ).toFixed(3)
            }

            <br>

            Walk-forward AUC:
            ${
                walk.average_auc === null
                ? "—"
                : Number(
                    walk.average_auc
                ).toFixed(3)
            }

            </div>
            `;

            grid.appendChild(
                card
            );

        }
    );

}

</script>

</body>

</html>
"""
