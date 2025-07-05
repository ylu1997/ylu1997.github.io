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
    updateAllPageContent();
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
function updateAllPageContent() {
if (!personalData || !personalData.data) {
  console.warn('No personal data available');
  return;
}

try {
  updateHeaderInfo();
  updateAboutPage();
  updateEducationPage();
  updatePublicationsPage();
  updateProjectsPage();
  updateContactPage();
} catch (error) {
  console.error('Error updating page content:', error);
}
}

// 更新头部信息
function updateHeaderInfo() {
const personal = personalData.getPersonalInfo();

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
function updateAboutPage() {
updateCurrentPosition();
updateSupervisionInfo();
updateResearchInterests();
}

// 更新当前职位
function updateCurrentPosition() {
const currentEdu = personalData.getCurrentEducation();
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
function updateSupervisionInfo() {
const currentEdu = personalData.getCurrentEducation();
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
function updateResearchInterests() {
const research = personalData.getResearchInfo();
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
function updateEducationPage() {
const education = personalData.getEducation();
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

// 修改updatePublicationsPage函数中的Notes & Presentations部分
function updatePublicationsPage() {
const publications = personalData.getPublications();
const card = document.getElementById('publications-card');

if (!card) return;

let content = '<h2>📄 Publications</h2>';

// 期刊论文
content += '<div class="publication-section"><h3>Journal Articles</h3>';
if (publications.journal_articles && publications.journal_articles.some(p => p.title)) {
publications.journal_articles.filter(p => p.title).forEach(paper => {
  content += `
    <div class="publication-item">
      <p><strong>${paper.title}</strong></p>
      <p>${paper.authors.join(', ')}</p>
      <p><em>${paper.journal}</em>, ${paper.year}</p>
      ${paper.doi ? `<p>DOI: ${paper.doi}</p>` : ''}
    </div>
  `;
});
} else {
content += '<div class="placeholder">[Published papers will be listed here]</div>';
}
content += '</div>';

// 会议论文部分
content += '<div class="publication-section"><h3>📄 Conference Papers</h3>';
if (publications.conference_papers && publications.conference_papers.some(p => p.title)) {
publications.conference_papers.filter(p => p.title).forEach(paper => {
  content += `
    <div class="publication-item">
      <p><strong>${paper.title}</strong></p>
      <p>${paper.authors.join(', ')}</p>
      <p><em>${paper.conference}</em>, ${paper.location} (${paper.year})</p>
      ${paper.pages ? `<p>Pages: ${paper.pages}</p>` : ''}
      ${paper.publisher ? `<p>Publisher: ${paper.publisher}</p>` : ''}
      ${paper.doi ? `<p>DOI: ${paper.doi}</p>` : ''}
    </div>
  `;
});
} else {
content += '<div class="placeholder">[Conference papers will be listed here]</div>';
}
content += '</div>';

// 预印本
content += '<div class="publication-section"><h3>📝 Preprints & Working Papers</h3>';
if (publications.preprints && publications.preprints.some(p => p.title)) {
publications.preprints.filter(p => p.title).forEach(paper => {
  content += `
    <div class="publication-item">
      <p><strong>${paper.title}</strong></p>
      <p>${paper.authors.join(', ')}</p>
      <p>arXiv: ${paper.arxiv} (${paper.year})</p>
    </div>
  `;
});
} else {
content += '<div class="placeholder">[Preprints and working papers will be listed here]</div>';
}
content += '</div>';

// 合并的 Notes & Presentations 分栏
content += '<div class="publication-section"><h3>📚 Notes & Presentations</h3>';
if (publications.notes_and_presentations && publications.notes_and_presentations.length > 0) {
publications.notes_and_presentations.forEach(item => {
  content += `
    <div class="publication-item">
      <p><strong>${item.title}</strong></p>
      <p>${item.content}</p>
      <p><span class="item-type ${item.type.toLowerCase()}">${item.type}</span> • ${item.year}</p>
      ${item.pdf_link ? `<a href="${item.pdf_link}" class="project-link" target="_blank">📄 View PDF →</a>` : ''}
    </div>
  `;
});
} else {
content += '<div class="placeholder">[Academic notes and presentations will be listed here]</div>';
}
content += '</div>';

card.innerHTML = content;
}

// 修改updateProjectsPage函数，支持自定义分栏
function updateProjectsPage() {
const projects = personalData.getProjects();
const projectsGrid = document.querySelector('#projects-card .projects-grid');

if (!projectsGrid) return;

let content = '';

// 使用自定义分栏
if (projects.sections && projects.sections.length > 0) {
  projects.sections.forEach(section => {
    // 为每个分栏添加标题
    content += `<div class="project-section-title"><h3>${section.title}</h3></div>`;
    
    section.items.forEach(project => {
      content += `
        <div class="project-item">
          <h4>${project.name}</h4>
          <p>${project.description}</p>
          ${project.technologies ? `<p><strong>Technologies:</strong> ${project.technologies.join(', ')}</p>` : ''}
          ${project.year ? `<p class="date">${project.year}</p>` : ''}
          ${project.status ? `<p><strong>Status:</strong> ${project.status}</p>` : ''}
          ${project.result ? `<p><strong>Result:</strong> ${project.result}</p>` : ''}
          <a href="${project.link}" class="project-link" target="_blank">View Project →</a>
        </div>
      `;
    });
  });
} else {
  content = '<div class="placeholder">[Projects will be listed here]</div>';
}

projectsGrid.innerHTML = content;
}

// 修改updateContactPage函数，修复重复标题问题
function updateContactPage() {
const contact = personalData.getContactInfo();
const contactInfo = document.querySelector('#contact-card .contact-info');

if (!contactInfo || !contact) return;

// 构建多个email的HTML
let emailsHTML = '';
if (contact.emails && contact.emails.length > 0) {
  emailsHTML = `
    <div class="contact-item">
      <div style="font-size: 1.5em; margin-bottom: 10px;">📧</div>
      <strong>Email Addresses</strong><br>
      <div class="emails-list">
  `;
  
  contact.emails.forEach(email => {
    emailsHTML += `
      <div class="email-item">
        <span class="email-type">${email.type}:</span>
        <a href="mailto:${email.address}">${email.address}</a>
        ${email.description ? `<span class="email-desc">(${email.description})</span>` : ''}
      </div>
    `;
  });
  
  emailsHTML += `
      </div>
    </div>
  `;
}

const content = `
  ${emailsHTML}
  <div class="contact-item">
    <div style="font-size: 1.5em; margin-bottom: 10px;">📍</div>
    <strong>Primary Address</strong><br>
    ${contact.addresses?.primary?.institution || ''}<br>
    ${contact.addresses?.primary?.department || ''}<br>
    ${contact.addresses?.primary?.address || ''}<br>
    ${contact.addresses?.primary?.city || ''}, ${contact.addresses?.primary?.country || ''}<br>
    ${contact.addresses?.primary?.postal_code || ''}
  </div>
  <div class="contact-item">
    <div style="font-size: 1.5em; margin-bottom: 10px;">🏛️</div>
    <strong>Visiting Address</strong><br>
    ${contact.addresses?.visiting?.institution || ''}<br>
    ${contact.addresses?.visiting?.department || ''}<br>
    ${contact.addresses?.visiting?.address || ''}<br>
    ${contact.addresses?.visiting?.city || ''}, ${contact.addresses?.visiting?.country || ''}<br>
    ${contact.addresses?.visiting?.postal_code || ''}
  </div>
`;

contactInfo.innerHTML = content;

// 更新学术档案链接 - 不添加重复标题
const academicProfiles = document.querySelector('.academic-profiles .academic-profile-links');
if (academicProfiles && contact.academic_profiles) {
  const profiles = contact.academic_profiles;
  let linksContent = '';
  
  const profileNames = {
    orcid: 'ORCID',
    google_scholar: 'Google Scholar',
    researchgate: 'ResearchGate',
    arxiv: 'arXiv',
    mathscinet: 'MathSciNet'
  };

  Object.keys(profiles).forEach(key => {
    if (profiles[key] && profiles[key].trim() !== '' && profiles[key] !== '#') {
      linksContent += `<p><a href="${profiles[key]}" class="project-link" target="_blank">${profileNames[key] || key}</a></p>`;
    }
  });
  
  academicProfiles.innerHTML = linksContent || '<div class="placeholder">[Academic profile links will be listed here]</div>';
}

// 更新社交媒体链接 - 不添加重复标题
const socialMedia = document.querySelector('.social-media .social-media-links');
if (socialMedia && contact.social_media) {
  const social = contact.social_media;
  let socialContent = '';
  
  const socialNames = {
    github: 'GitHub',
    linkedin: 'LinkedIn', 
    twitter: 'Twitter'
  };

  Object.keys(social).forEach(key => {
    if (social[key] && social[key].trim() !== '' && social[key] !== '#') {
      socialContent += `<p><a href="${social[key]}" class="project-link" target="_blank">${socialNames[key] || key}</a></p>`;
    }
  });
  
  socialMedia.innerHTML = socialContent || '<div class="placeholder">[Social media links will be listed here]</div>';
}
}

// 加载静态内容的备用函数
function loadStaticContent() {
console.log('Loading static content as fallback');
hideLoadingIndicator();
}

