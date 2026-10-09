from pathlib import Path
from urllib.parse import urlsplit, unquote
import html, json, re, shutil
import markdown, yaml
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs'; OUT.mkdir(exist_ok=True)
(OUT/'read').mkdir(exist_ok=True)
shutil.copytree(ROOT/'site-assets',OUT/'assets',dirs_exist_ok=True)
(OUT/'.nojekyll').write_text('')
manifest=json.loads((ROOT/'catalog.json').read_text())
records=manifest['records']; by_id={r['id']:r for r in records}
groups={'A':'入门认知','B':'目标与规划','C':'知识地图','D':'日常训练','E':'比赛得分','F':'教练与教学','G':'家长支持','H':'考试变化'}

def esc(s):return html.escape(str(s),quote=True)
def page_path(key):return 'index.html' if key=='index' else 'read/'+key+'.html'
def body_and_meta(raw):
    if raw.startswith('---\n'):
        _,head,body=raw.split('---',2)
        return body,yaml.safe_load(head) or {}
    return raw,{}

def nav(current,prefix):
    output=[f'<a class="nav-home" href="{prefix}index.html">总索引与阅读路线</a>']
    for code,name in groups.items():
        items=[r for r in records if r.get('code','').startswith(code) and r['kind']=='slides']
        links=''.join(f'<a {"aria-current=page" if current.split("-")[0]==r["id"] else ""} href="{prefix}{page_path(r["id"])}"><span>{r["code"]}</span>{esc(r["title"])}</a>' for r in items)
        output.append(f'<details {"open" if current=="index" or current.upper().startswith(code) else ""}><summary>{code} · {name}<small>{len(items)}</small></summary><div class="nav-items">{links}</div></details>')
    output.append(f'<div class="supplements"><a href="{prefix}read/archive-list.html">归档与待下载清单</a></div>')
    return ''.join(output)

for r in records:
    home=r['id']=='index'; prefix='' if home else '../'
    raw=(ROOT/'content'/(r['id']+'.md')).read_text()
    body,meta=body_and_meta(raw)
    md=markdown.Markdown(extensions=['extra','toc','sane_lists'],extension_configs={'toc':{'permalink':False,'toc_depth':'2-3'}})
    soup=BeautifulSoup(md.convert(body),'html.parser')
    for a in soup.find_all('a',href=True):
        href=a['href']; parsed=urlsplit(href)
        if not parsed.scheme and parsed.path.endswith('.md'):
            key=Path(parsed.path).stem
            assert key in by_id,href
            a['href']=prefix+page_path(key)+('#'+parsed.fragment if parsed.fragment else '')
        elif parsed.scheme in ('http','https'):
            a['rel']='noopener noreferrer';a['target']='_blank'
    for im in soup.find_all('img',src=True):
        name=Path(im['src']).name; data=manifest['images'][name]
        im['src']=prefix+'assets/images/'+name
        im['width']=data['width'];im['height']=data['height'];im['loading']='lazy';im['decoding']='async'
        a=soup.new_tag('a',href=im['src'],target='_blank',rel='noopener',attrs={'class':'slide-link','aria-label':'打开原尺寸画面'})
        im.wrap(a)
    for table in soup.find_all('table'):
        wrap=soup.new_tag('div',attrs={'class':'table-scroll','tabindex':'0','aria-label':'横向滚动查看表格'})
        table.wrap(wrap)
    heading=soup.find('h1')
    if heading: heading.decompose()
    tabs='';source='';nextprev=''
    if r.get('code'):
        base=r['code'].lower()
        tabs='<nav class="version-tabs" aria-label="讲稿版本">'+''.join(f'<a {"aria-current=page" if r["kind"]==kind else ""} href="{base}{suffix}.html">{label}</a>' for suffix,kind,label in [('', 'slides','图文对照'),('-edited','edited','精编讲稿'),('-full','full','完整讲稿')])+'</nav>'
        mainmeta=body_and_meta((ROOT/'content'/(base+'.md')).read_text())[1]
        url=mainmeta.get('url','')
        if url.startswith('https://www.bilibili.com/'):
            source=f'<a href="{esc(url)}" target="_blank" rel="noopener">原视频</a>'
        slides=[x for x in records if x['kind']=='slides'];n=next(i for i,x in enumerate(slides) if x['id']==base)
        adjacent=[]
        if n:adjacent.append(f'<a href="{slides[n-1]["id"]}.html"><small>上一讲</small>{slides[n-1]["code"]} · {esc(slides[n-1]["title"])}</a>')
        if n+1<len(slides):adjacent.append(f'<a href="{slides[n+1]["id"]}.html"><small>下一讲</small>{slides[n+1]["code"]} · {esc(slides[n+1]["title"])}</a>')
        nextprev='<nav class="next-prev" aria-label="相邻课程">'+''.join(adjacent)+'</nav>'
        kicker=r['code']+' / '+groups[r['code'][0]]
        published = meta.get('原视频发布时间') or mainmeta.get('原视频发布时间')
        date_html = f'<time datetime="{esc(published)}">原视频发布于 {esc(published)}</time> · ' if published else ''
        info=date_html+f'{mainmeta.get("duration","")} · {mainmeta.get("slides",0)} 张画面'
    else:
        kicker='课程索引' if home else '补充阅读';info=f'{manifest["courses"]} 讲 · 8 个主题 · 约 11 小时' if home else '课程归档资料'
    download=prefix+'read/'+r['id']+'.md'
    (OUT/'read'/(r['id']+'.md')).write_text(raw)
    # Downloaded markdown has sibling markdown links; assets use the shared ../assets path.
    toc=md.toc
    doc=f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light dark"><meta name="description" content="信奥课程阅读库：{manifest["courses"]}讲课程的索引、PPT画面与讲稿，按主题系统阅读。"><title>{esc(r['title'])} · 信奥课程阅读库</title><link rel="icon" type="image/svg+xml" href="{prefix}assets/favicon.svg"><link rel="stylesheet" href="{prefix}assets/style.css"><script defer src="{prefix}assets/app.js"></script></head>
