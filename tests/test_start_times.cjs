const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const path=require('node:path');
const source=fs.readFileSync(path.join(__dirname,'../app.js'),'utf8');
const context={};vm.createContext(context);
for(const name of ['parseEasternTimestamp','entryStartMeta','entryStartMs','entryDisplayTime']){
 const start=source.indexOf('function '+name+'('),end=source.indexOf('\nfunction ',start+10);
 vm.runInContext(source.slice(start,end),context);
}
assert.match(context.entryDisplayTime('2026-11-20T00:30:00Z'),/Thu.*7:30 PM EST/);
assert.match(context.entryDisplayTime('2026-07-20T23:30:00Z'),/Mon.*7:30 PM EDT/);
assert.equal(context.entryDisplayTime('invalid'),'');
assert.equal(context.entryDisplayTime(''),'');
console.log('Start-time labels: weekday, Eastern winter/summer and missing values passed');
