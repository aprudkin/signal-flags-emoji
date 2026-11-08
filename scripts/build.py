"""Process the supplied raster artwork; no replacement drawings or generated art."""
from pathlib import Path
import csv
import hashlib
import io
import json
import zipfile

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageCms, PngImagePlugin
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / 'scripts/flags.json').read_text())
RESAMPLE = Image.Resampling.LANCZOS

def save_png(im, path):
    # PNG sRGB chunk is deterministic (unlike freshly generated ICC timestamps).
    metadata = PngImagePlugin.PngInfo()
    metadata.add(b'sRGB', b'\x00')
    im.save(path, pnginfo=metadata, optimize=True)

def extract_if_needed():
    missing = [f for f in CONFIG['flags'] if not (ROOT/'originals'/f['source']).exists()]
    if any('archive_member' not in f for f in missing):
        raise FileNotFoundError('Restore separately supplied originals: ' + ', '.join(f['source'] for f in missing if 'archive_member' not in f))
    if missing:
        with zipfile.ZipFile(ROOT/'Maritime_Signal_Flags.zip') as archive:
            for f in missing:
                (ROOT/'originals'/f['source']).write_bytes(archive.read(f['archive_member']))

def silhouette(a, threshold):
    # Flood only the light region connected to the image boundary. The closed
    # original outline protects white cloth. Internal light pixels are retained.
    light = a.min(axis=2) > threshold
    seeds = np.zeros(light.shape, bool)
    seeds[[0, -1], :] = light[[0, -1], :]
    seeds[:, [0, -1]] = light[:, [0, -1]]
    outside = ndi.binary_propagation(seeds, mask=light)
    labels, count = ndi.label(~outside)
    sizes = np.bincount(labels.ravel()); sizes[0] = 0
    body = labels == sizes.argmax()
    body = ndi.binary_fill_holes(body)
    if not 0.4 < body.mean() < 0.9:
        raise ValueError('Unexpected silhouette; inspect background threshold')
    return body

