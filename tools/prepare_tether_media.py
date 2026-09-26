"""Publish the recorded suspended-load film and render a matching silent hero."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys
import imageio_ffmpeg
import mujoco
import numpy as np
from PIL import Image,ImageDraw

SITE=Path(__file__).resolve().parents[1]
DEMO=SITE.parent/'gpt_try/tether_demo'
sys.path.insert(0,str(DEMO))
import render_tether as replay

def main():
    video=SITE/'static/videos';images=SITE/'static/images'
    source=DEMO/'output'
    shutil.copyfile(source/'apcl-suspended-load.mp4',video/'apcl-demo.mp4')
    shutil.copyfile(source/'tether-poster.jpg',images/'demo-poster.jpg')
    shutil.copyfile(source/'tether-ko.vtt',video/'apcl-demo-ko.vtt')
    shutil.copyfile(source/'tether_episode.json',SITE/'static/data/tether_episode.json')
    shutil.copyfile(source/'verification.json',SITE/'static/data/tether_verification.json')
    replay.DATA=np.load(source/'tether_episode.npz')
    replay.META=json.loads((source/'tether_episode.json').read_text(encoding='utf-8'))
    model=replay.model_for_replay();data=mujoco.MjData(model)
    renderer=mujoco.Renderer(model,width=640,height=740)
    def frame(t):
        for name in ('none','full'):
            simt,stage=replay.timeline(t,name);tr=replay.DATA[name+'_trajectory']
            q=np.array([np.interp(simt,tr[:,0],tr[:,j+1]) for j in range(14)])
            for j in range(7):data.qpos[int(model.joint(f'{name}_j{j+1}').qposadr[0])]=q[j]
            adr=int(model.joint(name+'_load_free').qposadr[0])
            data.qpos[adr:adr+3]=q[7:10]+replay.OFFSETS[name]
            data.qpos[adr+3:adr+7]=q[10:14]/np.linalg.norm(q[10:14])
        mujoco.mj_forward(model,data)
        im=Image.new('RGB',(1280,1000),replay.BG)
        for name,x in [('none',0),('full',640)]:
            cam=mujoco.MjvCamera();cam.lookat[:]=replay.OFFSETS[name]+[.20,-.025,.40]
            cam.distance=1.46;cam.azimuth=replay.AZIMUTH;cam.elevation=-18
            renderer.update_scene(data,camera=cam)
            panel=Image.fromarray(renderer.render())
            sid=model.site(name+'_tcp').id;R=data.site_xmat[sid].reshape(3,3);o=data.site_xpos[sid]
            truth=o+R@replay.DATA['contact'];s=replay.snapshot(name,stage)
            color=replay.CORAL if name=='none' else replay.TEAL
            if s is not None:
                estimate=o+R@s[2]
                replay.markers(panel,replay.project(renderer.scene,truth,640,740),
                               replay.project(renderer.scene,estimate,640,740),color,True)
            im.paste(panel,(x,142))
            d=ImageDraw.Draw(im)
            title='CPF / NO RECOVERY' if name=='none' else 'APCL'
            width=d.textlength(title,font=replay.font(24,True))
            d.text((x+320-width/2,112),title,font=replay.font(24,True),fill=color)
            label=f'{replay.META["results"][name]["err"]*1000:.1f} mm' if stage==5 else '0.90 kg suspended load'
            size=32 if stage==5 else 19
            width=d.textlength(label,font=replay.font(size,True))
            d.text((x+320-width/2,836),label,font=replay.font(size,True),fill=color if stage==5 else replay.MUTED)
        d=ImageDraw.Draw(im)
        label=['SAME LOAD. UNKNOWN ATTACHMENT.','ONE VIEW. MANY POSSIBLE POINTS.',
               'PRESERVE THE UNRESOLVED DIRECTION.','TILT THE OBJECT. KEEP THE ATTACHMENT.',
               'SETTLE. THEN MEASURE AGAIN.','TWO VIEWS. TWO ESTIMATES.'][stage]
        width=d.textlength(label,font=replay.font(22,True))
        d.text(((1280-width)/2,41),label,font=replay.font(22,True),fill=replay.INK)
        note='Gold: true attachment   /   Diamond: estimate'
        width=d.textlength(note,font=replay.font(18))
        d.text(((1280-width)/2,915),note,font=replay.font(18),fill=replay.MUTED)
        return im
    ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
    dest=video/'apcl-hero.mp4'
    encoder=subprocess.Popen([ffmpeg,'-y','-hide_banner','-loglevel','warning','-f','rawvideo',
                              '-pix_fmt','rgb24','-s','1280x1000','-r','24','-i','-',
                              '-an','-c:v','libx264','-preset','fast','-crf','20','-pix_fmt','yuv420p',
                              '-movflags','+faststart',str(dest)],stdin=subprocess.PIPE)
    try:
        for k in range(720):
            im=frame(k/24);encoder.stdin.write(im.tobytes())
            if k==26*24:im.save(images/'hero-poster.jpg',quality=94)
            if k%120==0:print(f'Hero: {k}/720',flush=True)
    finally:
        encoder.stdin.close();renderer.close()
    assert encoder.wait()==0
    subprocess.run([ffmpeg,'-y','-hide_banner','-loglevel','error','-ss','26','-i',str(video/'apcl-demo.mp4'),
                    '-frames:v','1','-vf','scale=1200:675,crop=1200:630:0:0','-q:v','2',str(images/'social-card.jpg')],check=True)
    paths=[video/'apcl-demo.mp4',dest,images/'hero-poster.jpg',images/'demo-poster.jpg']
    manifest={p.relative_to(SITE).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    (SITE/'static/data/tether_media.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print('Updated film, hero loop, posters and Korean captions.',flush=True)

if __name__=='__main__':main()
