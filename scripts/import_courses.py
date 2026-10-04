"""Import only the index-linked materials and their lecture text variants."""
from pathlib import Path
import argparse, hashlib, json, re
from urllib.parse import unquote
from PIL import Image

PROJECT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser()
p.add_argument('source', type=Path, help='Local raw/courses directory')
args = p.parse_args()
root = args.source.resolve()
index = root/'信奥课程总索引与阅读指南.md'
text = index.read_text()
courses = re.findall(r'^#### ([A-H]\d+)｜(.+)$', text, re.M)
assert courses and len({code for code, _ in courses}) == len(courses), 'Index requires unique course IDs'
records = [{'id':'index','title':'信奥课程总索引与阅读指南','kind':'index','source':index}]
for code,title in courses:
    folder=root/title
    for suffix,kind,label in [('PPT讲稿对照','slides','PPT／讲稿对照'),('精编讲稿','edited','精编讲稿'),('完整讲稿','full','完整讲稿')]:
        source=next(folder.glob(f'*_{suffix}.md'))
        slug=code.lower()+('' if kind=='slides' else '-'+kind)
        records.append(dict(id=slug,title=title,kind=kind,label=label,code=code,source=source))
records.extend([
    dict(id='seven-lectures',title='信奥训练方法七讲合辑 · 总结',kind='supplement',source=root/'信奥训练方法七讲合辑_总结.md'),
    dict(id='archive-list',title='FayeTY 视频归档与待下载清单',kind='supplement',source=root/'FayeTY_待下载视频清单.md')])
source_map={r['source'].resolve():r['id'] for r in records}
content=PROJECT/'content'; content.mkdir(exist_ok=True)
images=PROJECT/'site-assets'/'images'; images.mkdir(parents=True,exist_ok=True)
image_map={};source_bytes=0
for r in records:
    s=r['source'].read_text()
    def replace(m):
        global source_bytes
        image,label,target=m.group(1),m.group(2),m.group(3).strip()
        target=target[1:-1] if target.startswith('<') and target.endswith('>') else target
        if target.startswith(('http:','https:','mailto:','#')):return m.group(0)
        target,sep,fragment=target.partition('#')
        local=(r['source'].parent/unquote(target)).resolve()
        if image:
            assert local.is_file(),local
            if local not in image_map:
                name=hashlib.sha256(local.read_bytes()).hexdigest()[:24]+'.webp'
                with Image.open(local) as im:
                    if not (images/name).exists():
                        im.save(images/name,'WEBP',lossless=True,method=6)
                    image_map[local]={'name':name,'width':im.width,'height':im.height}
                source_bytes+=local.stat().st_size
            return f'![{label}](../assets/images/{image_map[local]["name"]})'
        assert local in source_map, f'Unmapped local link: {local}'
        return f'[{label}]({source_map[local]}.md'+('#'+fragment if sep else '')+')'
    s=re.sub(r'(!?)\[([^\]]*)\]\((<[^>]+>|[^)]+)\)',replace,s)
    assert '/Users/' not in s, f'Local path remains in {r["id"]}'
    (content/(r['id']+'.md')).write_text(s)
    r['original_file']=r.pop('source').name
manifest={'courses':len(courses),'documents':len(records),'source_images':len(image_map),'image_source_bytes':source_bytes,'image_web_bytes':sum(x.stat().st_size for x in images.glob('*.webp')),'records':records,'images':{v['name']:v for v in image_map.values()}}
(PROJECT/'catalog.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in manifest.items() if k not in ('records','images')},ensure_ascii=False))
