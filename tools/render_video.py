"""Render the captured experiment, with measured posterior snapshots.

Robot visuals: MuJoCo Menagerie / Franka FR3 (see THIRD_PARTY.md).
Only the recorded q trajectory is replayed; rendering does not alter the study.
"""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor
import copy
import json
from pathlib import Path
import subprocess
import sys
import urllib.request
import xml.etree.ElementTree as ET

import imageio_ffmpeg
import mujoco
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / 'apcl'
CACHE = SITE / '.build' / 'franka_fr3'
DATA = np.load(SITE / 'static/data/episode.npz')
META = json.loads((SITE / 'static/data/episode.json').read_text(encoding='utf-8'))
sys.path.insert(0, str(ROOT / 'claude_try'))
from ctry.model import build_xml

BG = (9, 20, 29)
INK = (231, 240, 243)
MUTED = (133, 159, 172)
CYAN = (92, 229, 208)
CORAL = (255, 147, 116)
GOLD = (255, 216, 140)
FPS = 24
DURATION = 18


def font(size, bold=False):
    return ImageFont.truetype('C:/Windows/Fonts/' + ('segoeuib.ttf' if bold else 'segoeui.ttf'), size)


def fetch_meshes():
    source = ET.parse(ROOT / 'gpt_try/vendor/franka_fr3/fr3.xml').getroot()
    files = [n.attrib['file'] for n in source.findall('asset/mesh') if n.attrib['file'].endswith('.obj')]
    (CACHE / 'assets').mkdir(parents=True, exist_ok=True)
    def download(name):
        target = CACHE / 'assets' / name
        if not target.exists():
            url = 'https://raw.githubusercontent.com/google-deepmind/mujoco_menagerie/main/franka_fr3/assets/' + name
            with urllib.request.urlopen(url, timeout=90) as response:
                target.write_bytes(response.read())
        return target.stat().st_size
    with ThreadPoolExecutor(max_workers=6) as pool:
        total = sum(pool.map(download, files))
    print(f'Robot visual assets: {len(files)} meshes / {total / 1e6:.1f} MB', flush=True)
    return source


def visual_model():
    source = fetch_meshes()
    root = ET.fromstring(build_xml(obj=META['object']))
    asset = ET.SubElement(root, 'asset')
    for mat in source.findall('asset/material'):
        asset.append(copy.deepcopy(mat))
    for mesh in source.findall('asset/mesh'):
        if mesh.attrib['file'].endswith('.obj'):
            el = copy.deepcopy(mesh)
            el.set('name', Path(el.attrib['file']).stem)
            el.set('file', str(CACHE / 'assets' / el.attrib['file']))
            asset.append(el)
    ET.SubElement(asset, 'material', name='objectblue', rgba='.15 .48 .56 1', specular='.35', shininess='.4')
    ET.SubElement(asset, 'material', name='dark', rgba='.065 .085 .10 1', specular='.2')
    ET.SubElement(asset, 'texture', name='sky', type='skybox', builtin='flat', rgb1='.035 .078 .114', width='512', height='512')
    visual = ET.SubElement(root, 'visual')
    ET.SubElement(visual, 'global', offwidth='1280', offheight='960')
    ET.SubElement(visual, 'quality', shadowsize='4096', offsamples='4')
    ET.SubElement(visual, 'headlight', ambient='.30 .34 .39', diffuse='.55 .58 .63', specular='.2 .2 .2')
    ET.SubElement(visual, 'rgba', haze='0.035 0.078 0.114 1')
    world = root.find('worldbody')
    ET.SubElement(world, 'geom', type='plane', size='4 4 .05', rgba='.035 .078 .114 1', contype='0', conaffinity='0')
    ET.SubElement(world, 'geom', type='cylinder', size='.15 .016', pos='0 0 -.002', material='dark', contype='0', conaffinity='0')
    ET.SubElement(world, 'light', pos='1 -2 3', dir='-.2 .4 -1', diffuse='.8 .86 .95', castshadow='true')
    ET.SubElement(world, 'light', pos='-.5 2 2', dir='.2 -.5 -1', diffuse='.35 .5 .55', castshadow='false')
    base = ET.SubElement(world, 'body', name='visual_base')
    for i in range(8):
        original = source.find(f'.//body[@name="fr3_link{i}"]')
        target = base if i == 0 else root.find(f'.//body[@name="link{i}"]')
        for geom in original.findall('geom'):
            if geom.get('class') == 'visual':
                attrs = {k: v for k, v in geom.attrib.items() if k != 'class'}
                ET.SubElement(target, 'geom', **attrs, type='mesh', contype='0', conaffinity='0', mass='0')
    hand = root.find('.//body[@name="hand"]')
    ET.SubElement(hand, 'geom', type='box', size='.045 .035 .023', pos='0 0 .025', material='white', mass='0', contype='0', conaffinity='0')
    for x in (-.05, .05):
        ET.SubElement(hand, 'geom', type='box', size='.009 .015 .038', pos=f'{x} 0 .077', material='dark', mass='0', contype='0', conaffinity='0')
    obj = root.find('.//body[@name="object"]')
    ET.SubElement(obj, 'geom', type='box', size=' '.join(map(str, DATA['dims']/2)),
                  pos=' '.join(map(str, META['object']['com'])), material='objectblue', mass='0', contype='0', conaffinity='0')
    xml = ET.tostring(root, encoding='unicode')
    (SITE / '.build/visual_model.xml').write_text(xml, encoding='utf-8')
    model = mujoco.MjModel.from_xml_string(xml)
    return model


