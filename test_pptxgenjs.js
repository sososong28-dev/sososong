const pptx = require('pptxgenjs');

// 创建演示文稿
let pres = new pptx();

// 设置幻灯片尺寸（16:9）
pres.layout = 'LAYOUT_16x9';

// 配色方案
const COLORS = {
    primary: '1E3A8A',      // 深蓝
    secondary: '3B82F6',    // 亮蓝
    accent: 'EF4444',       // 红
    text: '1F2937',         // 深灰
    light: 'F3F4F6'         // 浅灰
};

// 1. 标题页
let slide1 = pres.addSlide();
slide1.background = { color: COLORS.primary };
slide1.addText('计生行业竞品调研报告', {
    x: 0.5, y: 2.5, w: 9, h: 1.5,
    fontSize: 48, bold: true, color: 'FFFFFF', align: 'center',
    fontFace: 'Microsoft YaHei'
});
slide1.addText('2026 年 3 月', {
    x: 0.5, y: 3.8, w: 9, h: 0.8,
    fontSize: 28, color: 'FFFFFF', align: 'center',
    fontFace: 'Microsoft YaHei'
});

// 2. 目录页
let slide2 = pres.addSlide();
slide2.addText('目录', {
    x: 0.5, y: 0.5, w: 9, h: 0.8,
    fontSize: 36, bold: true, color: COLORS.primary,
    fontFace: 'Microsoft YaHei'
});

const chapters = [
    '01 行业概况',
    '02 主要竞品品牌',
    '03 市场份额分析',
    '04 产品线对比',
    '05 价格策略',
    '06 营销渠道',
    '07 社交媒体表现',
    '08 新品动态',
    '09 用户画像',
    '10 趋势与建议'
];

chapters.forEach((chapter, i) => {
    let y = 1.5 + i * 0.55;
    slide2.addText(chapter.substring(0, 2), {
        x: 0.5, y: y, w: 0.8, h: 0.5,
        fontSize: 20, bold: true, color: COLORS.primary,
        fontFace: 'Arial'
    });
    slide2.addText(chapter.substring(3), {
        x: 1.2, y: y, w: 8, h: 0.5,
        fontSize: 18, color: COLORS.text,
        fontFace: 'Microsoft YaHei'
    });
});

// 3. 行业概况
let slide3 = pres.addSlide();
slide3.addText('1. 行业概况', {
    x: 0.5, y: 0.5, w: 9, h: 0.8,
    fontSize: 36, bold: true, color: COLORS.primary,
    fontFace: 'Microsoft YaHei'
});
slide3.addShape(pres.ShapeType.rect, {
    x: 0.5, y: 1.2, w: 3, h: 0.15, fill: COLORS.secondary
});

const industryPoints = [
    '市场规模：2025 年约 150 亿元',
    '年增长率：8-10%',
    '线上占比：65%+',
    '品牌集中度高（CR5 > 60%）',
    '营销创新活跃',
    '产品差异化明显'
];

industryPoints.forEach((point, i) => {
    let y = 1.6 + i * 0.6;
    slide3.addText('•', {
        x: 0.6, y: y, w: 0.3, h: 0.5,
        fontSize: 24, color: COLORS.secondary
    });
    slide3.addText(point, {
        x: 0.9, y: y, w: 10, h: 0.5,
        fontSize: 18, color: COLORS.text,
        fontFace: 'Microsoft YaHei'
    });
});

// 4. 品牌对比表格
let slide4 = pres.addSlide();
slide4.addText('2. 主要竞品品牌', {
    x: 0.5, y: 0.5, w: 9, h: 0.8,
    fontSize: 36, bold: true, color: COLORS.primary,
    fontFace: 'Microsoft YaHei'
});

let tableData = [
    [{ text: '品牌', options: { fill: COLORS.primary, color: 'FFFFFF', bold: true, fontSize: 16 } },
     { text: '产地', options: { fill: COLORS.primary, color: 'FFFFFF', bold: true, fontSize: 16 } },
     { text: '定位', options: { fill: COLORS.primary, color: 'FFFFFF', bold: true, fontSize: 16 } },
     { text: '价格带', options: { fill: COLORS.primary, color: 'FFFFFF', bold: true, fontSize: 16 } }],
    
    ['杜蕾斯', '英国', '高端', '¥¥¥'],
    ['杰士邦', '澳洲', '中高端', '¥¥'],
    ['冈本', '日本', '超薄高端', '¥¥¥'],
    ['大象', '中国', '年轻科技', '¥¥'],
    ['名流', '中国', '性价比', '¥']
];

slide4.addTable(tableData, {
    x: 0.5, y: 1.5, w: 12, h: 4,
    fontSize: 14,
    fontFace: 'Microsoft YaHei',
    fill: 'FFFFFF',
    color: COLORS.text,
    border: { pt: 1, color: 'CCCCCC' }
});

// 5. 市场份额（饼图）
let slide5 = pres.addSlide();
slide5.addText('3. 市场份额分析（线上 2025）', {
    x: 0.5, y: 0.5, w: 9, h: 0.8,
    fontSize: 32, bold: true, color: COLORS.primary,
    fontFace: 'Microsoft YaHei'
});

slide5.addChart(pres.ChartType.PIE, [
    { labels: ['杜蕾斯', '杰士邦', '冈本', '大象', '其他'], values: [28, 18, 12, 8, 34] }
], {
    x: 0.5, y: 1.5, w: 6, h: 5,
    showLegend: true,
    legendPos: 'right',
    colors: [COLORS.primary, '2563EB', '60A5FA', '93C5FD', '9CA3AF']
});

// 6. 结束页
let slide6 = pres.addSlide();
slide6.background = { color: COLORS.primary };
slide6.addText('谢谢', {
    x: 0.5, y: 2.5, w: 9, h: 2,
    fontSize: 64, bold: true, color: 'FFFFFF', align: 'center',
    fontFace: 'Microsoft YaHei'
});
slide6.addText('Q & A', {
    x: 0.5, y: 4.2, w: 9, h: 1,
    fontSize: 32, color: 'FFFFFF', align: 'center',
    fontFace: 'Arial'
});

// 保存文件
pres.writeFile({
    fileName: '竞品调研_PptxGenJS_20260318.pptx',
    outputType: 'nodejs'
}).then(() => {
    console.log('✅ PPT 生成成功！');
    console.log('📁 文件：竞品调研_PptxGenJS_20260318.pptx');
    console.log('📊 页数：6 页（示例）');
}).catch(err => {
    console.error('❌ 生成失败:', err);
});
