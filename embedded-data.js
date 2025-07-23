// embedded-data.js - 分离版本
// 数据和逻辑分离，但保持外部调用接口不变

// 默认的嵌入数据（作为后备）
const defaultEmbeddedData = {
personal: {
  name: { english: "Yi Lu", chinese: "陆艺" },
  title: "PhD Student in Algebraic Geometry",
  email: "yi.lu@cnu.edu.cn"
},
// 简化的默认数据...
};

// 数据访问类
class PersonalDataManager {
constructor() {
  this.data = defaultEmbeddedData;
  this.isDataLoaded = false;
  this.loadPromise = null;
}

async loadData(jsonFile = './personal-data.json') {
  // 避免重复加载
  if (this.loadPromise) {
    return this.loadPromise;
  }

  this.loadPromise = this._loadDataInternal(jsonFile);
  return this.loadPromise;
}

async _loadDataInternal(jsonFile) {
  try {
    const response = await fetch(jsonFile);
    if (response.ok) {
      const externalData = await response.json();
      this.data = externalData;
      this.isDataLoaded = true;
      console.log('External JSON data loaded successfully from:', jsonFile);
    } else {
      console.warn('Could not load external JSON, using default data. Status:', response.status);
    }
  } catch (error) {
    console.warn('Could not load external JSON, using default data:', error.message);
  }
  return this.data;
}

// 确保数据已加载的辅助方法
async ensureDataLoaded() {
  if (!this.isDataLoaded && !this.loadPromise) {
    await this.loadData();
  } else if (this.loadPromise) {
    await this.loadPromise;
  }
  return this.data;
}

async getPersonalInfo() {
  await this.ensureDataLoaded();
  return this.data.personal || {};
}

async getEducation() {
  await this.ensureDataLoaded();
  return this.data.education || [];
}

async getCurrentEducation() {
  await this.ensureDataLoaded();
  return this.data.education?.filter(edu => 
    edu.period && edu.period.includes('Present')
  ) || [];
}

async getResearchInfo() {
  await this.ensureDataLoaded();
  return this.data.research || {};
}

async getPublications() {
  await this.ensureDataLoaded();
  return this.data.publications || {};
}

async getProjects() {
  await this.ensureDataLoaded();
  return this.data.projects || {};
}

async getContactInfo() {
  await this.ensureDataLoaded();
  return this.data.contact || {};
}

// 辅助方法：获取所有导师信息
async getAllSupervisors() {
  await this.ensureDataLoaded();
  const supervisors = [];
  this.data.education?.forEach(edu => {
    if (edu.supervisor) supervisors.push(edu.supervisor);
    if (edu.supervisors) supervisors.push(...edu.supervisors);
  });
  return supervisors;
}

// 辅助方法：获取当前导师
async getCurrentSupervisors() {
  const currentEdu = await this.getCurrentEducation();
  const supervisors = [];
  currentEdu.forEach(edu => {
    if (edu.supervisor) supervisors.push(edu.supervisor);
    if (edu.supervisors) supervisors.push(...edu.supervisors);
  });
  return supervisors;
}

// 辅助方法：按年份排序出版物
async getPublicationsByYear() {
  await this.ensureDataLoaded();
  const pubs = this.data.publications || {};
  const allPubs = [
    ...(pubs.journal_articles || []),
    ...(pubs.preprints || []),
    ...(pubs.notes_and_presentations || [])
  ];
  return allPubs.sort((a, b) => (b.year || 0) - (a.year || 0));
}

// 辅助方法：获取最近的项目
async getRecentProjects(limit = 5) {
  await this.ensureDataLoaded();
  const projects = [];
  if (this.data.projects?.sections) {
    this.data.projects.sections.forEach(section => {
      projects.push(...section.items);
    });
  }
  return projects
    .sort((a, b) => (b.year || 0) - (a.year || 0))
    .slice(0, limit);
}

// 同步方法（为了向后兼容，但建议使用异步版本）
getPersonalInfoSync() {
  return this.data.personal || {};
}

getEducationSync() {
  return this.data.education || [];
}

getCurrentEducationSync() {
  return this.data.education?.filter(edu => 
    edu.period && edu.period.includes('Present')
  ) || [];
}

getResearchInfoSync() {
  return this.data.research || {};
}

getPublicationsSync() {
  return this.data.publications || {};
}

getProjectsSync() {
  return this.data.projects || {};
}

getContactInfoSync() {
  return this.data.contact || {};
}
}

// 创建全局实例
const personalData = new PersonalDataManager();

// 为了向后兼容，保持原有的 embeddedPersonalData 变量
// 但现在它会异步加载数据
let embeddedPersonalData = defaultEmbeddedData;

// 自动加载数据并更新 embeddedPersonalData
personalData.loadData().then(data => {
embeddedPersonalData = data;
});

// 导出数据（如果在Node.js环境中）
if (typeof module !== 'undefined' && module.exports) {
module.exports = { embeddedPersonalData, PersonalDataManager, personalData };
}

// 如果在浏览器环境中，将数据暴露到全局作用域
if (typeof window !== 'undefined') {
window.embeddedPersonalData = embeddedPersonalData;
window.personalData = personalData;
window.PersonalDataManager = PersonalDataManager;
}