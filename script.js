// script.js - 主要的网站交互脚本

// 标签页切换功能
function showTab(tabName) {
// 隐藏所有标签页内容
const tabContents = document.querySelectorAll('.tab-content');
tabContents.forEach(tab => {
  tab.classList.remove('active');
});

// 移除所有标签的active类
const navTabs = document.querySelectorAll('.nav-tab');
navTabs.forEach(tab => {
  tab.classList.remove('active');
});

// 显示选中的标签页
const selectedTab = document.getElementById(tabName);
if (selectedTab) {
  selectedTab.classList.add('active');
}

// 添加active类到对应的导航标签
const activeNavTab = document.querySelector(`[onclick="showTab('${tabName}')"]`);
if (activeNavTab) {
  activeNavTab.classList.add('active');
}
}

// 页面加载完成后的初始化
document.addEventListener('DOMContentLoaded', function() {
// 显示加载指示器
showLoadingIndicator();

// 设置最后更新时间
updateLastModified();

// 初始化数据加载
initializeDataLoading();
});

// 显示加载指示器
function showLoadingIndicator() {
const indicator = document.getElementById('loading-indicator');
if (indicator) {
  indicator.style.display = 'flex';
}
}

// 隐藏加载指示器
function hideLoadingIndicator() {
const indicator = document.getElementById('loading-indicator');
if (indicator) {
  indicator.classList.add('hidden');
  setTimeout(() => {
    indicator.style.display = 'none';
  }, 300);
}
}

// 设置最后更新时间
function updateLastModified() {
const lastModifiedElement = document.getElementById('last-modified');
if (lastModifiedElement) {
  const now = new Date();
  lastModifiedElement.textContent = now.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
}
}

// 初始化数据加载
async function initializeDataLoading() {
try {
  // 等待数据加载器准备就绪
  if (typeof personalData !== 'undefined') {
    await personalData.loadData();
    await updateAllPageContent();
  } else {
    console.warn('Personal data loader not found, using static content');
  }
} catch (error) {
  console.error('Error loading personal data:', error);
  // 如果数据加载失败，使用静态内容
  loadStaticContent();
} finally {
  hideLoadingIndicator();
}
}

// 更新所有页面内容
async function updateAllPageContent() {
if (!personalData || !personalData.data) {
  console.warn('No personal data available');
  return;
}

try {
  await updateHeaderInfo();
  await updateAboutPage();
  await updateEducationPage();
  await updatePublicationsPage();
  await updateProjectsPage();
  await updateContactPage();
} catch (error) {
  console.error('Error updating page content:', error);
}
}

// 更新头部信息
async function updateHeaderInfo() {
const personal = await personalData.getPersonalInfo();

const h1 = document.querySelector('h1');
const subtitle = document.querySelector('.subtitle');
const currentPosition = document.querySelector('.current-position');
const locationInfo = document.querySelector('.location-info');
const profileImg = document.querySelector('.profile-img');

if (h1) h1.textContent = `${personal.name?.english || 'Yi Lu'} (${personal.name?.chinese || '陆艺'})`;
if (subtitle) subtitle.textContent = personal.title || 'PhD Student in Algebraic Geometry';
if (currentPosition) currentPosition.textContent = personal.current_position || 'Capital Normal University & University of Liverpool';
if (locationInfo) locationInfo.textContent = personal.locations?.join(' | ') || 'Beijing, China | Liverpool, United Kingdom';
if (profileImg) profileImg.textContent = personal.profile_initials || 'YL';
}

// 更新About页面
async function updateAboutPage() {
await updateCurrentPosition();
await updateSupervisionInfo();
await updateResearchInterests();
}

// 更新当前职位
async function updateCurrentPosition() {
const currentEdu = await personalData.getCurrentEducation();
const card = document.getElementById('current-position-card');

if (!card || !currentEdu.length) return;

const content = currentEdu.map(edu => `
  <div class="experience-item">
    <h3>${edu.degree}</h3>
    <p><strong>${edu.institution}</strong></p>
    <p class="date">${edu.period}</p>
    <p>${edu.department}</p>
    ${edu.program ? `<p>${edu.program}</p>` : ''}
    ${edu.specialization ? `<p>Research Focus: ${edu.specialization}</p>` : ''}
  </div>
`).join('');

card.innerHTML = `<h2>🎓 Current Position</h2>${content}`;
}

// 更新导师信息
async function updateSupervisionInfo() {
const currentEdu = await personalData.getCurrentEducation();
const card = document.getElementById('supervision-card');

if (!card) return;

const allSupervisors = [];
currentEdu.forEach(edu => {
  if (edu.supervisor) allSupervisors.push(edu.supervisor);
  if (edu.supervisors) allSupervisors.push(...edu.supervisors);
});

const supervisorHTML = allSupervisors.map(supervisor => `
  <div class="supervisor-item">
    <h4>${supervisor.role}</h4>
    <p><strong>${supervisor.name}</strong></p>
    ${supervisor.institution ? `<p>${supervisor.institution}</p>` : ''}
  </div>
`).join('');

card.innerHTML = `
  <h2>👨‍🏫 Supervision</h2>
  <div class="supervisor-info">
    ${supervisorHTML}
  </div>
`;
}

