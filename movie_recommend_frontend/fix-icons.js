const fs = require('fs');
const path = require('path');

// 要处理的目录
const srcDir = './src';

// 递归遍历目录
function processDirectory(dir) {
  const files = fs.readdirSync(dir);
  
  files.forEach(file => {
    const filePath = path.join(dir, file);
    const stat = fs.statSync(filePath);
    
    if (stat.isDirectory()) {
      processDirectory(filePath);
    } else if (file.endsWith('.vue') || file.endsWith('.js')) {
      processFile(filePath);
    }
  });
}

// 处理单个文件
function processFile(filePath) {
  let content = fs.readFileSync(filePath, 'utf8');
  
  // 删除从 @element-plus/icons-vue 导入的语句
  const importRegex = /import\s*{([^}]*)}\s*from\s*['"]@element-plus\/icons-vue['"];?/g;
  content = content.replace(importRegex, '');
  
  fs.writeFileSync(filePath, content, 'utf8');
  console.log(`Processed: ${filePath}`);
}

// 开始处理
processDirectory(srcDir);
console.log('All icon imports removed!');