<body><a class="skip" href="#main">跳到正文</a><header class="topbar"><a class="brand" href="{prefix}index.html"><span class="brand-icon">OI</span><span>信奥课程阅读库</span></a><span class="top-caption">规划 · 训练 · 教学</span><button class="menu-button" aria-controls="navigation" aria-expanded="false">课程目录</button></header>
<div class="layout"><aside id="navigation" class="sidebar" aria-label="课程导航"><label class="search-label" for="course-search">查找课程</label><input id="course-search" type="search" placeholder="输入题目、家长、检查…" autocomplete="off"><p class="search-status" role="status" aria-live="polite"></p><nav>{nav(r['id'],prefix)}</nav><p class="sidebar-foot">按学习主题阅读 · 保留原讲稿</p></aside>
<main id="main"><header class="article-head"><p class="eyebrow">{esc(kicker)}</p><h1>{esc(r['title'])}</h1><div class="metadata"><span>{info}</span>{source}<a href="{download}" download>下载 Markdown</a></div></header>{tabs}<details class="page-toc"><summary>本页目录</summary>{toc}</details><article class="prose">{soup}</article>{nextprev}<footer class="footer">内容来自原课程及本地整理，观点与日期以原材料为准。<a href="{prefix}index.html">返回总索引</a><a href="#main">回到顶部</a></footer></main></div></body></html>'''
    target=OUT/page_path(r['id']);target.write_text(doc)
(OUT/'404.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>页面未找到</title><body><h1>页面未找到</h1><p><a href="/xinao-courses/">返回信奥课程总索引</a></p></body></html>')
# Crawl every local HTML reference, including anchors. No workstation paths can be published.
issues=[];checked=0
for f in OUT.rglob('*.html'):
    content=f.read_text();assert '/Users/' not in content,f
    soup=BeautifulSoup(content,'html.parser')
    for tag,attr in [('a','href'),('img','src'),('script','src'),('link','href')]:
        for el in soup.find_all(tag):
            ref=el.get(attr)
            if not ref:continue
            u=urlsplit(ref)
            if u.scheme or u.netloc:continue
            if ref.startswith('/xinao-courses/'):
                dest=OUT/unquote(u.path[len('/xinao-courses/'):])
            else:dest=(f.parent/unquote(u.path)).resolve() if u.path else f
            if dest.is_dir():dest=dest/'index.html'
            checked+=1
            if not dest.exists():issues.append((str(f),ref,'missing'))
            elif u.fragment and dest.suffix=='.html':
                target_soup=BeautifulSoup(dest.read_text(),'html.parser')
                if not target_soup.find(id=unquote(u.fragment)):issues.append((str(f),ref,'anchor'))
assert not issues,issues[:20]
report={'html_documents':len(records),'courses':manifest['courses'],'source_images':manifest['source_images'],'verified_links':checked,'broken_links':len(issues),'image_source_bytes':manifest['image_source_bytes'],'image_web_bytes':manifest['image_web_bytes']}
(ROOT/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False))
