// tab 路由 + 按需加载 section 片段与数据 (webpage/main.js)
// 依赖：marked.js（CDN，blog 渲染 md 时动态加载）

const tabs      = document.querySelectorAll('nav a[data-tab]'); // nav 链接
const container = document.getElementById('main-content');      // 挂载点
const cache     = {};                                            // HTML 片段缓存

// 加载 HTML 片段后注入容器，再渲染对应数据
async function activate(id) {
  tabs.forEach(a => a.classList.toggle('active', a.dataset.tab === id));
  history.replaceState(null, '', '#' + id);

  if (!cache[id]) {
    const res = await fetch(`website_pages/${id}.html`);
    cache[id] = await res.text();
  }
  container.innerHTML = cache[id];

  const renderers = { about: renderAbout, papers: renderPapers, code: renderCode, blog: renderBlog };
  if (renderers[id]) await renderers[id]();
}



// ----- 数据渲染 -----


async function fetchJSON(file) {
  const res = await fetch(`website_data/${file}`, { cache: 'no-store' });   // 禁用 JSON 缓存
  return res.json();
}


async function renderAbout() {
  const d = await fetchJSON('profile.json');

  document.title                                              = d.name + "'s Personal Website";
  document.getElementById('site-name').textContent            = d.name;
  document.querySelector('.about-info h1').textContent        = d.name;
  document.querySelector('.about-info .position').textContent = d.position;
  document.querySelector('.about-info .bio').innerHTML = d.bio;
  if (d.cv_pdf) {
    document.getElementById('cv-link').innerHTML =
      `<a class="cv-dl-btn" href="${d.cv_pdf}" download>CV ↓</a>`;
  }

  const linksEl = document.querySelector('.links');
  linksEl.innerHTML = d.links.map(l =>
    `<div class="link-row">
      <span class="link-label">${l.label}</span>
      <a href="${l.url}" ${l.url.startsWith('http') ? 'target="_blank"' : ''}>${l.display}</a>
    </div>`
  ).join('');

  const expEl = document.getElementById('experience-list');
  expEl.innerHTML = (d.experiences || []).map((cat, i) => `
    <div class="exp-category">
      <div class="exp-cat-title" data-idx="${i}">
        <span class="exp-arrow">▶</span>${cat.category}
      </div>
      <div class="exp-items">
        ${cat.category === 'Education'
          ? cat.items.map(item => `
            <div class="exp-item">
              <div class="exp-item-title">${item.degree}</div>
              ${item.institution ? `<div class="exp-item-sub"><span class="exp-item-key">Organisation</span> ${item.institution}</div>` : ''}
              ${item.period      ? `<div class="exp-item-sub"><span class="exp-item-key">Period</span> ${item.period}</div>`      : ''}
              ${item.desc        ? `<div class="exp-item-desc">${item.desc}</div>`        : ''}
            </div>`).join('')
          : cat.category === 'Teaching & Work'
          ? cat.items.map(item => `
            <div class="exp-item">
              <div class="exp-item-title">${item.role}</div>
              <div class="exp-item-content">${item.content}</div>
              ${item.institution ? `<div class="exp-item-sub"><span class="exp-item-key">Organisation</span> ${item.institution}</div>` : ''}
              ${item.period      ? `<div class="exp-item-sub"><span class="exp-item-key">Period</span> ${item.period}</div>`      : ''}
              ${item.desc        ? `<div class="exp-item-desc">${item.desc}</div>`        : ''}
            </div>`).join('')
          : cat.category === 'Academic Activities'
          ? cat.items.map(item => `
            <div class="exp-item">
              <div class="exp-item-title">${item.talk}</div>
              ${item.conference ? `<div class="exp-item-sub"><span class="exp-item-key">Conference</span> ${item.conference}</div>` : ''}
              ${item.location   ? `<div class="exp-item-sub"><span class="exp-item-key">Location</span> ${item.location}</div>`   : ''}
              ${item.period     ? `<div class="exp-item-sub"><span class="exp-item-key">Period</span> ${item.period}</div>`     : ''}
              ${item.desc       ? `<div class="exp-item-desc">${item.desc}</div>`      : ''}
            </div>`).join('')
          : cat.category === 'Awards, Scholarships & Certificates'
          ? cat.items.map(item => `
            <div class="exp-item">
              <div class="exp-item-title">${item.name}</div>
              ${item.result ? `<div class="exp-item-sub"><span class="exp-item-key">Result</span> ${item.result}</div>` : ''}
              ${item.issuer ? `<div class="exp-item-sub"><span class="exp-item-key">Issuer</span> ${item.issuer}</div>` : ''}
              ${item.period ? `<div class="exp-item-sub"><span class="exp-item-key">Period</span> ${item.period}</div>` : ''}
              ${item.desc   ? `<div class="exp-item-desc">${item.desc}</div>`  : ''}
            </div>`).join('')
          : cat.items.map(item => `
            <div class="exp-item">
              <div class="exp-item-title">${item.title}</div>
              ${item.period ? `<div class="exp-item-sub"><span class="exp-item-key">Period</span> ${item.period}</div>` : ''}
              ${item.desc   ? `<div class="exp-item-desc">${item.desc}</div>` : ''}
            </div>`).join('')
        }
      </div>
    </div>`).join('');

  // 折叠事件，默认全部折叠
  expEl.querySelectorAll('.exp-cat-title').forEach(title => {
    const body  = title.nextElementSibling; // exp-items
    const arrow = title.querySelector('.exp-arrow');
    body.style.display = 'none';            // 默认折叠
    title.style.cursor = 'pointer';
    title.addEventListener('click', () => {
      const open = body.style.display === 'none';
      body.style.display  = open ? 'block' : 'none';
      arrow.textContent   = open ? '▼' : '▶';
    });
  });
}

