// embedded-data.js - 修改后的版本

const embeddedPersonalData = {
personal: {
  name: {
    english: "Yi Lu",
    chinese: "陆艺"
  },
  title: "PhD Student in Algebraic Geometry",
  current_position: "Capital Normal University & University of Liverpool",
  locations: ["Beijing, China", "Liverpool, United Kingdom"],
  profile_initials: "YL",
  // 保留一个主要email用于其他地方显示
  email: "yi.lu@cnu.edu.cn"
},
education: [
  {
    degree: "Joint PhD in Mathematics",
    institution: "Capital Normal University & University of Liverpool",
    period: "2023 - Present",
    department: "School of Mathematical Sciences",
    program: "Joint PhD Program",
    specialization: "Algebraic Geometry",
    location: "Beijing, China & Liverpool, UK",
    note: "Joint training program during PhD studies",
    supervisors: [
      {
        name: "Dr. Thomas Eckl",
        role: "Primary Supervisor",
        institution: "University of Liverpool"
      },
      {
        name: "Dr. Zhixian Zhu",
        role: "Co-supervisor",
        title: "Associate Research Fellow",
        institution: "Capital Normal University"
      }
    ]
  },
  {
    degree: "Master of Science in Mathematics",
    institution: "Capital Normal University",
    period: "2021 - 2023",
    specialization: "Pure Mathematics",
    location: "Beijing, China",
    note: "Consecutive Master's to PhD program",
    supervisor: {
      name: "Prof. Shun Tang",
      role: "Supervisor",
      institution: "Capital Normal University"
    }
  },
  {
    degree: "Bachelor of Science in Internet of Things Engineering",
    institution: "Hebei University of Technology",
    period: "2016 - 2020",
    major: "Internet of Things Engineering (IoT)",
    location: "Tianjin, China"
  }
],
research: {
  interests: [
    "Positivity in AG",
    "Newton-Okounkov body", 
    "Combinatorics",
    "Toric Degeneration",
    "Graph Theory",
    "Computation in AG",
    "AI",
    "Deep Learning"
  ],
  // 添加研究兴趣跳转链接
  interests_detail_link: "./research-interest-prompt/"
},
publications: {
  journal_articles: [
    {
      title: "-",
      authors: ["-"],
      journal: "-",
      year: "-",
      doi: "-"
    }
  ],
  conference_papers: [
    {
      title: "-",
      authors: ["-"],
      conference: "-", 
      location: "-",
      year: "-",
      pages: "-",
      publisher: "-"
    }
  ],
  preprints: [
    {
      title: "Syzygy of Thoughts: Improving LLM CoT with the Minimal Free Resolution",
      authors: ["Chenghao Li", "Chaoning Zhang", "<strong>Yi Lu</strong>", "Jiaquan Zhang", "Qigan Sun", "Xudong Wang", "Jiwei Wei", "Guoqing Wang", "Yang Yang", "Heng Tao Shen "],
      arxiv: "2504.09566",
      year: "2025"
    },
    {
      title: "Interpreting and Improving Attention From the Perspective of Large Kernel Convolution",
      authors: ["Chenghao Li", "Chaoning Zhang", "Boheng Zeng", "<strong>Yi Lu</strong>", "Pengbo Shi", "Qingzi Chen", "Jirui Liu", "Lingyun Zhu", "Yang Yang", "Heng Tao Shen"],
      arxiv: "2401.05738",
      year: "2024"
    }
  ],
  // 合并 notes 和 presentations 为 notes_and_presentations
  notes_and_presentations: [
    {
      title: "K-jet Ampleness, Newton-Okounkov Bodies, and Related Criteria",
      content: "Annual progress report of second year in Uol",
      type: "Notes",
      year: "2025",
      pdf_link: "./academic/notes/APR_Uol_Year2_report.pdf"
    },
    {
      title: "K-jet Ampleness, Newton-Okounkov Bodies, and Related Criteria",
      content: "Annual progress report of second year in Uol",
      type: "Presentation",
      year: "2025",
      pdf_link: "./academic/presentations/APR_Uol_Year2_presentation.pdf"
    },
    {
      title:"Jet ampleness and Newton-Okounkov bodies of divisors",
      content: "2024 PHD Academic Forum in CNU",
      type: "Presentation",
      year: "2024",
      pdf_link: "./academic/presentations/2024_Doctoral_Academic_Forum__CNU_.pdf"
    }
  ]
  },
projects: {
  sections: [
    {
    title: "📚 Academic Tools",
    items: [
      {
        name: "LaTeX Literature Management System",
        description: "A comprehensive LaTeX system for managing academic literature with automated sorting, tag-based filtering, and BibTeX conversion tools.",
        technologies: ["LaTeX", "Python", "Tkinter", "BibTeX"],
        year: "2024",
        status: "Completed",
        features: [
          "Automated BibTeX conversion",
          "Tag-based filtering",
          "Multiple display formats",
          "GUI conversion tool",
          "Batch processing capabilities"
        ],
        link: "./latex_literature_management_system", 
      }
    ]
    },

    {
      title: "🏆 Competition Projects",
      items: [
        {
          name: "Only3000 - DNA Storage Solution",
          description: "Error-correcting code implementation for DNA storage with Substitution + Insertion + Deletion capabilities. Developed refined Levenshtein function for code table optimization.",
          technologies: ["Python", "Bioinformatics", "Error-Correcting Codes", "Algorithm Optimization"],
          year: "2023",
          status: "Completed",
          result: "Won 3,000 RMB in 2023 Mammoth Cup International Contest on Omics Sciences",
          competition: "2023 Mammoth Cup: DNA Storage Track",
          team: ["Chenghao Li", "Yi Lu", "Yun Ma", "Xin Zhang"],
          link: "./Only3000" // 或者你的项目链接
        }
      ]
    },
    {
      title: "💻 Technical Projects",
      items: [
        {
          name: "BitArray - Efficient Bit Manipulation Library",
          description: "A comprehensive C++ library for bitwise operations on individual bits with compact representation. Supports multi-language implementation (C++/Python) with optimized algorithms for bit manipulation, shifting, and array operations.",
          technologies: ["C++", "Python", "Data Structures", "Bit Manipulation", "Algorithm Optimization"],
          year: "2024",
          status: "Completed",
          features: [
            "Efficient bitwise AND, OR operations",
            "Flexible bit indexing and slicing",
            "High and low bit shifting operations",
            "Memory-optimized storage",
            "Cross-language compatibility",
            "Comprehensive bit array utilities"
          ],
          link: "./bitarray/",
          documentation: "./bitarray/Readme.md"
        },
        {
          name: "cuArray - CUDA Multi-dimensional Array Manager",
          description: "A templated C++ class for managing multi-dimensional arrays on both CPU and GPU using CUDA. Provides efficient data transfer, flexible indexing, and memory management for scientific computing and machine learning applications.",
          technologies: ["C++", "CUDA", "GPU Computing", "Template Programming", "Memory Management"],
          year: "2024",
          status: "Active Development",
          features: [
            "Multi-dimensional array handling",
            "Host and device data management", 
            "Flexible indexing system",
            "Automatic memory management",
            "CUDA kernel integration"
          ],
          link: "./cuArray/", // 指向cuArray文件夹
          github: "https://github.com/你的用户名/cuArray" // 如果有GitHub链接
        }
      ]
    }
  ]
},
// 修改contact部分，支持多个email
contact: {
  // 修改email为数组格式，支持多个邮箱
  emails: [
    {
      type: "Primary",
      address: "2230501004@cnu.edu.cn",
      description: "Capital Normal University Email(Valid until 2027)"
    },
    {
      type: "Academic",
      address: "yi.lu@liverpool.ac.uk", 
      description: "University of Liverpool Email(Valid until 2027)"
    },
    {
      type: "Personal",
      address: "abc_20080610@126.com",
      description: "Personal Email"
    }
  ],
  addresses: {
    primary: {
      institution: "Capital Normal University",
      department: "School of Mathematical Sciences",
      address: "105 West Third Ring Road North, Haidian District",
      city: "Beijing",
      country: "China",
      postal_code: "100048"
    },
    visiting: {
      institution: "University of Liverpool", 
      department: "Department of Mathematical Sciences",
      address: "Mathematical Sciences Building, Peach Street",
      city: "Liverpool",
      country: "United Kingdom",
      postal_code: "L69 7ZL"
    }
  },
  academic_profiles: {
    // orcid: "https://orcid.org/0000-0000-0000-0000",
    // google_scholar: "https://scholar.google.com/citations?user=example",
    // researchgate: "https://www.researchgate.net/profile/Yi-Lu",
    // arxiv: "https://arxiv.org/search/?searchtype=author&query=Lu%2C+Y",
    // mathscinet: "https://mathscinet.ams.org/mathscinet/author?authorId=example",
    
  },
  social_media: {
    github: "https://github.com/ylu1997",
    // linkedin: "https://linkedin.com/in/yi-lu-math",
    // twitter: "https://twitter.com/yilu_math",
    // zhihu: "https://www.zhihu.com/people/yi-lu-math"
  }
}
};

