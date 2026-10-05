import ssl, edge_tts.communicate as _c; _c._SSL_CTX = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt")
import asyncio, json, edge_tts, subprocess
lines=json.load(open("vo/lines.json"))
async def main():
    for k,t in lines:
        await edge_tts.Communicate(t,"ml-IN-SobhanaNeural",rate="+8%").save(f"vo/{k}.mp3")
        d=subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f"vo/{k}.mp3"],capture_output=True,text=True).stdout.strip()
        print(k,d)
asyncio.run(main())