def connector(scene, p1, p2, color, width=.002, arrow=False):
    g = scene.geoms[scene.ngeom]
    kind = mujoco.mjtGeom.mjGEOM_ARROW if arrow else mujoco.mjtGeom.mjGEOM_CAPSULE
    mujoco.mjv_initGeom(g, kind, np.zeros(3), np.zeros(3), np.eye(3).ravel(), np.array(color, dtype=np.float32))
    mujoco.mjv_connector(g, kind, width, np.asarray(p1), np.asarray(p2))
    scene.ngeom += 1


def sphere(scene, p, r, color):
    mujoco.mjv_initGeom(scene.geoms[scene.ngeom], mujoco.mjtGeom.mjGEOM_SPHERE,
                       np.array([r, 0, 0]), p, np.eye(3).ravel(), np.array(color, dtype=np.float32))
    scene.ngeom += 1


def timeline(t):
    # Hold the recorded snapshots long enough to read; the robot motion is slowed.
    if t < 4.0:
        return 2.49, 0
    if t < 7.0:
        return 2.5, 1
    if t < 12.0:
        return 2.5 + (t-7)/5*2.0, 2
    if t < 13.3:
        return 4.5 + (t-12)/1.3*2.5, 2
    return 7., 3


STAGES = [
    ('01 / MEASURE', 'One view leaves a line of possible contacts.'),
    ('02 / PRESERVE', 'Restore support along the unobservable direction.'),
    ('03 / MOVE', 'Reorient the object to gain a new measurement.'),
    ('04 / LOCALIZE', 'A second view resolves the remaining ambiguity.'),
]