// 更新研究兴趣
async function updateResearchInterests() {
const research = await personalData.getResearchInfo();
const skillsGrid = document.querySelector('.skills-grid');

if (!skillsGrid || !research.interests) return;

let skillsHTML = research.interests.map(interest => 
  `<div class="skill-item">${interest}</div>`
).join('');

// 添加跳转链接
if (research.interests_detail_link) {
  skillsHTML += `
    <div class="interest-detail-link">
      <a href="${research.interests_detail_link}" target="_blank" class="project-link">
        📝 Prompt of my Interest
      </a>
    </div>
  `;
}

skillsGrid.innerHTML = skillsHTML;
}

// 更新教育页面
async function updateEducationPage() {
const education = await personalData.getEducation();
const card = document.getElementById('education-card');

if (!card || !education.length) return;

const content = education.map(edu => `
  <div class="education-item">
    <h3>${edu.degree}</h3>
    <p><strong>${edu.institution}</strong>${edu.location ? ` - ${edu.location}` : ''}</p>
    <p class="date">${edu.period}</p>
    ${edu.department ? `<p>${edu.department}</p>` : ''}
    ${edu.program ? `<p>${edu.program}</p>` : ''}
    ${edu.specialization ? `<p>Research Focus: ${edu.specialization}</p>` : ''}
    ${edu.major ? `<p>Major: ${edu.major}</p>` : ''}
    ${edu.note ? `<p><em>${edu.note}</em></p>` : ''}
  </div>
`).join('');

card.innerHTML = `<h2>🎓 Education</h2>${content}`;
}

// 更新出版物页面
async function updatePublicationsPage() {
const publications = await personalData.getPublications();
const card = document.getElementById('publications-card');

if (!card) return;

let content = '<h2>📄 Publications</h2>';

// 期刊论文
content += '<div class="publication-section"><h3>Journal Articles</h3>';
if (publications.journal_articles && publications.journal_articles.some(p => p.title && p.title !== '-')) {
  publications.journal_articles.filter(p => p.title && p.title !== '-').forEach(paper => {
    content += `
      <div class="publication-item">
        <p><strong>${paper.title}</strong></p>
        <p>${paper.authors.join(', ')}</p>
        <p><em>${paper.journal}</em>, ${paper.year}</p>
        ${paper.doi && paper.doi !== '-' ? `<p>DOI: ${paper.doi}</p>` : ''}
      </div>
    `;
  });
} else {
  content += '<div class="placeholder">[Published papers will be listed here]</div>';
}
content += '</div>';

// 会议论文部分
content += '<div class="publication-section"><h3>📄 Conference Papers</h3>';
if (publications.conference_papers && publications.conference_papers.some(p => p.title && p.title !== '-')) {
  publications.conference_papers.filter(p => p.title && p.title !== '-').forEach(paper => {
    content += `
      <div class="publication-item">
        <p><strong>${paper.title}</strong></p>
        <p>${paper.authors.join(', ')}</p>
        <p><em>${paper.conference}</em>, ${paper.location} (${paper.year})</p>
        ${paper.pages && paper.pages !== '-' ? `<p>Pages: ${paper.pages}</p>` : ''}
        ${paper.publisher && paper.publisher !== '-' ? `<p>Publisher: ${paper.publisher}</p>` : ''}
        ${paper.doi && paper.doi !== '-' ? `<p>DOI: ${paper.doi}</p>` : ''}
      </div>
    `;
  });
} else {
  content += '<div class="placeholder">[Conference papers will be listed here]</div>';
}
content += '</div>';

// 预印本
content += '<div class="publication-section"><h3>📝 Preprints & Working Papers</h3>';
if (publications.preprints && publications.preprints.some(p => p.title && p.title !== '-')) {
  publications.preprints.filter(p => p.title && p.title !== '-').forEach(paper => {
    content += `
      <div class="publication-item">
        <p><strong>${paper.title}</strong></p>
        <p>${paper.authors.join(', ')}</p>
        ${paper.arxiv ? `<p>arXiv: <a href="https://arxiv.org/abs/${paper.arxiv}" target="_blank">${paper.arxiv}</a></p>` : ''}
        <p>Year: ${paper.year}</p>
      </div>
    `;
  });
} else {
  content += '<div class="placeholder">[Preprints will be listed here]</div>';
}
content += '</div>';

// Notes & Presentations
content += '<div class="publication-section"><h3>📋 Notes & Presentations</h3>';
if (publications.notes_and_presentations && publications.notes_and_presentations.length) {
  publications.notes_and_presentations.forEach(item => {
    content += `
      <div class="publication-item">
        <p><strong>${item.title}</strong></p>
        <p>${item.content} (${item.type})</p>
        <p>Year: ${item.year}</p>
        ${item.pdf_link ? `<p><a href="${item.pdf_link}" target="_blank" class="project-link">📄 View PDF</a></p>` : ''}
      </div>
    `;
  });
} else {
  content += '<div class="placeholder">[Notes and presentations will be listed here]</div>';
}
content += '</div>';

card.innerHTML = content;
}