function tagsHTML(tags) {
  return (tags || []).map(t => `<span class="tag">${t}</span>`).join('');
}

function cardLinksHTML(links) {
  return (links || []).map(l => `<a href="${l.url}">${l.label}</a>`).join('');
}

// 递归渲染任意层级可折叠树；节点有 children 则为分组，否则为叶子
function renderTree(el, nodes, itemHTML, depth = 0) {
  el.innerHTML = nodes.map((node, i) => {
    if (node.children) {
      // 分组节点：递归展开 children
      const levelClass = depth === 0 ? 'tree-header-l1' : depth === 1 ? 'tree-header-l2' : '';
      const bodyClass  = depth === 0 ? 'tree-body-l1'   : '';
      const count      = countLeaves(node); // 叶子总数
      return `
        <div class="tree-group">
          <div class="tree-header ${levelClass}" data-idx="${i}">
            <span class="tree-arrow">▶</span>
            <span>${node.category}</span>
            <span class="tree-count">${count}</span>
          </div>
          <div class="tree-body ${bodyClass}" data-depth="${depth}"></div>
        </div>`;
    } else {
      // 叶子节点：直接渲染卡片
      return itemHTML(node);
    }
  }).join('');

  // 递归填充子节点
  const groups = Array.from(el.children).filter(c => c.classList.contains('tree-group'));
  nodes.filter(n => n.children).forEach((node, gi) => {
    renderTree(groups[gi].querySelector('.tree-body'), node.children, itemHTML, depth + 1);
  });

  // 折叠事件
  el.querySelectorAll(':scope > .tree-group > .tree-header').forEach(h => {
    h.addEventListener('click', () => {
      const body  = h.nextElementSibling;
      const arrow = h.querySelector('.tree-arrow');
      const open  = body.classList.toggle('open');
      arrow.textContent = open ? '▼' : '▶';
    });
  });
}

// 统计叶子节点数量
function countLeaves(node) {
  if (!node.children) return 1;
  return node.children.reduce((s, c) => s + countLeaves(c), 0);
}


async function renderPapers() {
  const list = await fetchJSON('papers.json');
  renderTree(document.getElementById('papers-list'), list.data, p => {
    const boldSet = new Set(p.bold_authors || []);
    const authorsHTML = (p.authors || [])
      .map(a => boldSet.has(a) ? `<strong>${a}</strong>` : a)
      .join(', ');
    return `
    <div class="card">
      <div class="card-title">${p.title}</div>
      <div class="card-meta">${authorsHTML} · <em>${p.venue}</em> · ${p.year}</div>
      <div class="card-desc">${p.desc}</div>
      <div>${tagsHTML(p.tags)}</div>
      <div class="card-links">${cardLinksHTML(p.links)}</div>
    </div>`;
  });
}


