import fs from "node:fs/promises";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const outputDir = "/Users/macmac/Documents/Codex/FX/outputs/fx-trade-tracker";
const outputPath = outputDir + "/FX_Trade_Tracker.xlsx";
const lastRow = 504;
const wb = Workbook.create();
const dark = "#111827", ink = "#111827", muted = "#64748B", pale = "#F1F5F9", white = "#FFFFFF";
const green = "#047857", red = "#B91C1C";
const money = '$#,##0.00;[Red]($#,##0.00);-';
const pct = '0.00%;[Red](0.00%);-';

const names = ["Dashboard","Bots","Daily Log","All Trades","Forex","Commodities","Indices","Stocks","Crypto","ETFs","Futures","Open Positions","Cash Flows","Sync Status","Fills","Config"];
const sheets = Object.fromEntries(names.map(name => [name, wb.worksheets.add(name)]));

function title(sheet, text, subtitle, endCol="H") {
  sheet.showGridLines = false;
  sheet.getRange("A1:"+endCol+"1").merge();
  sheet.getRange("A1").values = [[text]];
  sheet.getRange("A1:"+endCol+"1").format = {fill:dark,font:{bold:true,color:white,size:18},rowHeight:31,verticalAlignment:"center"};
  sheet.getRange("A2:"+endCol+"2").merge();
  sheet.getRange("A2").values = [[subtitle]];
  sheet.getRange("A2:"+endCol+"2").format = {font:{color:muted,italic:true,size:10},rowHeight:25,wrapText:true};
}
function header(sheet, address) {
  sheet.getRange(address).format = {fill:pale,font:{bold:true,color:ink},rowHeight:42,verticalAlignment:"center",wrapText:true,borders:{bottom:{style:"thin",color:"#CBD5E1"}}};
}
function standard(sheet, cols) {
  sheet.freezePanes.freezeRows(4);
  sheet.getRange("A:"+cols).format.font = {name:"Aptos",size:10};
  sheet.getRange("A:"+cols).format.columnWidth = 17;
}

title(sheets.Dashboard,"FX Trade Dashboard","Local database is authoritative · USD reporting · Asia/Dubai daily display · paper, research, and live remain separate","N");
sheets.Dashboard.getRange("A4:B13").values = [
  ["Metric","Value"],["Closed trades",null],["Trade win rate",null],["Breakeven trades",null],
  ["Net realized P&L",null],["Gross profit",null],["Gross loss",null],["Profit factor",null],
  ["Peak ending equity",null],["Latest ending equity",null]
];
sheets.Dashboard.getRange("B5:B13").formulas = [
  ["=COUNTIFS('All Trades'!$AB$5:$AB$504,\"CLOSED\",'All Trades'!$AC$5:$AC$504,\"<>LEGACY_UNVERIFIED\")"],
  ["=IF(B5=0,\"Unavailable\",COUNTIFS('All Trades'!$AB$5:$AB$504,\"CLOSED\",'All Trades'!$W$5:$W$504,\">0\",'All Trades'!$AC$5:$AC$504,\"<>LEGACY_UNVERIFIED\")/B5)"],
  ["=COUNTIFS('All Trades'!$AB$5:$AB$504,\"CLOSED\",'All Trades'!$W$5:$W$504,0,'All Trades'!$AC$5:$AC$504,\"<>LEGACY_UNVERIFIED\")"],
  ["=IF(B5=0,\"Unavailable\",SUMIFS('All Trades'!$W$5:$W$504,'All Trades'!$AB$5:$AB$504,\"CLOSED\",'All Trades'!$AC$5:$AC$504,\"<>LEGACY_UNVERIFIED\"))"],
  ["=IF(B5=0,\"Unavailable\",SUMIFS('All Trades'!$W$5:$W$504,'All Trades'!$AB$5:$AB$504,\"CLOSED\",'All Trades'!$W$5:$W$504,\">0\",'All Trades'!$AC$5:$AC$504,\"<>LEGACY_UNVERIFIED\"))"],
  ["=IF(B5=0,\"Unavailable\",ABS(SUMIFS('All Trades'!$W$5:$W$504,'All Trades'!$AB$5:$AB$504,\"CLOSED\",'All Trades'!$W$5:$W$504,\"<0\",'All Trades'!$AC$5:$AC$504,\"<>LEGACY_UNVERIFIED\")))"],
  ["=IF(OR(B5=0,B11=0),\"Unavailable\",B10/B11)"],
  ["=IF(COUNT('Daily Log'!$I$5:$I$504)=0,\"Unavailable\",MAX('Daily Log'!$I$5:$I$504))"],
  ["=IF(COUNT('Daily Log'!$I$5:$I$504)=0,\"Unavailable\",LOOKUP(2,1/('Daily Log'!$I$5:$I$504<>\"\"),'Daily Log'!$I$5:$I$504))"]
];
header(sheets.Dashboard,"A4:B4");sheets.Dashboard.getRange("B6").format.numberFormat=pct;sheets.Dashboard.getRange("B8:B13").format.numberFormat=money;
sheets.Dashboard.getRange("D4:N4").merge();sheets.Dashboard.getRange("D4").values=[["Filters and equity curve activate when verified records are synchronized. Empty cells mean unavailable, never zero performance."]];
sheets.Dashboard.getRange("D4:N6").format={fill:"#F8FAFC",font:{color:muted},wrapText:true,verticalAlignment:"center"};
sheets.Dashboard.getRange("A1:N20").format.font={name:"Aptos"};sheets.Dashboard.getRange("A:A").format.columnWidth=27;sheets.Dashboard.getRange("B:B").format.columnWidth=19;

