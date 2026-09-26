"""Render the captured experiment, with measured posterior snapshots.

Robot visuals: MuJoCo Menagerie / Franka FR3 (see THIRD_PARTY.md).
Two visual instances replay their own recorded trajectories. Scene translations
separate the paired trials for presentation; rendering does not alter the study.
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
CAMERA_AZIMUTH = 210
# Screen-right direction for the fixed MuJoCo camera. Offsets are perpendicular
# to the viewing direction, so both instances have the same scale/depth.
SCREEN_RIGHT = np.array([np.sin(np.deg2rad(CAMERA_AZIMUTH)), -np.cos(np.deg2rad(CAMERA_AZIMUTH)), 0.])
INSTANCE_OFFSETS = {'none': -.49 * SCREEN_RIGHT, 'full': .49 * SCREEN_RIGHT}


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
    pedestal = ET.SubElement(world, 'geom', type='cylinder', size='.15 .016', pos='0 0 -.002', material='dark', contype='0', conaffinity='0')
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
    # Duplicate the complete visual/kinematic robot, not a second copy of the
    # same rendered frame. Each instance has its own seven joints and TCP.
    chain = world.find('body[@name="link1"]')
    for child in (chain, base, pedestal):
        world.remove(child)
    for name, offset in INSTANCE_OFFSETS.items():
        instance = ET.SubElement(world, 'body', name=f'{name}_instance', pos=' '.join(map(str, offset)))
        for child in (chain, base, pedestal):
            clone = copy.deepcopy(child)
            for element in clone.iter():
                if 'name' in element.attrib:
                    element.set('name', f'{name}_{element.attrib["name"]}')
            instance.append(clone)
    # Replay uses mj_forward only. Original actuator references would point to
    # unprefixed joints, and no dynamics are stepped in this visualization.
    root.remove(root.find('actuator'))
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


def posterior(name, stage):
    snap = 'view2' if stage == 3 else ('view1_D3' if stage >= 1 and name == 'full' else 'view1')
    P, weights = DATA[f'{name}_{snap}_P'], DATA[f'{name}_{snap}_w']
    mean = weights @ P / weights.sum()
    return P, weights, mean


def particle_panel(name, stage, size=(604, 246)):
    w, h = size
    im = Image.new('RGB', size, (13, 29, 40))
    draw = ImageDraw.Draw(im)
    color = CYAN if name == 'full' else CORAL
    draw.rounded_rectangle((0, 0, w-1, h-1), radius=16, outline=(37, 58, 70), width=1)
    draw.text((22, 15), 'APCL' if name == 'full' else 'CPF / NO RECOVERY', font=font(19, True), fill=color)
    R1, R2 = DATA[f'{name}_view1_R'], DATA[f'{name}_view2_R']
    u1, u2 = R1.T @ DATA['force'], R2.T @ DATA['force']
    e1 = u1/np.linalg.norm(u1)
    e2 = u2 - e1*np.dot(u2, e1)
    e2 /= np.linalg.norm(e2)
    P, weights, mean = posterior(name, stage)
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
    px,py=xy([(mean-DATA['contact']) @ e1*1000,(mean-DATA['contact']) @ e2*1000])
    if left < px < right and top < py < bottom:
        draw.line((px-5,py-5,px+5,py+5),fill=INK,width=2)
        draw.line((px-5,py+5,px+5,py-5),fill=INK,width=2)
    label = f"{META['results'][name]['err']*1000:.1f} mm error" if stage==3 else ('Recovered support' if name=='full' and stage>=1 else 'View 1 posterior')
    draw.text((22,h-34),label,font=font(18),fill=INK)
    draw.text((w-135,h-33),'±250 mm',font=font(16),fill=MUTED)
    return im


def project(scene, point, width, height):
    """Project a world point with MuJoCo's actual mono-view GL camera."""
    left, right = scene.camera
    camera_pos = (left.pos + right.pos) / 2
    forward = (left.forward + right.forward) / 2
    forward /= np.linalg.norm(forward)
    up = (left.up + right.up) / 2
    up /= np.linalg.norm(up)
    horizontal = np.cross(forward, up)
    horizontal /= np.linalg.norm(horizontal)
    delta = np.asarray(point) - camera_pos
    depth = np.dot(delta, forward)
    assert depth > 0, 'Annotation is behind the camera'
    half_height = (left.frustum_top-left.frustum_bottom) / (2*left.frustum_near)
    scale = height / (2*half_height*depth)
    return np.array([width/2 + np.dot(delta, horizontal)*scale,
                     height/2 - np.dot(delta, up)*scale])


def dashed(draw, start, end, color, width=2):
    start, end = np.asarray(start), np.asarray(end)
    length = np.linalg.norm(end-start)
    if length < 18:
        return
    direction = (end-start)/length
    for distance in np.arange(12, length-10, 11):
        a = start + direction*distance
        b = start + direction*min(distance+5, length-10)
        draw.line((*a, *b), fill=color, width=width)