async function renderCode() {
  const list = await fetchJSON('code.json');
  renderTree(document.getElementById('code-list'), list.data, p => `
    <div class="card">
      <div class="card-title">${p.name}</div>
      <div class="card-meta">${Array.isArray(p.lang) ? p.lang.join(', ') : (p.lang || '')} · ${p.year}</div>
      <div class="card-desc">${p.desc}</div>
      <div>${tagsHTML(p.tags)}</div>
      <div class="card-links">${cardLinksHTML(p.links)}</div>
    </div>`);
}

// ----- Blog -----

// 动态加载 marked.js（Markdown 渲染）
function loadMarked() {
  return new Promise(resolve => {
    if (window.marked) return resolve();
    const s = document.createElement('script');
    s.src = 'https://cdn.jsdelivr.net/npm/marked/marked.min.js';
    s.onload = resolve;
    document.head.appendChild(s);
  });
}
// marked 解析前保护公式，防止 _ 被转义
function protectedMarkedParse(src) {
  const store = [];

  const save = (m) => { store.push(m); return `\x02MATH${store.length - 1}\x03`; };

  // 先保护块级 $$...$$
  src = src.replace(/\$\$([\s\S]+?)\$\$/g, save);
  // 再保护行内 $...$（不含换行的单个 $）
  src = src.replace(/\$([^\$\r\n]+?)\$/g, save);

  let html = window.marked.parse(src);

  // marked 可能把占位符包在 <p>、<code> 里，用宽松匹配还原
  html = html.replace(/\x02MATH(\d+)\x03/g, (_, i) => store[+i]);
  return html;
}

function loadMathJax() {
  return new Promise(resolve => {
    if (window.MathJax) return resolve();
    window.MathJax = {
      tex: { inlineMath: [['$', '$'], ['\\(', '\\)']] },
      startup: { ready() { MathJax.startup.defaultReady(); resolve(); } }
    };
    const s = document.createElement('script');
    s.src = 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js';
    document.head.appendChild(s);
  });
}


// 根据条目类型生成操作链接
function blogActionHTML(p) {
  const types = Array.isArray(p.type) ? p.type : [p.type];
  return types.map(t => {
    if (t === 'md')  return `<a href="#" class="blog-open-md" data-file="${p.file}">Read</a>`;
    if (t === 'tex') return `<a href="#" class="blog-open-tex" data-file="${p.tex}">View .tex</a>
                             <a href="${p.tex}" download>Download .tex</a>`;
    if (t === 'pdf') return `<a href="#" class="blog-open-pdf" data-file="${p.pdf}" data-title="${p.title}">View PDF</a>`;
    return '';
  }).join('');
}

// 打开 md 文章页，并将文件路径写入 hash
async function openMdPost(file) {
  history.replaceState(null, '', '#blog/' + encodeURIComponent(file));
  await loadMarked();
  await loadMathJax();
  const res      = await fetch(file, { cache: 'no-store' });
  const text     = await res.text();
  const filename = file.split('/').pop();

  container.innerHTML = `
    <div class="post-page">
      <div class="post-subnav">
        <button class="post-back">← Back</button>
        <div class="post-subnav-actions">
          <a class="post-action-btn" href="${file}" download="${filename}">↓ Download</a>
          <button class="post-action-btn" id="post-copy-btn">⎘ Copy</button>
        </div>
      </div>
      <div class="post-content">${protectedMarkedParse(text)}</div>
    </div>`;

  container.querySelector('.post-back').addEventListener('click', () => activate('blog'));
  container.querySelector('#post-copy-btn').addEventListener('click', () => {
    navigator.clipboard.writeText(text).then(() => {
      const btn = container.querySelector('#post-copy-btn');
      btn.textContent = '✓ Copied';
      setTimeout(() => btn.textContent = '⎘ Copy', 2000);
    });
  });

  // ↓↓↓ 新增：修正图片路径 ↓↓↓
  const baseDir = file.substring(0, file.lastIndexOf('/') + 1);
  container.querySelectorAll('.post-content img').forEach(img => {
    const src = img.getAttribute('src');
    if (src && !src.startsWith('http') && !src.startsWith('/')) {
      img.src = baseDir + src;
    }
  });
  // ↑↑↑ 新增结束 ↑↑↑

  MathJax.typesetPromise([container.querySelector('.post-content')]);
}