const botHeaders=["Bot ID","Bot name","Asset focus","Strategy ID","Strategy version","Lifecycle state","Paper eligible","Readiness reason","Training runs","Last trained UTC","Net P&L","Closed trades","Win rate","Max drawdown","Owner ID"];
title(sheets.Bots,"Bot Readiness & Performance","A bot is available only after every required evidence gate passes.","O");
sheets.Bots.getRange("A4:O4").values=[botHeaders];header(sheets.Bots,"A4:O4");standard(sheets.Bots,"O");
sheets.Bots.getRange("A:O").format.columnWidth=15;sheets.Bots.getRange("H:H").format.columnWidth=48;

const dailyHeaders=["Date (Dubai)","Account ID","Mode","Starting balance","Deposits","Withdrawals","Net realized P&L","Unrealized P&L","Ending equity","Starting equity","Total daily P&L","Cash-flow adjusted return","High-water mark","Drawdown $","Drawdown %","Winning day","Data quality"];
title(sheets["Daily Log"],"Daily Balance & Equity","Ending equity includes open-position valuation. Cash flows are excluded from trading performance.","Q");
sheets["Daily Log"].getRange("A4:Q4").values=[dailyHeaders];header(sheets["Daily Log"],"A4:Q4");standard(sheets["Daily Log"],"Q");
sheets["Daily Log"].getRange("I5").formulasR1C1=[["=IF(RC[-8]=\"\",\"\",RC[-5]+RC[-4]-RC[-3]+RC[-2]+RC[-1])"]];sheets["Daily Log"].getRange("I5:I"+lastRow).fillDown();
sheets["Daily Log"].getRange("K5").formulasR1C1=[["=IF(OR(RC[-10]=\"\",RC[-1]=\"\"),\"\",RC[-2]-RC[-1]-RC[-6]+RC[-5])"]];sheets["Daily Log"].getRange("K5:K"+lastRow).fillDown();
sheets["Daily Log"].getRange("L5").formulasR1C1=[["=IF(OR(RC[-2]=\"\",RC[-2]=0),\"Unavailable\",RC[-1]/RC[-2])"]];sheets["Daily Log"].getRange("L5:L"+lastRow).fillDown();
sheets["Daily Log"].getRange("M5").formulasR1C1=[["=IF(RC[-4]=\"\",\"\",MAX(R5C9:RC[-4]))"]];sheets["Daily Log"].getRange("M5:M"+lastRow).fillDown();
sheets["Daily Log"].getRange("N5").formulasR1C1=[["=IF(OR(RC[-1]=\"\",RC[-5]=\"\"),\"\",RC[-1]-RC[-5])"]];sheets["Daily Log"].getRange("N5:N"+lastRow).fillDown();
sheets["Daily Log"].getRange("O5").formulasR1C1=[["=IF(OR(RC[-2]=\"\",RC[-2]=0),\"Unavailable\",RC[-1]/RC[-2])"]];sheets["Daily Log"].getRange("O5:O"+lastRow).fillDown();
sheets["Daily Log"].getRange("P5").formulasR1C1=[["=IF(RC[-5]=\"\",\"\",RC[-5]>0)"]];sheets["Daily Log"].getRange("P5:P"+lastRow).fillDown();
sheets["Daily Log"].getRange("A5:A"+lastRow).format.numberFormat="yyyy-mm-dd";sheets["Daily Log"].getRange("D5:O"+lastRow).format.numberFormat=money;sheets["Daily Log"].getRange("L5:L"+lastRow).format.numberFormat=pct;sheets["Daily Log"].getRange("O5:O"+lastRow).format.numberFormat=pct;

