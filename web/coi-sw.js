// Service worker que añade las cabeceras de "aislamiento de origen cruzado".
// Sin ellas el navegador no permite usar varios hilos del procesador (SharedArrayBuffer),
// y los modelos en modo CPU corren en un solo hilo, mucho más lento. GitHub Pages no deja poner estas cabeceras.
self.addEventListener('install',()=>self.skipWaiting());
self.addEventListener('activate',e=>e.waitUntil(self.clients.claim()));
self.addEventListener('fetch',e=>{
  const r=e.request;
  if(r.cache==='only-if-cached'&&r.mode!=='same-origin')return;
  e.respondWith(fetch(r).then(res=>{
    if(res.status===0)return res;
    const h=new Headers(res.headers);
    h.set('Cross-Origin-Embedder-Policy','credentialless');
    h.set('Cross-Origin-Opener-Policy','same-origin');
    return new Response(res.body,{status:res.status,statusText:res.statusText,headers:h});
  }).catch(()=>Response.error()));
});
