---
type: cheatsheet
domain: forensics
tags: [vision, multimodal, ocr, qrcode, 图片]
source: 原创
date: 2026-09-27
---

# 视觉输入工作流（CC 多模态 + 镜像工具配合）

CC 的后端是多模态模型：**图片可以直接"看"**（宿主机侧 Read 任意 png/jpg）。
镜像是给"看不了/看不准"的场景准备的解码与转换工具。分工：

- **看内容**（图形逻辑、流程图、验证码、图案规律、二维码内容）→ CC 直接读图；
- **抠数据**（LSB、频谱、二维码原始字节、大图局部）→ 容器内工具，结果回文本。

## 图片搬运约定

容器只挂载 workspace：附件在容器里看不了时，从宿主机侧直接 Read
`workspace/<题>/attachments/xxx.png`；容器里生成的图（频谱图/修复后的二维码）
写进 workspace 目录，宿主机即可 Read。

## 转换命令速查（ctf-forensics 内置）

```bash
pdftoppm -png -r 150 file.pdf out        # PDF → PNG（视觉读 PDF 前先转图）
convert in.png -resize 400% out.png      # 放大低分辨率图/验证码
convert in.png -colorspace gray out.png  # 灰度化
zbarimg --raw qr.png                     # 二维码解码（直接出内容）
sox audio.wav -n spectrogram -o spec.png # 音频 → 频谱图（然后视觉看 flag）
python3 -c "import pytesseract; print(pytesseract.image_to_string('img.png', lang='chi_sim+eng'))"
```

## 二维码题套路

1. 扫不出 → 检查尺寸是否被改（PIL 打开看宽高，QR 应为正方形且版本对齐）、
   三个定位角是否缺损（用 PIL 补画）；
2. 白边太窄 → `convert -bordercolor white -border 20`；
3. 反色/残缺 → `convert -negate`；定位角补齐脚本让 CC 现写（PIL 三块 7x7 图案）；
4. 修复后 `zbarimg` 解码。

## 验证码/截图类

低分辨率验证码先放大 + 灰度化再让 CC 看，准确率显著提高；
有干扰线时先容器内做二值化（`convert -threshold 50%`）。

## 关联

- 示例：`examples/misc-qr-warmup`（QR 内容用视觉直读 + zbarimg 双通道验证）
- 音频隐写进阶：steghide（wav）、morphia? 不内置，现场 pip