def particle_panel(name, stage, size=(604, 246)):
    w, h = size
    im = Image.new('RGB', size, (13, 29, 40))
    draw = ImageDraw.Draw(im)
    color = CYAN if name == 'full' else CORAL
    draw.rounded_rectangle((0, 0, w-1, h-1), radius=16, outline=(37, 58, 70), width=1)
    draw.text((22, 15), 'APCL' if name == 'full' else 'CPF / NO RECOVERY', font=font(19, True), fill=color)
    snap = ('view2' if stage == 3 else ('view1_D3' if stage >= 1 and name == 'full' else 'view1'))
    R1, R2 = DATA[f'{name}_view1_R'], DATA[f'{name}_view2_R']
    u1, u2 = R1.T @ DATA['force'], R2.T @ DATA['force']
    e1 = u1/np.linalg.norm(u1)
    e2 = u2 - e1*np.dot(u2, e1)
    e2 /= np.linalg.norm(e2)
    P, weights = DATA[f'{name}_{snap}_P'], DATA[f'{name}_{snap}_w']
    proj = np.column_stack(((P-DATA['contact']) @ e1, (P-DATA['contact']) @ e2))*1000
    left, right, top, bottom = 28, w-28, 61, h-48
    def xy(p):
        return left+(p[0]+250)/500*(right-left), (top+bottom)/2-p[1]/120*(bottom-top)
    cx, cy = xy([0,0])
    draw.line((left, cy, right, cy), fill=(46, 71, 81), width=1)
    draw.line((cx, top, cx, bottom), fill=(31, 51, 65), width=1)
    for v in (-200,-100,100,200):
        x, y = xy([v,0])
        draw.line((x,cy-3,x,cy+3),fill=(67,83,97))
    if stage == 3:
        slope = np.dot(u2,e2)/np.dot(u2,e1)
        a,b=xy([-60/max(abs(slope),1e-6),-60*np.sign(slope)]),xy([60/max(abs(slope),1e-6),60*np.sign(slope)])
        draw.line((*a,*b),fill=(65,95,100),width=1)
    indices = np.random.default_rng(2).choice(len(P), 1200, p=weights/weights.sum())
    for p in proj[indices]:
        x,y=xy(p)
        if left < x < right and top < y < bottom:
            draw.ellipse((x-1.35,y-1.35,x+1.35,y+1.35),fill=color)
    # True point and the actual weighted estimate, not an animated interpolation.
    draw.ellipse((cx-5,cy-5,cx+5,cy+5),fill=GOLD,outline=BG,width=1)
    mean=weights @ P / weights.sum()
    px,py=xy([(mean-DATA['contact']) @ e1*1000,(mean-DATA['contact']) @ e2*1000])
    if left < px < right and top < py < bottom:
        draw.line((px-5,py-5,px+5,py+5),fill=INK,width=2)
        draw.line((px-5,py+5,px+5,py-5),fill=INK,width=2)
    label = f"{META['results'][name]['err']*1000:.1f} mm error" if stage==3 else ('Recovered support' if name=='full' and stage>=1 else 'View 1 posterior')
    draw.text((22,h-34),label,font=font(18),fill=INK)
    draw.text((w-135,h-33),'±250 mm',font=font(16),fill=MUTED)
    return im


