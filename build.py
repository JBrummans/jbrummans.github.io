import os
import markdown
import shutil
from datetime import datetime

# Configuration
POSTS_DIR = './posts'
INCLUDES_DIR = './_includes'
POSTS_OUTPUT_DIR = './site' # Subfolder for posts
ROOT_OUTPUT_DIR = '.'       # Root for index.html

# 1. Setup Output Directory for Posts
if os.path.exists(POSTS_OUTPUT_DIR):
    shutil.rmtree(POSTS_OUTPUT_DIR)
os.makedirs(POSTS_OUTPUT_DIR)

# 2. Load Templates
def load_include(filename):
    path = os.path.join(INCLUDES_DIR, filename)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

raw_header = load_include('header.html')
raw_footer = load_include('footer.html')

# 3. Parse Markdown Files
posts = []
md = markdown.Markdown(extensions=[
    'meta', 
    'fenced_code', 
    'codehilite', 
    'pymdownx.tilde'  # <--- Adds ~~ support
    # 'pymdownx.github' # <--- Alternatively, adds ALL GitHub features (tables, etc)
])

print("🔨 Building site...")

for filename in os.listdir(POSTS_DIR):
    if filename.endswith(".md"):
        filepath = os.path.join(POSTS_DIR, filename)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            raw_content = f.read()
            html_content = md.convert(raw_content)
            
            # Extract Metadata
            meta = md.Meta if hasattr(md, 'Meta') else {}
            title = meta.get('title', [filename.replace('.md', '')])[0]
            date_str = meta.get('date', ['1970-01-01'])[0]
            
            slug = filename.replace('.md', '.html')
            
            posts.append({
                'title': title,
                'date': date_str,
                'slug': slug,
                'content': html_content
            })
            md.reset()

# 4. Write Individual Post Pages (Inside ./site folder)
for post in posts:
    # ADJUST PATHS: Since posts are in ./site/, we need to go up one level (../) 
    # to find style.css and index.html
    post_header = raw_header.replace('href="style.css"', 'href="../style.css"') \
                            .replace('href="index.html"', 'href="../index.html"')

    page_html = f"""
{post_header}
<article class="post-content">
    <h1>{post['title']}</h1>
    <small>{post['date']}</small>
    <hr>
    {post['content']}
</article>
{raw_footer}
"""
    
    out_path = os.path.join(POSTS_OUTPUT_DIR, post['slug'])
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(page_html)
    print(f"   Generated: site/{post['slug']}")

# 5. Generate Homepage (At Root)
posts.sort(key=lambda x: x['date'], reverse=True)

list_items = []
for post in posts:
    # ADJUST LINKS: The index is at root, so it must point into site/ folder
    link_to_post = f"site/{post['slug']}"
    
    item = f"""
    <div class="news-item">
        <span class="news-date">[{post['date']}]</span>
        <a href="{link_to_post}" class="news-link">{post['title']}</a>
    </div>
    """
    list_items.append(item)

index_html = f"""
{raw_header}
<div class="news-aggregator">
    <h2>Latest Updates</h2>
    <div class="news-list">
        {''.join(list_items)}
    </div>
</div>
{raw_footer}
"""

with open(os.path.join(ROOT_OUTPUT_DIR, 'index.html'), 'w', encoding='utf-8') as f:
    f.write(index_html)

print("✅ Build complete! Index is at root, posts are in ./site/")