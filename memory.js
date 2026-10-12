/* Pure evidence state. No claim is made about hidden ground-truth locations. */
(function(root){
function iou(a,b){const x=Math.max(a[0],b[0]),y=Math.max(a[1],b[1]),r=Math.min(a[0]+a[2],b[0]+b[2]),d=Math.min(a[1]+a[3],b[1]+b[3]);const i=Math.max(0,r-x)*Math.max(0,d-y);return i/(a[2]*a[3]+b[2]*b[3]-i||1);}
function choose(p,t){return {label:p.class,box:p.bbox.slice(),score:p.score,lastSeen:t,state:'visible',candidate:null};}
function update(m,pred,t){if(!m)return null;const same=pred.filter(p=>p.class===m.label).sort((a,b)=>iou(b.bbox,m.box)-iou(a.bbox,m.box));const best=same[0];const ambiguous=same.length>1&&iou(same[1].bbox,m.box)>.2;const continuous=m.state==='visible'&&t-m.lastSeen<1200;
if(continuous&&best&&iou(best.bbox,m.box)>.25&&!ambiguous)return choose(best,t);
const lostFor=t-m.lastSeen;if(lostFor<1000&&m.state==='visible')return {...m,state:'visible',candidate:null,stale:true};
return {...m,state:best?'candidate':'unobserved',candidate:same.length===1?best:null,stale:false,ambiguous:same.length>1};}
const api={iou,choose,update};if(typeof module!=='undefined')module.exports=api;root.VisualMemory=api;
})(typeof window!=='undefined'?window:globalThis);
