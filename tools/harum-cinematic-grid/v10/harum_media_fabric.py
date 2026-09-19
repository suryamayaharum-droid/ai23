#!/usr/bin/env python3
from __future__ import annotations
import argparse, concurrent.futures, json, subprocess, sys, time, os
from pathlib import Path

def runshot(engine,image,out,preset,duration):
    p=subprocess.run([sys.executable,engine,image,'--out',str(out),'--duration',str(duration),'--fps','24','--preset',preset],capture_output=True,text=True)
    if p.returncode: raise RuntimeError(p.stderr[-3000:])
    return {'out':str(out),'meta':json.loads(p.stdout)}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('image');ap.add_argument('--out',default='HARUM_CPU_FILM_v10.mp4');a=ap.parse_args()
    here=Path(__file__).resolve().parent; engine=str(here/'harum_cpu_cinema.py'); tmp=here/'runtime'/'shots';tmp.mkdir(parents=True,exist_ok=True)
    specs=[('left',2.2),('push',2.4),('right',2.2),('breath',2.2)]
    workers=min(2,max(1,(os.cpu_count() or 2)//2));t=time.perf_counter();results=[None]*len(specs)
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as ex:
        fs={ex.submit(runshot,engine,a.image,tmp/f'{i:02d}.mp4',pr,d):i for i,(pr,d) in enumerate(specs)}
        for f in concurrent.futures.as_completed(fs):results[fs[f]]=f.result()
    concat=tmp/'concat.txt';concat.write_text(''.join(f"file '{Path(r['out']).resolve().as_posix()}'\n" for r in results),encoding='utf-8')
    visual=tmp/'visual.mp4'
    subprocess.run(['ffmpeg','-y','-f','concat','-safe','0','-i',str(concat),'-c:v','libx264','-preset','veryfast','-crf','19','-vf','scale=1080:1920:flags=lanczos','-an',str(visual)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    duration=sum(d for _,d in specs)
    filt=f"anoisesrc=color=pink:amplitude=0.012:duration={duration}:sample_rate=48000,lowpass=f=3600,highpass=f=65,afade=t=in:st=0:d=1,afade=t=out:st={duration-1}:d=1"
    subprocess.run(['ffmpeg','-y','-i',str(visual),'-f','lavfi','-i',filt,'-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','144k','-shortest','-movflags','+faststart',a.out],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration,size:stream=codec_name,width,height,r_frame_rate','-of','json',a.out],text=True))
    print(json.dumps({'output':str(Path(a.out).resolve()),'render_seconds':round(time.perf_counter()-t,3),'workers':workers,'shots':len(specs),'probe':probe},indent=2))
if __name__=='__main__':main()