// 更新项目页面
async function updateProjectsPage() {
const projects = await personalData.getProjects();
const card = document.getElementById('projects-card');

if (!card) return;

let content = '<h2>💼 Projects</h2>';

if (projects.sections && projects.sections.length) {
  projects.sections.forEach(section => {
    content += `<div class="project-section"><h3>${section.title}</h3>`;
    
    section.items.forEach(project => {
      content += `
        <div class="project-item">
          <h4>${project.name}</h4>
          <p>${project.description}</p>
          <div class="project-meta">
            <span class="project-year">${project.year}</span>
            <span class="project-status">${project.status}</span>
          </div>
          ${project.technologies ? `
            <div class="tech-tags">
              ${project.technologies.map(tech => `<span class="tech-tag">${tech}</span>`).join('')}
            </div>
          ` : ''}
          ${project.features ? `
            <ul class="project-features">
              ${project.features.map(feature => `<li>${feature}</li>`).join('')}
            </ul>
          ` : ''}
          ${project.result ? `<p class="project-result"><strong>Result:</strong> ${project.result}</p>` : ''}
          ${project.team ? `<p><strong>Team:</strong> ${project.team.join(', ')}</p>` : ''}
          <div class="project-links">
            ${project.link ? `<a href="${project.link}" target="_blank" class="project-link">🔗 View Project</a>` : ''}
            ${project.github ? `<a href="${project.github}" target="_blank" class="project-link">📂 GitHub</a>` : ''}
            ${project.documentation ? `<a href="${project.documentation}" target="_blank" class="project-link">📚 Documentation</a>` : ''}
          </div>
        </div>
      `;
    });
    
    content += '</div>';
  });
} else {
  content += '<div class="placeholder">[Projects will be listed here]</div>';
}

card.innerHTML = content;
}

// 更新联系页面
async function updateContactPage() {
const contact = await personalData.getContactInfo();
const card = document.getElementById('contact-card');

if (!card) return;

let content = '<h2>📞 Contact Information</h2>';

// 邮箱信息
if (contact.emails && contact.emails.length) {
  content += '<div class="contact-section"><h3>📧 Email Addresses</h3>';
  contact.emails.forEach(email => {
    content += `
      <div class="contact-item">
        <p><strong>${email.type}:</strong> <a href="mailto:${email.address}">${email.address}</a></p>
        <p class="contact-description">${email.description}</p>
      </div>
    `;
  });
  content += '</div>';
}

// 地址信息
if (contact.addresses) {
  content += '<div class="contact-section"><h3>🏢 Addresses</h3>';
  
  if (contact.addresses.primary) {
    const addr = contact.addresses.primary;
    content += `
      <div class="contact-item">
        <h4>Primary Address</h4>
        <p><strong>${addr.institution}</strong></p>
        <p>${addr.department}</p>
        <p>${addr.address}</p>
        <p>${addr.city}, ${addr.country} ${addr.postal_code}</p>
      </div>
    `;
  }
  
  if (contact.addresses.visiting) {
    const addr = contact.addresses.visiting;
    content += `
      <div class="contact-item">
        <h4>Visiting Address</h4>
        <p><strong>${addr.institution}</strong></p>
        <p>${addr.department}</p>
        <p>${addr.address}</p>
        <p>${addr.city}, ${addr.country} ${addr.postal_code}</p>
      </div>
    `;
  }
  
  content += '</div>';
}

// 社交媒体
if (contact.social_media && Object.keys(contact.social_media).length) {
  content += '<div class="contact-section"><h3>🌐 Online Profiles</h3>';
  Object.entries(contact.social_media).forEach(([platform, url]) => {
    if (url) {
      content += `
        <div class="contact-item">
          <p><strong>${platform.charAt(0).toUpperCase() + platform.slice(1)}:</strong> 
          <a href="${url}" target="_blank">${url}</a></p>
        </div>
      `;
    }
  });
  content += '</div>';
}

card.innerHTML = content;
}

// 加载静态内容的后备函数
function loadStaticContent() {
console.log('Loading static content as fallback');
// 这里可以添加静态内容的加载逻辑
}