// 打开 pdf 文章页，并将文件路径写入 hash
function openPdfPost(file) {
  history.replaceState(null, '', '#blog/' + encodeURIComponent(file));
  const filename = file.split('/').pop(); // 下载文件名

  container.innerHTML = `
    <div class="post-page post-page--pdf">
      <div class="post-subnav">
        <button class="post-back">← Back</button>
        <div class="post-subnav-actions">
          <a class="post-action-btn" href="${file}" download="${filename}">↓ Download</a>
        </div>
      </div>
      <iframe class="pdf-embed" src="${file}"></iframe>
    </div>`;

  container.querySelector('.post-back').addEventListener('click', () => activate('blog'));
}

async function renderBlog() {
  const list = await fetchJSON('blog.json');
  renderTree(document.getElementById('blog-list'), list.data, p => `
    <div class="card">
      <div class="card-title">${p.title}</div>
      <div class="blog-date">${p.date}</div>
      <div class="card-desc">${p.desc}</div>
      <div class="card-links">${blogActionHTML(p)}</div>
    </div>`);

  // Markdown：替换 main-content 为渲染页
  // Markdown：替换 main-content 为渲染页
document.getElementById('blog-list').addEventListener('click', async e => {
  const mdLink = e.target.closest('.blog-open-md');
  if (!mdLink) return;
  e.preventDefault();
  await openMdPost(mdLink.dataset.file);
});



  // LaTeX：弹出源码覆盖层
  document.getElementById('blog-list').addEventListener('click', async e => {
    const texLink = e.target.closest('.blog-open-tex');
    if (!texLink) return;
    e.preventDefault();
    const res  = await fetch(texLink.dataset.file);
    const text = await res.text();
    openTexOverlay(text);
  });  
  // PDF：替换 main-content 为嵌入页
document.getElementById('blog-list').addEventListener('click', e => {
  const pdfLink = e.target.closest('.blog-open-pdf');
  if (!pdfLink) return;
  e.preventDefault();
  openPdfPost(pdfLink.dataset.file);
});


}
// 转义 HTML 特殊字符
function escapeHTML(str) {
  return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

// tex 源码覆盖层
function openTexOverlay(text) {
  const overlay = document.createElement('div');
  overlay.className = 'post-overlay';
  overlay.innerHTML = `
    <div class="post-overlay-inner">
      <button class="overlay-close">✕</button>
      <pre class="tex-preview">${escapeHTML(text)}</pre>
    </div>`;
  overlay.querySelector('.overlay-close').addEventListener('click', () => overlay.remove());
  document.body.appendChild(overlay);
}

// ----- QR Code -----

// 动态加载 qrcode 库
function loadQRLib() {
  return new Promise(resolve => {
    if (window.QRCode) return resolve();
    const s = document.createElement('script');
    s.src = 'https://cdn.jsdelivr.net/npm/qrcodejs/qrcode.min.js';
    s.onload = resolve;
    document.head.appendChild(s);
  });
}

document.getElementById('qr-btn').addEventListener('click', async () => {
  if (document.getElementById('qr-popup')) return; // 已打开则忽略
  await loadQRLib();

  const popup = document.createElement('div');
  popup.id = 'qr-popup';
  popup.innerHTML = `
    <div id="qr-popup-inner">
      <div id="qr-canvas"></div>
      <div class="qr-url">${location.href}</div>
      <button class="qr-close">✕</button>
    </div>`;
  document.body.appendChild(popup);

  new QRCode(document.getElementById('qr-canvas'), {
    text:   location.href,  // 当前页面 URL
    width:  180,
    height: 180,
  });

  popup.querySelector('.qr-close').addEventListener('click', () => popup.remove());
  popup.addEventListener('click', e => { if (e.target === popup) popup.remove(); });
});

// ----- 初始化 -----

tabs.forEach(a => {
  a.addEventListener('click', e => {
    e.preventDefault();
    activate(a.dataset.tab);
  });
});

// 解析 hash：支持 #blog/path 直接打开文章
const hash    = location.hash.slice(1);          // 去掉 #
const slashIdx = hash.indexOf('/');
if (slashIdx !== -1) {
  const tab  = hash.slice(0, slashIdx);          // 'blog'
  const file = decodeURIComponent(hash.slice(slashIdx + 1)); // 文件路径
  if (tab === 'blog') {
    // 先激活 blog tab（加载列表），再打开文章
    activate('blog').then(() => {
      const ext = file.split('.').pop();
      if (ext === 'pdf') openPdfPost(file);
      else               openMdPost(file);
    });
  } else {
    activate(tab);
  }
} else {
  activate(hash || 'about');
}