def annotate_scene(image, points, stage):
    """Keep the true and estimated 3-D locations readable, even if occluded."""
    draw=ImageDraw.Draw(image)
    for name in ('none','full'):
        color=CYAN if name=='full' else CORAL
        truth, estimate, error=points[name]
        tx,ty=truth
        ex,ey=estimate
        dashed(draw,truth,estimate,color)
        # A hollow diamond shows the projected estimate. Its center is never
        # shifted away from the measurement merely to make a gap more visible.
        diamond=[(ex,ey-11),(ex+11,ey),(ex,ey+11),(ex-11,ey),(ex,ey-11)]
        draw.line(diamond,fill=BG,width=6)
        draw.line(diamond,fill=color,width=3)
        draw.ellipse((tx-5,ty-5,tx+5,ty+5),fill=GOLD,outline=BG,width=1)
        # Method-specific callout; offset only the text, not the marker.
        heading='CONTACT ESTIMATE' if stage==3 else 'SNAPSHOT MEAN'
        value=f'{error:.1f} mm error' if stage==3 else 'View 1 estimate'
        box_w,box_h=205,72
        label_x=ex+33
        label_y=ey-92
        if label_x+box_w>image.width-18:
            label_x=ex-box_w-33
        label_x=max(18,label_x)
        label_y=max(112,min(image.height-box_h-14,label_y))
        near_x=label_x if label_x>ex else label_x+box_w
        draw.line((ex+12 if label_x>ex else ex-12,ey,near_x,label_y+box_h*.62),fill=color,width=1)
        draw.rounded_rectangle((label_x,label_y,label_x+box_w,label_y+box_h),radius=9,fill=BG,outline=(51,74,87),width=1)
        draw.text((label_x+12,label_y+10),heading,font=font(12,True),fill=MUTED)
        draw.text((label_x+12,label_y+30),value,font=font(24,True),fill=color)
    return image


def render_scene(model, data, renderer, simt, stage):
    for name in ('none','full'):
        trajectory=DATA[f'{name}_trajectory']
        for j in range(7):
            adr=int(model.joint(f'{name}_j{j+1}').qposadr[0])
            data.qpos[adr]=np.interp(simt,trajectory[:,0],trajectory[:,j+1])
    mujoco.mj_forward(model,data)
    camera=mujoco.MjvCamera()
    camera.lookat[:]=[.15,.01,.40]
    camera.distance=1.48
    camera.azimuth=CAMERA_AZIMUTH
    camera.elevation=-19
    renderer.update_scene(data,camera=camera)
    direction=DATA['force']/np.linalg.norm(DATA['force'])
    points={}
    for name in ('none','full'):
        tcp=model.site(f'{name}_tcp').id
        R=data.site_xmat[tcp].reshape(3,3)
        o=data.site_xpos[tcp]
        mean=posterior(name,stage)[2]
        truth=o+R @ DATA['contact']
        estimate=o+R @ mean
        error=float(np.linalg.norm(mean-DATA['contact'])*1000)
        assert np.isclose(np.linalg.norm(truth-estimate)*1000,error,atol=1e-8)
        color=np.array(CYAN if name=='full' else CORAL)/255
        # World-frame point force and markers at their true spatial positions.
        connector(renderer.scene,truth-direction*.17,truth,(1,.80,.43,1),.007,True)
        sphere(renderer.scene,truth,.005,(1,.84,.52,1))
        sphere(renderer.scene,estimate,.007,(*color,1))
        if stage < 3:
            connector(renderer.scene,truth-direction*.22,truth+direction*.22,(*color,.45),.0012)
        if error > 12:
            connector(renderer.scene,truth,estimate,(*color,.75),.0015)
        points[name]=(project(renderer.scene,truth,1280,760),project(renderer.scene,estimate,1280,760),error)
    scene=Image.fromarray(renderer.render())
    return annotate_scene(scene,points,stage),points


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--preview',action='store_true')
    args=parser.parse_args()
    (SITE/'static/images').mkdir(parents=True,exist_ok=True)
    (SITE/'static/videos').mkdir(parents=True,exist_ok=True)
    model=visual_model()
    data=mujoco.MjData(model)
    panels={(n,s):particle_panel(n,s) for n in ('none','full') for s in range(4)}
    with mujoco.Renderer(model,width=1280,height=760) as renderer:
        def frame(t):
            simt,stage=timeline(t)
            scene,points=render_scene(model,data,renderer,simt,stage)
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
            d.text((90,85),'CPF / NO RECOVERY',font=font(22,True),fill=CORAL)
            d.text((795,85),'APCL',font=font(22,True),fill=CYAN)
            hero.paste(panels['none',stage],(24,700))
            hero.paste(panels['full',stage],(652,700))
            d.text((32,962),'3D: colored diamond = estimate  /  plots: × = mean',font=font(16),fill=MUTED)
            d.ellipse((906,969,914,977),fill=GOLD)
            d.text((924,960),'True contact',font=font(16),fill=MUTED)
            d.text((1090,960),'3D to scale',font=font(16),fill=MUTED)
            video=Image.new('RGB',(1600,900),BG)
            dv=ImageDraw.Draw(video)
            dv.text((52,32),'APCL',font=font(28,True),fill=CYAN)
            dv.text((170,40),'AMBIGUITY-PRESERVING CONTACT LOCALIZATION',font=font(17),fill=MUTED)
            dv.text((52,107),STAGES[stage][0],font=font(18,True),fill=CYAN)
            dv.text((52,145),STAGES[stage][1],font=font(36,True),fill=INK)
            video.paste(scene.resize((920,546),Image.Resampling.LANCZOS),(-15,230))
            dv.text((62,245),'CPF / NO RECOVERY',font=font(17,True),fill=CORAL)
            dv.text((550,245),'APCL',font=font(17,True),fill=CYAN)
            video.paste(panels['none',stage],(930,232))
            video.paste(panels['full',stage],(930,510))
            dv.text((54,765),'Two recorded trajectories · one shared starting condition',font=font(19),fill=INK)
            dv.text((54,796),'Gold dot: true contact   /   Colored diamond: estimated contact',font=font(16),fill=MUTED)
            dv.text((934,775),'• True contact    × Weighted estimate',font=font(16),fill=GOLD)
            dv.text((54,853),'DEVELOPMENT SEED 17 / 2 VIEWS     |     SIMULATION ONLY',font=font(16),fill=MUTED)
            dv.text((835,853),'3D positions to scale; markers enlarged. Estimates update at snapshots.',font=font(15),fill=MUTED)
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
                if idx==360:
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
