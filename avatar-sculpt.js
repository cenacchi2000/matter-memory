import * as T from './three.module.js';
const host=document.querySelector('#avatar');
try {
const scene=new T.Scene();scene.background=new T.Color('#628696');
const renderer=new T.WebGLRenderer({antialias:true});renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.ACESFilmicToneMapping;renderer.toneMappingExposure=1.05;host.append(renderer.domElement);renderer.domElement.setAttribute('aria-label','Original animated grey humanoid bust; drag to orbit and scroll to zoom');
const camera=new T.PerspectiveCamera(31,1,.01,50);let yaw=0,pitch=0,zoom=4.15;
scene.add(new T.HemisphereLight(0xdceaf4,0x293640,2.0));
for(const [c,i,x,y,z] of [[0xfff5e6,3,-3,5,4],[0xc4dfff,1.3,3,2,2],[0xe6efff,3,1,4,-3]]){const l=new T.DirectionalLight(c,i);l.position.set(x,y,z);scene.add(l);}
const skin=new T.MeshPhysicalMaterial({color:0x92999e,roughness:.74,metalness:.04,clearcoat:.06});
const frame=new T.MeshStandardMaterial({color:0x182125,metalness:.67,roughness:.46});
const steel=new T.MeshStandardMaterial({color:0xb8bfc2,metalness:.83,roughness:.29});
const matte=new T.MeshStandardMaterial({color:0x090e11,roughness:.8});
const white=new T.MeshPhysicalMaterial({color:0xd8d9d1,roughness:.23,clearcoat:.8});
const irisMat=new T.MeshPhysicalMaterial({color:0x6595ad,roughness:.27,metalness:.1});
const wireMat=new T.MeshStandardMaterial({color:0x8d7042,roughness:.6});
const root=new T.Group();scene.add(root);
function mesh(g,m,p=root,x=0,y=0,z=0){const o=new T.Mesh(g,m);o.position.set(x,y,z);p.add(o);return o;}
function oval(p,m,x,y,z,a,b,c){const o=mesh(new T.SphereGeometry(1,40,28),m,p,x,y,z);o.scale.set(a,b,c);return o;}
function rod(p,a,b,r,m=steel){const A=new T.Vector3(...a),B=new T.Vector3(...b),d=B.clone().sub(A);const o=mesh(new T.CylinderGeometry(r,r,d.length(),20),m,p);o.position.copy(A.add(B).multiplyScalar(.5));o.quaternion.setFromUnitVectors(new T.Vector3(0,1,0),d.normalize());return o;}
function curve(p,points,r,m=frame){return mesh(new T.TubeGeometry(new T.CatmullRomCurve3(points.map(a=>new T.Vector3(...a))),48,r,8,false),m,p);}
function bolt(p,x,y,z,r=.018){const o=mesh(new T.CylinderGeometry(r,r,.012,6),steel,p,x,y,z);o.rotation.x=Math.PI/2;mesh(new T.BoxGeometry(r*.9,.003,.004),matte,p,x,y,z+.008);}
function plate(p,pts,depth,material,z=0){const s=new T.Shape();pts.forEach(([x,y],i)=>i?s.lineTo(x,y):s.moveTo(x,y));s.closePath();const g=new T.ExtrudeGeometry(s,{depth,bevelEnabled:true,bevelThickness:.013,bevelSize:.012,bevelSegments:3,curveSegments:16});return mesh(g,material,p,0,0,z);}
// Open mechanical thorax, layered armor, shoulder bearings and actuator rails.
const body=new T.Group();root.add(body);
plate(body,[[-.28,.12],[-.39,.56],[-.27,.98],[.27,.98],[.39,.56],[.28,.12]],.19,frame,-.12);
for(const s of [-1,1]){
  const shoulder=mesh(new T.CylinderGeometry(.19,.19,.15,48),steel,body,s*.65,.77,0);shoulder.rotation.z=Math.PI/2;
  const bearing=mesh(new T.CylinderGeometry(.14,.14,.16,48),frame,body,s*.68,.77,0);bearing.rotation.z=Math.PI/2;
  oval(body,skin,s*.76,.75,.014,.075,.215,.19);
  plate(body,[[s*.39,.42],[s*.53,.48],[s*.59,.89],[s*.46,.94]],.08,steel,-.03);
  rod(body,[s*.53,.23,0],[s*.62,.63,0],.066,frame);
  rod(body,[s*.57,.23,.045],[s*.64,.63,.045],.031,steel);
  for(let j=0;j<3;j++)rod(body,[s*(.35+.037*j),.24,.17],[s*(.4+.034*j),.77,.12],.013,steel);
  curve(body,[[s*.58,.96,-.08],[s*.34,1.08,-.09],[s*.13,1.19,-.05]],.044,frame);
  for(let j=0;j<4;j++){curve(body,[[s*(.32+j*.02),.38,.06],[s*(.46+j*.012),.68,.015],[s*.31,.94,-.05]],.005,j%2?wireMat:matte);bolt(body,s*.46,.49+j*.105,.097,.015);}
  rod(body,[s*.47,.85,.09],[s*.26,1.09,.03],.026,steel);
}
// Sculpted sternum with annular speaker; no borrowed logo or mesh.
plate(body,[[-.23,.18],[-.30,.44],[-.23,.82],[-.13,.91],[.13,.91],[.23,.82],[.30,.44],[.23,.18]],.09,skin,.15);
const speaker=mesh(new T.CylinderGeometry(.105,.105,.026,64),matte,body,0,.53,.274);speaker.rotation.x=Math.PI/2;
mesh(new T.TorusGeometry(.11,.015,12,64),steel,body,0,.53,.288);
for(let y=-7;y<=7;y++)for(let x=-7;x<=7;x++)if(x*x+y*y<47)oval(body,steel,x*.012,.53+y*.012,.289,.0025,.0025,.0015);
for(const s of [-1,1])for(const y of [.28,.74])bolt(body,s*.20,y,.261,.013);
// Neck yoke and exposed tendons.
rod(root,[0,.95,-.035],[0,1.38,-.035],.082,matte);
for(let j=0;j<4;j++){const ring=mesh(new T.TorusGeometry(.084,.009,8,40),steel,root,0,1.04+j*.066,-.035);ring.rotation.x=Math.PI/2;}
for(const s of [-1,1]){
  rod(root,[s*.21,.93,.11],[s*.12,1.4,.01],.028,steel);
  rod(root,[s*.22,1.02,-.10],[s*.17,1.43,-.10],.036,frame);
  curve(root,[[s*.22,.98,.12],[s*.13,1.13,.14],[s*.15,1.36,.09]],.043,frame);
  oval(root,steel,s*.2,1.01,.13,.035,.035,.035);
}
const head=new T.Group();head.position.y=1.34;root.add(head);
// Cross-section sculpt. Face, cheeks, nose, lips and chin share one surface.
// Coordinates are authored here, not a downloaded or extracted robot asset.
const sections=[[-.015,.025,.055,.0],[.045,.105,.13,.01],[.13,.18,.205,.0],[.23,.235,.245,0],[.35,.272,.256,-.015],[.47,.288,.262,-.027],[.60,.292,.264,-.035],[.72,.285,.268,-.035],[.85,.25,.248,-.035],[.94,.19,.206,-.035],[1.0,.10,.12,-.035],[1.025,.002,.004,-.035]];
function section(y){let i=0;while(i<sections.length-2&&y>sections[i+1][0])i++;const a=sections[i],b=sections[i+1],t=T.MathUtils.clamp((y-a[0])/(b[0]-a[0]),0,1);const prev=sections[Math.max(0,i-1)],next=sections[Math.min(sections.length-1,i+2)];return [1,2,3].map(k=>{const m0=(b[k]-prev[k])/(b[0]-prev[0])*(b[0]-a[0]),m1=(next[k]-a[k])/(next[0]-a[0])*(b[0]-a[0]);return (2*t*t*t-3*t*t+1)*a[k]+(t*t*t-2*t*t+t)*m0+(-2*t*t*t+3*t*t)*b[k]+(t*t*t-t*t)*m1;});}
const G=(x,y,cx,cy,sx,sy)=>Math.exp(-(((x-cx)/sx)**2)-((y-cy)/sy)**2);
function sculpt(x,y,z){
 return z + .017*G(x,y,0,.73,.22,.16)
 -.033*(G(x,y,-.122,.605,.078,.06)+G(x,y,.122,.605,.078,.06))
 +.034*(G(x,y,-.16,.46,.082,.11)+G(x,y,.16,.46,.082,.11))
 +.065*G(x,y,0,.525,.035,.12)+.112*G(x,y,0,.425,.045,.037)
 +.037*(G(x,y,-.044,.409,.023,.024)+G(x,y,.044,.409,.023,.024))
 -.014*G(x,y,0,.365,.022,.04)
 +.024*G(x,y,0,.321,.105,.016)+.034*G(x,y,0,.289,.092,.02)
 +.043*G(x,y,0,.165,.105,.065);
}
const verts=[],indices=[],uvs=[],rows=220,cols=280;
for(let j=0;j<=rows;j++){const y=-.015+j*1.04/rows,[w,d,c]=section(y);for(let i=0;i<=cols;i++){const a=i/cols*2*Math.PI,x=w*Math.sin(a);let z=c+d*Math.cos(a);if(Math.cos(a)>0)z=sculpt(x,y,z);verts.push(x,y,z);uvs.push(i/cols,j/rows);}}
const aperture=(x,y,z)=>z>0&&((Math.abs(x-.12)/.073)**2+((y-.605)/.027)**2<1||(Math.abs(x+.12)/.073)**2+((y-.605)/.027)**2<1);
for(let j=0;j<rows;j++)for(let i=0;i<cols;i++){const k=j*(cols+1)+i;const ids=[k,k+1,k+cols+1,k+cols+2];const x=ids.reduce((s,k)=>s+verts[k*3],0)/4,y=ids.reduce((s,k)=>s+verts[k*3+1],0)/4,z=ids.reduce((s,k)=>s+verts[k*3+2],0)/4;if(aperture(x,y,z))continue;indices.push(k,k+1,k+cols+1,k+1,k+cols+2,k+cols+1);}
const geo=new T.BufferGeometry();geo.setAttribute('position',new T.Float32BufferAttribute(verts,3));geo.setAttribute('uv',new T.Float32BufferAttribute(uvs,2));geo.setIndex(indices);geo.computeVertexNormals();const face=mesh(geo,skin,head);const base=Float32Array.from(verts);
const eyes=[];
for(const s of [-1,1]){
 const e=new T.Group();e.position.set(s*.12,.605,.188);head.add(e);
 oval(e,white,0,0,0,.073,.048,.052);
 oval(e,irisMat,0,0,.049,.024,.024,.006);
 mesh(new T.TorusGeometry(.023,.002,8,48),frame,e,0,0,.055);
 for(let n=0;n<40;n++){const a=n*Math.PI/20;rod(e,[Math.sin(a)*.011,Math.cos(a)*.011,.057],[Math.sin(a)*.022,Math.cos(a)*.022,.055],.00065,n%2?frame:steel);}
 oval(e,matte,0,0,.058,.010,.011,.002);oval(e,white,-.008,.009,.061,.004,.004,.001);
 const lids=[];
 for(const upper of [true,false]){const ps=[];for(let n=0;n<=24;n++){const a=n/24*Math.PI;const x=s*.12-.073*Math.cos(a),y=.605+(upper?1:-1)*.027*Math.sin(a);const [w,d,c]=section(y);const z=sculpt(x,y,c+d*Math.sqrt(Math.max(0,1-(x/w)**2)));ps.push([x,y,z+.001]);}lids.push(curve(head,ps,.006,skin));}
 // Closed lid surface sits behind open aperture until blink.
 const lid=oval(head,skin,s*.12,.631,.210,.074,.004,.036);
 curve(head,[[s*.053,.67,.222],[s*.11,.69,.224],[s*.19,.674,.195]],.008,skin);
 oval(head,skin,s*.29,.505,-.005,.040,.090,.058);oval(head,frame,s*.314,.51,.029,.012,.045,.018);
 curve(head,[[s*.30,.58,.034],[s*.325,.55,.045],[s*.325,.47,.043],[s*.30,.44,.031]],.009,skin);
 curve(head,[[s*.25,.80,.079],[s*.258,.735,.103],[s*.223,.699,.155]],.0017,frame);
 eyes.push({eye:e,lid,lids});
 oval(head,matte,s*.032,.397,.332,.012,.006,.007);
}
const mouth=curve(head,[[-.102,.308,.247],[-.064,.306,.267],[0,.305,.281],[.064,.306,.267],[.102,.308,.247]],.0028,matte);
for(const s of [-1,1])curve(head,[[s*.263,.40,.09],[s*.213,.23,.144],[s*.13,.115,.183],[0,.089,.195]],.0014,frame);
const grid=new T.GridHelper(8,40,0x849fa9,0x6e909e);grid.position.y=.05;scene.add(grid);
let gazeX=0,gazeY=0,drag=false,px=0,py=0,blinkAt=2,blinkStart=-10,manualTalk=0;const clock=new T.Clock();
renderer.domElement.style.touchAction='none';renderer.domElement.addEventListener('pointerdown',e=>{drag=true;px=e.clientX;py=e.clientY;renderer.domElement.setPointerCapture(e.pointerId);});renderer.domElement.addEventListener('pointermove',e=>{if(drag){yaw=T.MathUtils.clamp(yaw+(e.clientX-px)*.008,-1.1,1.1);pitch=T.MathUtils.clamp(pitch+(e.clientY-py)*.004,-.25,.25);px=e.clientX;py=e.clientY;}});renderer.domElement.addEventListener('pointerup',()=>drag=false);renderer.domElement.addEventListener('pointercancel',()=>drag=false);renderer.domElement.addEventListener('wheel',e=>{e.preventDefault();zoom=T.MathUtils.clamp(zoom+e.deltaY*.002,2.7,5.5);},{passive:false});
window.addEventListener('avatar-gaze',e=>{gazeX=T.MathUtils.clamp(e.detail.x,-1,1);gazeY=T.MathUtils.clamp(e.detail.y,-1,1);});
document.querySelector('#avatarReset')?.addEventListener('click',()=>{yaw=pitch=0;zoom=4.15;});document.querySelector('#avatarTalk')?.addEventListener('click',()=>{manualTalk=clock.getElapsedTime()+4;});
const resize=()=>{renderer.setSize(host.clientWidth,host.clientHeight);camera.aspect=host.clientWidth/host.clientHeight;camera.updateProjectionMatrix();};const ro=new ResizeObserver(resize);ro.observe(host);resize();
let frameNo=0;function animate(){const t=clock.getElapsedTime();if(t>blinkAt){blinkStart=t;blinkAt=t+3+Math.random()*3;}const blink=Math.max(0,Math.sin(Math.min(Math.max((t-blinkStart)/.2,0),1)*Math.PI));const talking=t<manualTalk||document.querySelector('#amecaState')?.textContent.includes('SPEAKING');const open=talking?(.5+.5*Math.sin(t*14))*(.4+.6*Math.abs(Math.sin(t*5))):0;
 camera.position.set(Math.sin(yaw)*zoom,1.37+pitch*zoom,Math.cos(yaw)*zoom);camera.lookAt(0,1.30,0);head.rotation.y=gazeX*.15+Math.sin(t*.33)*.022;head.rotation.x=-gazeY*.08+Math.sin(t*.51)*.008;
 for(const {eye,lid}of eyes){eye.rotation.y=gazeX*.16;eye.rotation.x=-gazeY*.12;lid.scale.y=.004+blink*.030;lid.position.y=.631-blink*.026;}
 const a=geo.attributes.position;for(let i=0;i<a.count;i++){const x=base[i*3],y=base[i*3+1],z=base[i*3+2];const w=z>0?G(x,y,0,.235,.15,.095):0;a.setY(i,y-open*.016*w);a.setZ(i,z-open*.005*w);}a.needsUpdate=true;if(frameNo++%3===0)geo.computeVertexNormals();mouth.scale.y=1+open*.024;mouth.position.y=-open*.004;
 renderer.render(scene,camera);host.dataset.frames=String(frameNo);
}
renderer.setAnimationLoop(animate);host.dataset.status='ready';host.dataset.vertices=String(geo.attributes.position.count);host.dataset.design='original-cross-section-sculpt';
window.addEventListener('pagehide',()=>{renderer.setAnimationLoop(null);ro.disconnect();scene.traverse(o=>{o.geometry?.dispose();});renderer.dispose();});
}catch(e){host.textContent='Avatar could not start: '+e.message;host.dataset.status='error';}
