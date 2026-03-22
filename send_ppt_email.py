#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
发送邮件 - 计生行业竞品调研 PPT
"""

import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path

# 配置信息
smtp_server = "smtp.qq.com"
smtp_port = 465
from_email = "kinsongho@qq.com"
to_email = "hejs@edaxiang.com"

# 从环境变量获取密码
password = os.environ.get("QQ_EMAIL_PASSWORD")

if not password:
    print("[Error] 未找到 QQ 邮箱授权码")
    print("请设置环境变量：QQ_EMAIL_PASSWORD")
    print("或者在 C:\\Users\\ho\\.openclaw\\.env 文件中配置")
    exit(1)

# 邮件内容
subject = "计生行业竞品调研报告 - 2026 年 3 月"
body = """
Nelson，你好！

这是你要的计生行业竞品调研 PPT 报告。

【报告内容】
1. 行业概况
2. 主要竞品品牌（杜蕾斯、杰士邦、冈本、大象、名流）
3. 市场份额分析
4. 产品线对比
5. 价格策略
6. 营销渠道
7. 社交媒体表现
8. 新品动态（2026）
9. 用户画像
10. 趋势与建议

【核心发现】
• 市场集中度提升，头部品牌优势明显
• 国产品牌快速崛起，技术创新是关键
• 线上渠道主导，即时零售增长快
• 营销创新活跃，内容质量决定传播效果

共 14 页幻灯片。

如有需要修改的地方，随时告诉我！

祝好，
虾饺 🥟
"""

# PPT 文件路径
ppt_path = Path(r"C:\Users\ho\.openclaw\workspace\sososong\计生行业竞品调研_20260318.pptx")

if not ppt_path.exists():
    print(f"[Error] PPT 文件不存在：{ppt_path}")
    exit(1)

# 创建邮件
msg = MIMEMultipart()
msg['From'] = from_email
msg['To'] = to_email
msg['Subject'] = subject

# 添加正文
msg.attach(MIMEText(body, 'plain', 'utf-8'))

# 添加附件
with open(ppt_path, "rb") as attachment:
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(attachment.read())

encoders.encode_base64(part)
part.add_header(
    'Content-Disposition',
    f'attachment; filename={ppt_path.name}'
)
msg.attach(part)

# 发送邮件
try:
    print(f"[Info] 正在发送邮件到 {to_email}...")
    
    with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
        server.login(from_email, password)
        server.send_message(msg)
    
    print(f"[OK] 邮件发送成功！")
    print(f"[From] {from_email}")
    print(f"[To] {to_email}")
    print(f"[Subject] {subject}")
    print(f"[Attachment] {ppt_path.name}")
    
except Exception as e:
    print(f"[Error] 邮件发送失败：{e}")
    import traceback
    traceback.print_exc()