// 数据访问类
class PersonalDataManager {
constructor() {
  this.data = embeddedPersonalData;
}

async loadData(jsonFile = null) {
  // 如果提供了JSON文件路径，尝试加载外部数据
  if (jsonFile) {
    try {
      const response = await fetch(jsonFile);
      if (response.ok) {
        const externalData = await response.json();
        this.data = { ...this.data, ...externalData };
        console.log('External data loaded successfully');
      }
    } catch (error) {
      console.warn('Could not load external data, using embedded data:', error);
    }
  }
  return this.data;
}

getPersonalInfo() {
  return this.data.personal || {};
}

getEducation() {
  return this.data.education || [];
}

getCurrentEducation() {
  return this.data.education?.filter(edu => 
    edu.period && edu.period.includes('Present')
  ) || [];
}

getResearchInfo() {
  return this.data.research || {};
}

getPublications() {
  return this.data.publications || {};
}

getProjects() {
  return this.data.projects || {};
}

getContactInfo() {
  return this.data.contact || {};
}

// 辅助方法：获取所有导师信息
getAllSupervisors() {
  const supervisors = [];
  this.data.education?.forEach(edu => {
    if (edu.supervisor) supervisors.push(edu.supervisor);
    if (edu.supervisors) supervisors.push(...edu.supervisors);
  });
  return supervisors;
}

// 辅助方法：获取当前导师
getCurrentSupervisors() {
  const currentEdu = this.getCurrentEducation();
  const supervisors = [];
  currentEdu.forEach(edu => {
    if (edu.supervisor) supervisors.push(edu.supervisor);
    if (edu.supervisors) supervisors.push(...edu.supervisors);
  });
  return supervisors;
}

// 辅助方法：按年份排序出版物
getPublicationsByYear() {
  const pubs = this.data.publications || {};
  const allPubs = [
    ...(pubs.journal_articles || []),
    ...(pubs.preprints || []),
    ...(pubs.presentations || [])
  ];
  return allPubs.sort((a, b) => (b.year || 0) - (a.year || 0));
}

// 辅助方法：获取最近的项目
getRecentProjects(limit = 5) {
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
}

// 创建全局实例
const personalData = new PersonalDataManager();

// 导出数据（如果在Node.js环境中）
if (typeof module !== 'undefined' && module.exports) {
module.exports = { embeddedPersonalData, PersonalDataManager };
}