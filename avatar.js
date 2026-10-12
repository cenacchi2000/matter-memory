import * as THREE from './three.module.js';
const host=document.getElementById('avatar');
try{
const scene=new THREE.Scene();scene.background=new THREE.Color('#d9dfdc');scene.fog=new THREE.Fog('#d9dfdc',8,15);
const renderer=new THREE.WebGLRenderer({antialias:true,alpha:false});renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.3;host.append(renderer.domElement);renderer.domElement.setAttribute('aria-label','Animated three-dimensional robot bust with grey face, blue eyes and mechanical neck');
const camera=new THREE.PerspectiveCamera(34,1,.1,30);camera.position.set(.1,1.6,4.6);camera.lookAt(0,1.36,0);
scene.add(new THREE.HemisphereLight('#f7ffff','#667775',2));
function light(color,intensity,pos){const l=new THREE.DirectionalLight(color,intensity);l.position.set(...pos);scene.add(l);return l;}
const key=light('#fff6e8',4,[3,5,5]);key.castShadow=true;key.shadow.mapSize.set(2048,2048);light('#c2defa',2,[-4,2,3]);light('#b4ccff',3,[-1,4,-3]);
const skin=new THREE.MeshPhysicalMaterial({color:'#9ea7a5',roughness:.56,metalness:.13,clearcoat:.15});const dark=new THREE.MeshStandardMaterial({color:'#20292a',roughness:.5,metalness:.65});const silver=new THREE.MeshStandardMaterial({color:'#c4cbd0',metalness:.87,roughness:.23});const black=new THREE.MeshStandardMaterial({color:'#0a1013',roughness:.4});const white=new THREE.MeshPhysicalMaterial({color:'#edece1',roughness:.24,clearcoat:1});const blue=new THREE.MeshPhysicalMaterial({color:'#178ec2',roughness:.22,metalness:.12,clearcoat:1});const lipmat=new THREE.MeshStandardMaterial({color:'#7c8888',roughness:.65});
function mesh(geo,mat,parent,x=0,y=0,z=0){const m=new THREE.Mesh(geo,mat);m.position.set(x,y,z);m.castShadow=true;m.receiveShadow=true;parent.add(m);return m;}
function oval(parent,mat,x,y,z,sx,sy,sz){const m=mesh(new THREE.SphereGeometry(1,64,48),mat,parent,x,y,z);m.scale.set(sx,sy,sz);return m;}
function rod(parent,a,b,r,mat){const va=new THREE.Vector3(...a),vb=new THREE.Vector3(...b),v=vb.clone().sub(va);const m=mesh(new THREE.CylinderGeometry(r,r,v.length(),24),mat,parent);m.position.copy(va.clone().add(vb).multiplyScalar(.5));m.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0),v.normalize());return m;}
function tube(parent,points,r,mat){const c=new THREE.CatmullRomCurve3(points.map(p=>new THREE.Vector3(...p)));return mesh(new THREE.TubeGeometry(c,64,r,12,false),mat,parent);}
const bust=new THREE.Group();scene.add(bust);const torso=new THREE.Group();bust.add(torso);
oval(torso,dark,0,.40,0,.68,.55,.30);oval(torso,silver,0,.3,.13,.47,.39,.22);
for(const s of [-1,1]){oval(torso,silver,s*.69,.59,0,.23,.27,.24);oval(torso,dark,s*.78,.60,.12,.13,.18,.14);rod(torso,[s*.64,.37,.08],[s*.64,.72,.03],.07,silver);for(let i=0;i<4;i++){rod(torso,[s*(.24+i*.055),.37,.3],[s*(.25+i*.07),.85,.12],.017,i%2?silver:dark);}tube(torso,[[s*.64,.78,0],[s*.43,.95,.04],[s*.18,1,.06]],.055,dark);for(let i=0;i<6;i++){oval(torso,dark,s*.48,.17+i*.09,.29,.022,.022,.018);}}
mesh(new THREE.CylinderGeometry(.34,.46,.08,64),dark,torso,0,.06,0);
// Exposed neck: central actuator, bilateral pistons, wiring and vertebral collars.
rod(bust,[0,.70,0],[0,1.22,0],.12,dark);for(let i=0;i<5;i++){mesh(new THREE.TorusGeometry(.13,.014,12,48),silver,bust,0,.80+i*.07,0).rotation.x=Math.PI/2;}
for(const s of [-1,1]){rod(bust,[s*.25,.77,.12],[s*.15,1.25,.02],.045,silver);rod(bust,[s*.23,.83,.11],[s*.14,1.20,.03],.023,dark);oval(bust,silver,s*.23,.8,.13,.07,.07,.06);tube(bust,[[s*.21,.77,-.09],[s*.24,.97,-.1],[s*.12,1.19,-.13]],.025,dark);}
const head=new THREE.Group();head.position.set(0,1.23,0);bust.add(head);
// A continuous, dense sculpted surface; front-facing z is positive.
const geo=new THREE.SphereGeometry(1,192,160),a=geo.attributes.position;
function G(x,y,cx,cy,sx,sy){return Math.exp(-(((x-cx)/sx)**2)-((y-cy)/sy)**2);}
for(let i=0;i<a.count;i++){let x=a.getX(i),y=a.getY(i),z=a.getZ(i);const yy=y*.68+.53;let xx=x*.48*(1-.13*Math.max(0,-y));let zz=z*.42;if(z>0){const mask=Math.pow(z,2);zz+=mask*(.03*G(xx,yy,0,.8,.4,.3)+.043*(G(xx,yy,-.25,.43,.16,.18)+G(xx,yy,.25,.43,.16,.18))-.065*(G(xx,yy,-.19,.69,.13,.10)+G(xx,yy,.19,.69,.13,.10))+.045*G(xx,yy,0,.29,.23,.12));}a.setXYZ(i,xx,yy,zz);}geo.computeVertexNormals();mesh(geo,skin,head);
// Eyes with iris rings, pupils, catchlights and articulated eyelids.
const eyes=[];for(const s of [-1,1]){const eye=new THREE.Group();eye.position.set(s*.188,.681,.34);head.add(eye);oval(eye,white,0,0,0,.116,.087,.087);const iris=oval(eye,blue,0,0,.081,.046,.046,.010);oval(eye,black,0,0,.092,.022,.025,.005);for(let j=0;j<28;j++){const angle=j*Math.PI*2/28;rod(eye,[Math.sin(angle)*.029,Math.cos(angle)*.029,.093],[Math.sin(angle)*.043,Math.cos(angle)*.043,.09],.0015,silver);}oval(eye,white,-.013,.017,.099,.007,.008,.003);
const lid=oval(head,skin,s*.188,.738,.372,.122,.017,.077);eyes.push({eye,lid});tube(head,[[s*.085,.701,.415],[s*.18,.760,.405],[s*.30,.701,.365]],.015,skin);tube(head,[[s*.085,.667,.414],[s*.18,.624,.41],[s*.30,.668,.365]],.012,skin);tube(head,[[s*.085,.823,.373],[s*.18,.849,.380],[s*.30,.817,.344]],.022,skin);
// Ear cartilage and inset auditory opening.
oval(head,skin,s*.477,.57,-.004,.07,.144,.085);oval(head,dark,s*.503,.572,.04,.028,.075,.028);tube(head,[[s*.49,.68,.045],[s*.53,.63,.07],[s*.525,.54,.068],[s*.48,.47,.04]],.019,skin);}
// Sculpted nasal bridge and alae.
oval(head,skin,0,.57,.413,.055,.125,.066);oval(head,skin,0,.474,.471,.082,.055,.074);for(const s of [-1,1]){oval(head,skin,s*.069,.453,.448,.045,.039,.049);oval(head,dark,s*.053,.434,.479,.023,.013,.012);}
const jaw=new THREE.Group();head.add(jaw);oval(jaw,skin,0,.162,.242,.252,.118,.16);const mouth=oval(head,black,0,.321,.424,.121,.016,.012);const upper=tube(head,[[-.128,.322,.413],[-.062,.338,.429],[0,.331,.439],[.062,.338,.429],[.128,.322,.413]],.014,lipmat);const lower=tube(jaw,[[-.125,.311,.413],[-.065,.297,.43],[0,.292,.435],[.065,.297,.43],[.125,.311,.413]],.018,skin);
// Thin panel seams communicate a manufactured face without replacing the facial surface.
for(const s of [-1,1])tube(head,[[s*.41,.95,.17],[s*.37,.86,.27],[s*.32,.82,.33]],.0035,dark);
const clock=new THREE.Clock();let drag=false,previousX=0,userYaw=0,gazeX=0,gazeY=0,nextBlink=2,blinkStart=-10;
renderer.domElement.style.touchAction='none';renderer.domElement.addEventListener('pointerdown',e=>{drag=true;previousX=e.clientX;renderer.domElement.setPointerCapture(e.pointerId);});renderer.domElement.addEventListener('pointermove',e=>{if(drag){userYaw=THREE.MathUtils.clamp(userYaw+(e.clientX-previousX)*.008,-.7,.7);previousX=e.clientX;}});renderer.domElement.addEventListener('pointerup',()=>drag=false);renderer.domElement.addEventListener('dblclick',()=>userYaw=0);
window.addEventListener('avatar-gaze',e=>{gazeX=e.detail.x;gazeY=e.detail.y;});
const resize=()=>{const w=host.clientWidth,h=host.clientHeight;renderer.setSize(w,h);camera.aspect=w/h;camera.updateProjectionMatrix();};new ResizeObserver(resize).observe(host);resize();
function animate(){const t=clock.getElapsedTime();const speaking=document.getElementById('amecaState')?.textContent.includes('SPEAKING');if(t>nextBlink){blinkStart=t;nextBlink=t+3+Math.random()*3;}const blink=Math.max(0,1-Math.abs(t-blinkStart-.09)/.09);head.rotation.y=userYaw+Math.sin(t*.4)*.035+gazeX*.08;head.rotation.x=Math.sin(t*.63)*.018-gazeY*.04;head.rotation.z=Math.sin(t*.37)*.014;torso.scale.y=1+Math.sin(t*1.3)*.003;for(const {eye,lid}of eyes){eye.rotation.y=gazeX*.12;eye.rotation.x=-gazeY*.09;lid.scale.y=.017+blink*.079;lid.position.y=.738-blink*.05;}const opening=speaking?(.5+.5*Math.sin(t*16))*(.5+.5*Math.sin(t*7)):.03;mouth.scale.y=.016+opening*.025;jaw.position.y=-opening*.025;renderer.render(scene,camera);}
renderer.setAnimationLoop(animate);host.dataset.status='ready';host.dataset.vertices=String(a.count);window.addEventListener('pagehide',()=>{renderer.setAnimationLoop(null);renderer.dispose();});
}catch(e){host.textContent='The 3D avatar could not start: '+e.message;host.dataset.status='error';}