const tradeHeaders=["Trade ID","Bot ID","Strategy ID","Strategy version","Campaign ID","Account ID","Owner ID","Mode","Asset class","Exposure category","Ticker","Venue","Product type","Entry UTC","Exit UTC","Direction","Quantity","Quantity unit","Contract multiplier","Average entry","Average exit","Gross realized P&L","Net realized P&L","Unrealized P&L","Initial stop","Profit plan","Initial monetary risk","Status","Data quality","Commissions","Funding / financing","Currency conversion cost","Measured slippage","Planned reward-to-risk","Realized R-multiple","Exit reason","Holding seconds","Decision evidence","Manual notes"];
title(sheets["All Trades"],"Canonical Trade Ledger","Machine-managed canonical records. Manual notes are preserved in the final column.","AM");
sheets["All Trades"].getRange("A4:AM4").values=[tradeHeaders];header(sheets["All Trades"],"A4:AM4");standard(sheets["All Trades"],"AM");
sheets["All Trades"].getRange("AI5").formulasR1C1=[["=IF(OR(RC[-12]=\"\",RC[-8]=\"\",RC[-8]=0),\"Unavailable\",RC[-12]/RC[-8])"]];sheets["All Trades"].getRange("AI5:AI"+lastRow).fillDown();
sheets["All Trades"].getRange("N5:O"+lastRow).format.numberFormat="yyyy-mm-dd hh:mm:ss";sheets["All Trades"].getRange("T5:AI"+lastRow).format.numberFormat=money;sheets["All Trades"].getRange("AH5:AI"+lastRow).format.numberFormat="0.00x";
sheets["All Trades"].getRange("I5:I"+lastRow).dataValidation={rule:{type:"list",values:["Forex","Commodities","Indices","Stocks","Crypto","ETFs","Futures"]}};
sheets["All Trades"].getRange("H5:H"+lastRow).dataValidation={rule:{type:"list",values:["RESEARCH","LOCAL_PAPER","BROKER_PAPER","LIVE"]}};
sheets["All Trades"].getRange("AM:AM").format.columnWidth=38;

for (const asset of ["Forex","Commodities","Indices","Stocks","Crypto","ETFs","Futures"]) {
  const sh=sheets[asset];title(sh,asset+" Trades","Filtered reporting view. Totals must always reconcile to All Trades; do not sum overlapping category tabs.","L");
  sh.getRange("A4:L4").values=[["Trade ID","Bot ID","Campaign ID","Ticker","Product type","Direction","Entry UTC","Exit UTC","Net P&L","Status","Data quality","Manual note"]];
  header(sh,"A4:L4");standard(sh,"L");sh.getRange("A5:L5").merge();sh.getRange("A5").values=[["FX synchronization populates this view from canonical records. No verified "+asset.toLowerCase()+" trades are currently available."]];sh.getRange("A5:L5").format={font:{color:muted,italic:true},rowHeight:28};
}

