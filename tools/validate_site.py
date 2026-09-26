"""Browser smoke check, responsive inspection, local links and numeric provenance."""
import asyncio
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import urlsplit, unquote
from playwright.async_api import async_playwright

SITE=Path(__file__).resolve().parents[1]
URL='http://127.0.0.1:8765/'


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.local=set()
        self.fragments=set()
        self.ids=set()
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if 'id' in attrs:
            assert attrs['id'] not in self.ids, f"Duplicate id: {attrs['id']}"
            self.ids.add(attrs['id'])
        for attr in ('href','src','poster'):
            value=attrs.get(attr,'')
            if not value:
                continue
            if value.startswith('#'):
                self.fragments.add(value[1:])
            elif not urlsplit(value).scheme:
                self.local.add(unquote(urlsplit(value).path))


async def main():
    out=SITE/'.build'
    out.mkdir(exist_ok=True)
    links=Links()
    links.feed((SITE/'index.html').read_text(encoding='utf-8'))
    assert links.fragments <= links.ids, links.fragments-links.ids
    for link in links.local:
        assert (SITE/link).is_file(), f'Missing asset: {link}'
    data=json.loads((SITE/'static/data/results.json').read_text(encoding='utf-8'))
    episode=json.loads((SITE/'static/data/tether_episode.json').read_text(encoding='utf-8'))
    verification=json.loads((SITE/'static/data/tether_verification.json').read_text(encoding='utf-8'))
    media=json.loads((SITE/'static/data/tether_media.json').read_text(encoding='utf-8'))
    for name,digest in media.items():
        assert hashlib.sha256((SITE/name).read_bytes()).hexdigest()==digest,name
    assert media['static/videos/apcl-demo.mp4']==verification['sha256']
    errors=[]
    bad_responses=[]
    checks=[]
    async with async_playwright() as p:
        browser=await p.chromium.launch(executable_path='C:/Program Files/Google/Chrome/Application/chrome.exe',headless=True)
        context=await browser.new_context(viewport={'width':1440,'height':1000},device_scale_factor=1)
        page=await context.new_page()
        page.on('pageerror',lambda error:errors.append(str(error)))
        page.on('response',lambda response:bad_responses.append(f'{response.status} {response.url}') if response.status>=400 else None)
        await page.goto(URL,wait_until='networkidle')
        await page.wait_for_function("document.querySelector('#hero-video').readyState >= 2")
        assert await page.locator('#hero-video').evaluate('(v)=>v.duration')==30
        await page.wait_for_function("document.querySelector('#hero-video').currentTime > 0")
        assert await page.locator('#hero-toggle').get_attribute('aria-label')=='Pause background simulation'
        await page.locator('#hero-toggle').click()
        assert await page.locator('#hero-video').evaluate('(v)=>v.paused')
        await page.locator('#hero-video').evaluate('''v => new Promise(resolve => {
          v.addEventListener('seeked', () => resolve(), {once:true}); v.currentTime=5;
        })''')
        assert await page.locator('#hero-video').evaluate('(v)=>v.currentTime')==5,'MP4 seeking requires HTTP Range support'
        await page.wait_for_timeout(250)
        await page.screenshot(path=str(out/'desktop-hero.png'))
        await page.screenshot(path=str(out/'desktop-full.png'),full_page=True)
        checks.append('hero autoplay, 30-second metadata, pause control, exact 5-second seek')

        await page.locator('#demo-video').scroll_into_view_if_needed()
        await page.locator('#demo-video').evaluate('(v)=>{v.muted=true;v.load();}')
        await page.wait_for_function("document.querySelector('#demo-video').readyState >= 2")
        assert await page.locator('#demo-video').evaluate('(v)=>v.duration')==30
        assert await page.locator('#demo-video').evaluate('(v)=>v.videoWidth')==1600
        await page.locator('#demo-video').evaluate('''v => new Promise(resolve => {
          v.addEventListener('seeked', () => resolve(), {once:true}); v.currentTime=26;
        })''')
        assert await page.locator('#demo-video track').count()==2
        await page.locator('#film').screenshot(path=str(out/'suspended-load-film.png'))
        takeaways=await page.locator('.film-takeaways').inner_text()
        for name in ('none','full'):
            assert f"{episode['results'][name]['err']*1000:.1f} mm" in takeaways
        checks.append('published film matches approved MP4, both caption tracks, final frame seek and recorded errors')

        embedded=await page.evaluate('results')
        keys={'median':'median_mm','p95':'p95_mm','cbw':'cbw_pct','count':'cbw_count','coverage':'coverage_pct','n':'n'}
        for population in ('all','accepted'):
            for variant in ('none','full'):
                for key,source in keys.items():
                    assert abs(embedded[population][variant][key]-data[population][variant][source])<1e-8,(population,variant,key)
        await page.locator('[data-population=accepted]').click()
        assert await page.locator('#table-full-cbw').inner_text()=='2 / 556'
        assert await page.locator('#table-none-coverage').inner_text()=='64.4%'
        assert await page.locator('#cbw-none-bar').evaluate('(e)=>parseFloat(e.style.getPropertyValue("--bar-width"))')<100
        await page.locator('[data-population=all]').click()
        assert await page.locator('#table-full-cbw').inner_text()=='10 / 1,200'
        await page.locator('#results').screenshot(path=str(out/'results.png'))
        checks.append('both populations and every embedded metric match source summary')

        await page.locator('#view-angle').fill('0')
        assert 'Parallel' in await page.locator('#geometry-note').inner_text()
        await page.locator('#view-angle').fill('90')
        assert await page.locator('#second-line').get_attribute('transform')=='rotate(-90 300 160)'
        await page.locator('#view-angle').fill('35')
        checks.append('geometry control at 0, 35 and 90 degrees')

        for width in (320,390,680,768,1024,1440,1920):
            await page.set_viewport_size({'width':width,'height':900 if width>680 else 844})
            await page.evaluate('window.scrollTo(0,0)')
            await page.wait_for_timeout(100)
            overflow=await page.evaluate('document.documentElement.scrollWidth > window.innerWidth')
            assert not overflow,f'Horizontal overflow at {width}px'
            if width==390:
                await page.screenshot(path=str(out/'mobile-hero.png'))
                await page.screenshot(path=str(out/'mobile-full.png'),full_page=True)
                await page.locator('.menu-toggle').click()
                assert await page.locator('.menu-toggle').get_attribute('aria-expanded')=='true'
                await page.keyboard.press('Escape')
                assert await page.locator('.menu-toggle').get_attribute('aria-expanded')=='false'
        checks.append('no horizontal overflow at 320, 390, 680, 768, 1024, 1440, 1920 px; mobile menu')
        for link in links.local:
            response=await context.request.get(URL+link)
            assert response.ok,f'{response.status}: {link}'
        checks.append(f'{len(links.local)} local assets and {len(links.fragments)} anchor targets')
        partial=await context.request.get(URL+'static/videos/apcl-demo.mp4',headers={'Range':'bytes=100-199'})
        assert partial.status==206 and len(await partial.body())==100
        assert partial.headers['content-range'].startswith('bytes 100-199/')
        checks.append('HTTP byte-range support for video seeking')

        reduced=await browser.new_context(viewport={'width':1440,'height':1000},reduced_motion='reduce')
        rp=await reduced.new_page()
        await rp.goto(URL,wait_until='networkidle')
        assert await rp.locator('#hero-video').evaluate('(v)=>v.paused')
        await rp.locator('#hero-toggle').click()
        await rp.wait_for_function("!document.querySelector('#hero-video').paused")
        checks.append('reduced motion starts paused, explicit playback works')

        direct=await browser.new_page()
        await direct.goto((SITE/'index.html').as_uri())
        await direct.locator('[data-population=accepted]').click()
        assert await direct.locator('#table-full-p95').inner_text()=='15.8 mm'
        checks.append('direct file opening retains interactive results')
        await browser.close()
    assert not errors,errors
    assert not bad_responses,bad_responses
    report={'status':'passed','checks':checks,'javascript_errors':errors,'http_errors':bad_responses}
    (out/'validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    asyncio.run(main())
