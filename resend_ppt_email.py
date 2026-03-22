#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重新发送邮件 - 计生行业竞品调研 PPT
确保附件正确
"""

import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# 配置信息
smtp_server = "smtp.qq.com"
smtp_port = 465
from_email = "kinsongho@qq.com"
to_email = "hejs@edaxiang.com"
password = os.environ.get("QQ_EMAIL_PASSWORD")

if not password:
    print("[Error] 未找到 QQ 邮箱授权码")
    exit(1)

# 邮件内容
subject = "【重发】计生行业竞品调研报告 - 2026 年 3 月（PPTX 格式）"
body = """Nelson，你好！

这是重新发送的计生行业竞品调研 PPT 报告。

【文件格式】PPTX（可编辑的 PowerPoint）
【文件大小】约 44KB
【页数】14 页

【报告目录】
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

请用 PowerPoint 2007+ 或 WPS Office 打开。

如有问题请告诉我！

虾饺 🥟
"""

# PPT 文件路径（使用绝对路径）
ppt_path = r"C:\Users\ho\.openclaw\workspace\sososong\计生行业竞品调研_20260318.pptx"

# 创建邮件
msg = MIMEMultipart()
msg['From'] = from_email
msg['To'] = to_email
msg['Subject'] = subject

# 添加正文
msg.attach(MIMEText(body, 'plain', 'utf-8'))

# 添加附件
try:
    with open(ppt_path, "rb") as f:
        attachment = f.read()
    
    part = MIMEBase('application', 'vnd.openxmlformats-officedocument.presentationml.presentation')
    part.set_payload(attachment)
    encoders.encode_base64(part)
    part.add_header(
        'Content-Disposition',
        'attachment; filename="family_planning_research_20260318.pptx"'
    )
    msg.attach(part)
    
    print(f"[OK] 邮件准备完成")
    print(f"[附件] {ppt_path}")
    print(f"[大小] {len(attachment)} 字节")
    
except Exception as e:
    print(f"[Error] 读取附件失败：{e}")
    import traceback
    traceback.print_exc()
    exit(1)

# 发送邮件
try:
    print(f"\n[Info] 正在发送...")
    
    with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
        server.login(from_email, password)
        server.send_message(msg)
    
    print(f"\n[OK] 发送成功！")
    print(f"[发件人] {from_email}")
    print(f"[收件人] {to_email}")
    print(f"[主题] {subject}")
    
except Exception as e:
    print(f"\n[Error] 发送失败：{e}")
    import traceback
    traceback.print_exc()