def process(flag):
    cfg = CONFIG['defaults'] | flag.get('settings', {})
    source = ROOT/'originals'/flag['source']
    assert hashlib.sha256(source.read_bytes()).hexdigest() == flag['sha256'], source
    im = Image.open(source)
    if im.info.get('icc_profile'):
        im = ImageCms.profileToProfile(im, io.BytesIO(im.info['icc_profile']),
                                      ImageCms.createProfile('sRGB'), outputMode='RGB')
    scale = max(im.size) / 1024
    source_pixels = np.asarray(im.convert('RGB'))
    pixels = source_pixels.copy()
    body = silhouette(pixels.astype(float), cfg['background_threshold'])
    alpha = np.rint(ndi.gaussian_filter(body.astype(float), 0.55*scale)*255).astype('uint8')
    alpha[alpha < 4] = 0
    alpha[alpha > 251] = 255
    # Remove the white JPEG matte only from the translucent outer fringe.
    # Keep the source RGB values of every opaque pixel, including its outline.
    solid = ndi.distance_transform_edt(body) >= 2*scale
    nearest = ndi.distance_transform_edt(~solid, return_distances=False, return_indices=True)
    fringe = (alpha > 0) & (alpha < 255)
    pixels[fringe] = pixels[tuple(nearest)][fringe]
    pixels[alpha == 0] = 0
    assert np.array_equal(pixels[alpha == 255], source_pixels[alpha == 255])
    result = Image.fromarray(np.dstack([pixels, alpha]))
    save_png(result, ROOT/'processed'/f'{flag["slug"]}.png')
    cropped = result.crop(result.getbbox())
    cropped.thumbnail((90, 90), RESAMPLE)  # Pillow uses premultiplied-alpha RGBA resampling.
    emoji = Image.new('RGBA', (100, 100))
    emoji.alpha_composite(cropped, ((100-cropped.width)//2, (100-cropped.height)//2))
    pixels = np.array(emoji)
    pixels[pixels[..., 3] < 2] = 0  # Remove isolated low-alpha Lanczos ringing.
    emoji = Image.fromarray(pixels)
    save_png(emoji, ROOT/'emoji'/f'{flag["slug"]}.png')
    return result, emoji

def display_name(flag):
    return flag['name'] + (' ?' if flag['identification'] != 'identified' else '')

def font(size):
    return ImageFont.load_default(size=size)

def previews(flags, results):
    for theme, bg, fg, subtle in [('white','#FFFFFF','#17212B','#5B6875'),
                                   ('dark','#17212B','#FFFFFF','#A6B6C6')]:
        sheet = Image.new('RGB', (1000, 96+len(flags)*124), bg)
        draw = ImageDraw.Draw(sheet)
        draw.text((24,18), f'SIGNAL FLAGS / {theme.upper()} / {bg}', font=font(25), fill=fg)
        for x,s in [(267,20),(335,24),(411,32),(525,100)]:
            draw.text((x,65),f'{s} px',font=font(15),fill=subtle)
        draw.text((690,65),'24 px / inline text',font=font(15),fill=subtle)
        for i,(flag,(_,em)) in enumerate(zip(flags,results)):
            y=96+i*124
            draw.line((24,y,976,y),fill=subtle,width=1)
            draw.text((24,y+47),f'{flag["letter"]} / {display_name(flag)}',font=font(21),fill=fg)
            for x,s in [(270,20),(340,24),(420,32),(525,100)]:
                icon=em.resize((s,s),RESAMPLE); sheet.paste(icon,(x,y+(124-s)//2),icon)
            draw.text((660,y+49),'Signal',font=font(20),fill=fg)
            icon=em.resize((24,24),RESAMPLE);sheet.paste(icon,(731,y+48),icon)
            draw.text((765,y+49),'received',font=font(20),fill=fg)
        save_png(sheet,ROOT/'previews'/f'contact-{theme}.png')
        overview=Image.new('RGB',(880,80+((len(flags)+4)//5)*190),bg);d=ImageDraw.Draw(overview)
        d.text((24,20),f'SIGNAL FLAGS / {len(flags)} emoji / {bg}',font=font(25),fill=fg)
        for i,(f,(_,em)) in enumerate(zip(flags,results)):
            x=i%5*176;y=80+i//5*190
            overview.paste(em,(x+38,y+10),em)
            d.text((x+13,y+127),f'{f["letter"]} {display_name(f)}',font=font(17),fill=fg)
        save_png(overview,ROOT/'previews'/f'overview-{theme}.png')
    for start in range(0,len(flags),6):
        batch=flags[start:start+6]
        canvas=Image.new('RGB',(1000,70+len(batch)*230),'#E6EBF0');d=ImageDraw.Draw(canvas)
        d.text((20,20),'ORIGINAL (JPEG)       /       PROCESSED ON WHITE       /       PROCESSED ON DARK',font=font(18),fill='#17212B')
        for row,f in enumerate(batch):
            y=70+row*230
            d.text((15,y+8),f'{f["letter"]} / {display_name(f)}',font=font(18),fill='#17212B')
            original=Image.open(ROOT/'originals'/f['source']).convert('RGB');original.thumbnail((200,200))
            canvas.paste(original,(140,y+10))
            proc=results[start+row][0].resize((200,200),RESAMPLE)
            for x,bg in [(450,'#FFFFFF'),(740,'#17212B')]:
                tile=Image.new('RGB',(200,200),bg);tile.paste(proc,(0,0),proc);canvas.paste(tile,(x,y+10))
        save_png(canvas,ROOT/'previews'/f'comparison-{start//6+1:02}.png')

def validate(flags):
    report=[]
    for f in flags:
        item={'flag':f['slug'],'source_sha256':f['sha256']}
        with Image.open(ROOT/'originals'/f['source']) as original:
            source_size = original.size
            if original.info.get('icc_profile'):
                original = ImageCms.profileToProfile(original, io.BytesIO(original.info['icc_profile']),
                                                      ImageCms.createProfile('sRGB'), outputMode='RGB')
            source_pixels = np.asarray(original.convert('RGB'))
        for folder,expected in [('processed',source_size),('emoji',(100,100))]:
            path=ROOT/folder/f'{f["slug"]}.png'
            with Image.open(path) as im:
                assert im.format=='PNG' and im.mode=='RGBA' and im.size==expected, path
                assert im.info.get('srgb')==0, path
                pixels = np.array(im)
                a = pixels[..., 3]
                if folder == 'processed':
                    assert np.array_equal(pixels[a == 255, :3], source_pixels[a == 255]), path
                    item['original_opaque_rgb_preserved'] = True
                assert a.min()==0 and a.max()==255 and np.any((a>0)&(a<255)),path
                assert not np.any(np.r_[a[0],a[-1],a[:,0],a[:,-1]]),path
                mask=a>127; labels,n=ndi.label(mask)
                assert n==1 and np.array_equal(ndi.binary_fill_holes(mask),mask),path
                # Match the alpha edge width at native source resolution.
                core=ndi.binary_erosion(mask,iterations=max(3, int(np.ceil(3*max(im.size)/1024))))
                assert np.all(a[core]==255),path
                box=im.getbbox()
                if folder=='emoji':
                    assert max(box[2]-box[0],box[3]-box[1])==90,(path,box)
                    assert min(box[0],box[1],100-box[2],100-box[3])>=5,path
                item[folder]={'size':list(im.size),'rgba':True,'srgb':True,'bbox':list(box),'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
        report.append(item)
    (ROOT/'docs/validation.json').write_text(json.dumps({'count':len(flags),'checks':'dimensions, PNG/RGBA, sRGB, transparent borders, solid interior, single component, no holes, 90px bounds, original SHA-256, original opaque RGB preserved','files':report},indent=2)+'\n')

def catalog(flags):
    fields=['source','original_name','archive_member','actual_format','letter','name','identification','processed','emoji','sha256','notes']
    rows=[]
    for f in flags:
        rows.append(dict(source='originals/'+f['source'],original_name=f['original_name'],archive_member=f.get('archive_member',''),actual_format='JPEG',letter=f['letter'],name=f['name'],identification=f['identification'],processed=f'processed/{f["slug"]}.png',emoji=f'emoji/{f["slug"]}.png',sha256=f['sha256'],notes=f['notes']))
    with (ROOT/'catalog.csv').open('w',newline='') as out:
        writer=csv.DictWriter(out,fieldnames=fields,lineterminator="\n");writer.writeheader();writer.writerows(rows)
    missing = ', '.join(sorted(set('ABCDEFGHIJKLMNOPQRSTUVWXYZ') - {f['letter'] for f in flags})) or 'нет'
    confident = sum(f['identification'] == 'identified' for f in flags)
    text=f'# Каталог флагов\n\n{len(flags)} исходников; {confident} определены уверенно. O/X/Y — предположительные варианты с отклонениями; точная идентификация X не подтверждена. Отсутствующие буквы: {missing}. Знак ? на превью отмечает предположительное обозначение. Прежние имена и записи архива сохранены в catalog.csv.\n\n| Флаг | Исходник (JPEG) | Обработанный PNG | Эмодзи | Примечание |\n|---|---|---|---|---|\n'
    for f,row in zip(flags,rows):
        text+=f'| {f["letter"]} {display_name(f)} | [{f["source"]}]({row["source"]}) | [PNG]({row["processed"]}) | [100 px]({row["emoji"]}) | {f["notes"]} |\n'
    (ROOT/'CATALOG.md').write_text(text)

def main():
    for folder in ['originals','processed','emoji','previews','docs']:
        (ROOT/folder).mkdir(exist_ok=True)
    extract_if_needed()
    flags=CONFIG['flags']
    actual={p.name for p in (ROOT/'originals').iterdir() if p.is_file() and p.name != '.DS_Store'}
    assert actual=={f['source'] for f in flags},'Uncatalogued or missing source files'
    results=[]
    for f in flags:
        results.append(process(f));print(f'Processed {f["letter"]} / {display_name(f)}',flush=True)
    previews(flags,results);catalog(flags);validate(flags)
    print(f'OK: {len(flags)} flags; PNG RGBA/sRGB 100 x 100; previews and validation report ready.')

if __name__=='__main__':
    main()