const openHeaders=["Trade ID","Bot ID","Campaign ID","Asset class","Ticker","Venue","Direction","Quantity","Average entry","Last price","Initial stop","Profit plan","Maximum loss","Unrealized P&L","Protection status","Last valued UTC"];
title(sheets["Open Positions"],"Open Positions","Every position must retain protection. Missing valuation is labelled unavailable.","P");sheets["Open Positions"].getRange("A4:P4").values=[openHeaders];header(sheets["Open Positions"],"A4:P4");standard(sheets["Open Positions"],"P");
title(sheets["Cash Flows"],"Cash Flows","Deposits, withdrawals, and internal allocations are recorded separately from trading P&L.","I");sheets["Cash Flows"].getRange("A4:I4").values=[["Cash flow ID","Timestamp UTC","Account ID","Type","Amount","Currency","USD amount","Conversion evidence","Notes"]];header(sheets["Cash Flows"],"A4:I4");standard(sheets["Cash Flows"],"I");
title(sheets["Sync Status"],"Synchronization Status","Local records commit first. Cloud reporting failures never delay protective execution.","H");sheets["Sync Status"].getRange("A4:H4").values=[["Destination","Last attempt UTC","Last success UTC","Pending records","Status","Error summary","Reconciliation difference","Workbook ID"]];header(sheets["Sync Status"],"A4:H4");sheets["Sync Status"].getRange("A5:H5").values=[["Google Sheets",null,null,0,"CONNECTED via Composio","No verified local trades are currently eligible for export.",0,"1NAgM6_NQzRJsiljK6-i5cghlJcds3VqTUl8OJwMuKHU"]];standard(sheets["Sync Status"],"H");
sheets["Sync Status"].getRange("F:F").format.columnWidth=48;sheets["Sync Status"].getRange("H:H").format.columnWidth=42;
title(sheets.Fills,"Fill-Level Support","Protected support tab. Partial fills and exits remain linked to their parent trade.","N");sheets.Fills.getRange("A4:N4").values=[["Fill ID","Trade ID","Order ID","Execution ID","Timestamp UTC","Side","Quantity","Price","Commission","Measured slippage","Venue","Liquidity role","Record version","Source evidence"]];header(sheets.Fills,"A4:N4");standard(sheets.Fills,"N");
title(sheets.Config,"Tracker Configuration","Machine-managed configuration and auditable reporting conventions.","C");sheets.Config.getRange("A4:C12").values=[["Setting","Value","Meaning"],["Reporting currency","USD","Native amounts and conversion evidence remain preserved."],["Display timezone","Asia/Dubai","All stored event timestamps remain UTC."],["Trade probability gate",0.85,"Calibrated probability of profitable completion after costs."],["Cost ceiling",0.30,"Maximum costs as a share of planned gross winning payoff."],["Canonical source","Local SQLite","Google Sheets is an authorized reporting copy."],["Legacy default","Excluded","Unprotected or unreliable legacy data is excluded by default."],["Live trading","Disabled","Requires a separate future activation process."],["Workbook schema version","1.0","Stable IDs and record versions prevent duplicate exports."]];header(sheets.Config,"A4:C4");sheets.Config.getRange("B7:B8").format.numberFormat=pct;sheets.Config.getRange("A:C").format.columnWidth=28;sheets.Config.getRange("C:C").format.columnWidth=60;

for (const sh of Object.values(sheets)) {
  const used=sh.getUsedRange();if(used){used.format.font={name:"Aptos",size:10};used.format.wrapText=false}
}
sheets.Dashboard.getRange("A1:N2").format.wrapText=true;sheets.Config.getRange("C5:C12").format.wrapText=true;
await fs.mkdir(outputDir,{recursive:true});
const file=await SpreadsheetFile.exportXlsx(wb);await file.save(outputPath);
const inspect=await wb.inspect({kind:"table",range:"Dashboard!A1:N15",include:"values,formulas",tableMaxRows:15,tableMaxCols:14});
console.log(inspect.ndjson);
const errors=await wb.inspect({kind:"match",searchTerm:"#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",options:{useRegex:true,maxResults:100},summary:"final formula error scan"});
console.log(errors.ndjson);
const preview=await wb.render({sheetName:"Dashboard",range:"A1:N15",scale:1.5,format:"png"});
await fs.writeFile(outputDir+"/dashboard-preview.png",new Uint8Array(await preview.arrayBuffer()));
const previewRanges = {
  "Bots":"A1:O8","Daily Log":"A1:Q8","All Trades":"A1:AM8","Forex":"A1:L7",
  "Commodities":"A1:L7","Indices":"A1:L7","Stocks":"A1:L7","Crypto":"A1:L7",
  "ETFs":"A1:L7","Futures":"A1:L7","Open Positions":"A1:P8","Cash Flows":"A1:I8",
  "Sync Status":"A1:H8","Fills":"A1:N8","Config":"A1:C12"
};
for (const [sheetName, range] of Object.entries(previewRanges)) {
  const image = await wb.render({sheetName,range,scale:0.75,format:"png"});
  await fs.writeFile(outputDir+"/preview-"+sheetName.toLowerCase().replaceAll(" ","-")+".png",new Uint8Array(await image.arrayBuffer()));
}
console.log(outputPath);