def render_scene(model, data, renderer, q, stage):
    data.qpos[:] = q
    mujoco.mj_forward(model,data)
    camera=mujoco.MjvCamera()
    camera.lookat[:]=[.15,.01,.40]
    camera.distance=1.35
    camera.azimuth=132
    camera.elevation=-19
    renderer.update_scene(data,camera=camera)
    tcp=model.site('tcp').id
    R=data.site_xmat[tcp].reshape(3,3)
    o=data.site_xpos[tcp]
    p=o+R @ DATA['contact']
    direction=DATA['force']/np.linalg.norm(DATA['force'])
    # World-frame applied point force. No obstacle/contact solver is claimed.
    connector(renderer.scene,p-direction*.22,p,(1,.80,.43,1),.009,True)
    sphere(renderer.scene,p,.009,(1,.84,.52,1))
    if stage < 3:
        connector(renderer.scene,p-direction*.23,p+direction*.23,(.34,.85,.78,.55),.0017)
    return Image.fromarray(renderer.render())


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--preview',action='store_true')
    args=parser.parse_args()
    (SITE/'static/images').mkdir(parents=True,exist_ok=True)
    (SITE/'static/videos').mkdir(parents=True,exist_ok=True)
    model=visual_model()
    data=mujoco.MjData(model)
    trajectory=DATA['full_trajectory']
    panels={(n,s):particle_panel(n,s) for n in ('none','full') for s in range(4)}
    with mujoco.Renderer(model,width=1280,height=760) as renderer:
        def frame(t):
            simt,stage=timeline(t)
            q=np.array([np.interp(simt,trajectory[:,0],trajectory[:,j+1]) for j in range(7)])
            scene=render_scene(model,data,renderer,q,stage)
            hero=Image.new('RGB',(1280,1000),BG)
            hero.paste(scene,(0,-16))
            # A soft floor fade unifies the render and the posterior panels.
            fade=Image.new('RGB',scene.size,BG)
            mask=np.zeros((760,1280),np.uint8)
            mask[540:,:]=np.linspace(0,255,220,dtype=np.uint8)[:,None]
            hero.paste(fade,(0,-16),Image.fromarray(mask))
            d=ImageDraw.Draw(hero)
            d.text((34,29),'FR3 / MUJOCO',font=font(19,True),fill=MUTED)
            d.text((850,29),STAGES[stage][0],font=font(19,True),fill=CYAN)
            hero.paste(panels['none',stage],(24,700))
            hero.paste(panels['full',stage],(652,700))
            d.text((32,962),'Posterior snapshots · tool frame',font=font(16),fill=MUTED)
            d.ellipse((906,969,914,977),fill=GOLD)
            d.text((924,960),'True contact',font=font(16),fill=MUTED)
            d.text((1090,960),'× Estimate',font=font(16),fill=MUTED)
            video=Image.new('RGB',(1600,900),BG)
            dv=ImageDraw.Draw(video)
            dv.text((52,32),'APCL',font=font(28,True),fill=CYAN)
            dv.text((170,40),'AMBIGUITY-PRESERVING CONTACT LOCALIZATION',font=font(17),fill=MUTED)
            dv.text((52,107),STAGES[stage][0],font=font(18,True),fill=CYAN)
            dv.text((52,145),STAGES[stage][1],font=font(36,True),fill=INK)
            video.paste(scene.resize((920,546),Image.Resampling.LANCZOS),(-15,230))
            video.paste(panels['none',stage],(930,232))
            video.paste(panels['full',stage],(930,510))
            dv.text((54,755),'Recorded torque-controlled motion',font=font(20),fill=INK)
            dv.text((54,786),'Unknown box payload · applied point force · object-fixed contact',font=font(17),fill=MUTED)
            dv.text((934,775),'• True contact    × Weighted estimate',font=font(16),fill=GOLD)
            dv.text((54,853),'DEVELOPMENT SEED 17 / 2 VIEWS     |     SIMULATION ONLY',font=font(16),fill=MUTED)
            dv.text((915,853),'Motion slowed; distributions update at saved snapshots.',font=font(16),fill=MUTED)
            dv.line((54,832,1546,832),fill=(37,58,70),width=2)
            dv.line((54,832,54+1492*t/DURATION,832),fill=CYAN,width=3)
            return hero,video
        if args.preview:
            for sec in (1,5,15):
                h,v=frame(sec)
                h.save(SITE/f'.build/hero-{sec}.jpg',quality=93)
                v.save(SITE/f'.build/demo-{sec}.jpg',quality=93)
            print('Saved preview frames',flush=True)
            return
        ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
        def encoder(path,size):
            return subprocess.Popen([ffmpeg,'-y','-hide_banner','-loglevel','warning','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s',size,'-r',str(FPS),'-i','-','-an','-vcodec','libx264','-preset','fast','-crf','23','-pix_fmt','yuv420p','-movflags','+faststart',str(path)],stdin=subprocess.PIPE)
        enc1=encoder(SITE/'static/videos/apcl-hero.mp4','1280x1000')
        enc2=encoder(SITE/'static/videos/apcl-demo.mp4','1600x900')
        try:
            for idx in range(FPS*DURATION):
                t=idx/FPS
                h,v=frame(t)
                enc1.stdin.write(h.tobytes())
                enc2.stdin.write(v.tobytes())
                if idx==120:
                    h.save(SITE/'static/images/hero-poster.jpg',quality=92)
                    v.save(SITE/'static/images/demo-poster.jpg',quality=92)
                if idx%72==0:
                    print(f'Rendered {idx}/{FPS*DURATION} frames',flush=True)
        finally:
            enc1.stdin.close()
            enc2.stdin.close()
        if enc1.wait() or enc2.wait():
            raise RuntimeError('Video encoder failed')
        for n in ('none','full'):
            for s in (0,1,3):
                panels[n,s].save(SITE/f'static/images/{n}-{s}.png')
        print('Both MP4 videos complete',flush=True)


if __name__=='__main__':
    main()
