import subprocess, sys
opts = subprocess.run([sys.executable, "ops/pinjs.py", sys.argv[1]], capture_output=True, text=True, check=True).stdout.strip()
print(opts + """
const csrf=document.cookie.match(/csrftoken=([^;]+)/)[1];
const body=new URLSearchParams({source_url:"/pin-creation-tool/",data:JSON.stringify({options,context:{}})});
const r=await fetch('/resource/PinResource/create/',{method:'POST',headers:{'X-CSRFToken':csrf,'X-Requested-With':'XMLHttpRequest','Content-Type':'application/x-www-form-urlencoded'},body});
const j=await r.json(); r.status+' '+(j.resource_response?.data?.id||JSON.stringify(j.resource_response?.error).slice(0,300))""")
