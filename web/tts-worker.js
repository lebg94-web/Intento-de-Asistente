/* Voz Piper en un hilo aparte (no congela la cara ni el chat).
   Pasos: texto -> fonemas (espeak-ng en wasm) -> modelo VITS (onnxruntime-web) -> audio. */
const HF='https://huggingface.co/diffusionstudio/piper-voices/resolve/main/';
const PHON='https://cdn.jsdelivr.net/npm/@diffusionstudio/piper-wasm@1.0.0/build/piper_phonemize';
const ORT='https://cdn.jsdelivr.net/npm/onnxruntime-web@1.18.0/dist/';
let cur=null,createPhon=null;
importScripts(ORT+'ort.wasm.min.js');
ort.env.wasm.wasmPaths=ORT;
ort.env.wasm.numThreads=self.crossOriginIsolated?2:1;
ort.env.wasm.proxy=false;

// Descarga con progreso y guarda en Cache Storage (la próxima vez no se vuelve a bajar).
async function cached(url,sizeHint,tag){
  const cache=await caches.open('piper-v1');
  let r=await cache.match(url);
  if(!r){
    const res=await fetch(url);
    if(!res.ok)throw new Error('descarga falló ('+res.status+')');
    const total=+res.headers.get('content-length')||sizeHint||0;
    const rd=res.body.getReader();const parts=[];let loaded=0;
    for(;;){const{done,value}=await rd.read();if(done)break;parts.push(value);loaded+=value.length;
      if(tag)postMessage({type:'progress',tag,loaded,total})}
    r=new Response(new Blob(parts));
    await cache.put(url,r.clone());
  }
  return r;
}

async function load(path,sizeHint){
  const cfg=await(await cached(HF+path+'.json',0,null)).json();
  const buf=await(await cached(HF+path,sizeHint,'voz')).arrayBuffer();
  postMessage({type:'progress',tag:'motor',loaded:0,total:1});
  const session=await ort.InferenceSession.create(new Uint8Array(buf),{executionProviders:['wasm']});
  if(!createPhon)createPhon=(await import('./vendor/piper/piper-phonemize.js')).createPiperPhonemize;
  cur={cfg,session};
}

async function phonemize(text,voice){
  return new Promise(async(resolve,reject)=>{
    try{
      const m=await createPhon({
        print:l=>{try{resolve(JSON.parse(l).phoneme_ids)}catch(e){reject(e)}},
        printErr:l=>reject(new Error(l)),
        locateFile:l=>l.endsWith('.wasm')?PHON+'.wasm':l.endsWith('.data')?PHON+'.data':l
      });
      m.callMain(['-l',voice,'--input',JSON.stringify([{text:text.trim()}]),'--espeak_data','/espeak-ng-data']);
    }catch(e){reject(e)}
  });
}

async function synth(text,speed){
  const{cfg,session}=cur;
  const ids=await phonemize(text,cfg.espeak.voice);
  const inf=cfg.inference||{};
  const feeds={
    input:new ort.Tensor('int64',BigInt64Array.from(ids,BigInt),[1,ids.length]),
    input_lengths:new ort.Tensor('int64',BigInt64Array.from([BigInt(ids.length)]),[1]),
    scales:new ort.Tensor('float32',Float32Array.from([inf.noise_scale??.667,(inf.length_scale??1)/(speed||1),inf.noise_w??.8]),[3])
  };
  if(cfg.num_speakers>1)feeds.sid=new ort.Tensor('int64',BigInt64Array.from([0n]),[1]);
  const out=await session.run(feeds);
  const data=out.output.data;
  return{samples:new Float32Array(data),rate:cfg.audio.sample_rate};
}

onmessage=async e=>{
  const m=e.data;
  try{
    if(m.type==='load'){await load(m.path,m.size);postMessage({type:'ready'})}
    else if(m.type==='synth'){const r=await synth(m.text,m.speed);postMessage({type:'audio',id:m.id,samples:r.samples,rate:r.rate},[r.samples.buffer])}
  }catch(err){postMessage({type:'error',id:m.id,message:String(err&&err.message||err)})}
};
