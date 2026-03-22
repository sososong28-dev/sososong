#!/usr/bin/env python3
import sys, os
sys.stdout.reconfigure(encoding='utf-8')

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# 配置
smtp_server = "smtp.qq.com"
smtp_port = 465
from_email = "kinsongho@qq.com"
to_email = "hejs@edaxiang.com"
password = os.environ.get("QQ_EMAIL_PASSWORD")

subject = "PptxGenJS 测试 - 计生行业竞品调研 PPT"
body = """Nelson，你好！

这是使用 PptxGenJS（JavaScript）生成的 PPT 测试版本。

【技术栈】
- PptxGenJS v3.12.0
- Node.js v22.22.0
- 完全免费，无需 API Key

【PPT 信息】
- 文件名：竞品调研_PptxGenJS_20260318.pptx
- 页数：6 页（示例）
- 大小：156 KB
- 风格：专业商务风（深蓝色主题）

【内容目录】
1. 标题页
2. 目录
3. 行业概况
4. 主要竞品品牌（表格）
5. 市场份额（饼图）
6. 结束页

【对比之前版本】
- ✅ 支持更多图表类型
- ✅ 模板更丰富
- ✅ 代码更简洁
- ✅ 社区更活跃

请查收附件！

虾饺 🥟
"""

# 创建邮件
msg = MIMEMultipart()
msg['From'] = from_email
msg['To'] = to_email
msg['Subject'] = subject
msg.attach(MIMEText(body, 'plain', 'utf-8'))

# 添加附件
ppt_path = r"C:\Users\ho\.openclaw\workspace\sososong\竞品调研_PptxGenJS_20260318.pptx"
with open(ppt_path, "rb") as f:
    part = MIMEBase('application', 'vnd.openxmlformats-officedocument.presentationml.presentation')
    part.set_payload(f.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="竞品调研_PptxGenJS.pptx"')
    msg.attach(part)

# 发送
with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
    server.login(from_email, password)
    server.send_message(msg)

print(f"[OK] 邮件发送成功！")
print(f"[To] {to_email}")
print(f"[Subject] {subject}")
print(f"[Attachment] 竞品调研_PptxGenJS.pptx")
