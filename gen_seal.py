"""生成火漆印 PNG（透明底）"""
import random
import math
from PIL import Image, ImageDraw, ImageFilter

SIZE = 400
CENTER = SIZE // 2
RADIUS = 150

img = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# ========== 1. 蜡底：不规则圆形 + 深红色 ==========
# 生成不规则半径（模拟蜡滴边缘）
seal_mask = Image.new('L', (SIZE, SIZE), 0)
mask_draw = ImageDraw.Draw(seal_mask)

points = []
for angle in range(360):
    rad = math.radians(angle)
    # 基础圆 + 多层随机波动（模拟蜡滴不规则边缘）
    r = RADIUS
    r += 12 * math.sin(angle * 3.7)      # 大波浪
    r += 6 * math.sin(angle * 7.3 + 1)   # 中波浪
    r += 4 * math.sin(angle * 13.1 + 2)  # 小波浪
    r += 3 * math.cos(angle * 5.9 + 0.5)
    x = CENTER + r * math.cos(rad)
    y = CENTER + r * math.sin(rad)
    points.append((x, y))

mask_draw.polygon(points, fill=255)

# 模糊边缘（蜡的柔软感）
seal_mask = seal_mask.filter(ImageFilter.GaussianBlur(3))

# ========== 2. 填充蜡色（多层渐变） ==========
# 基础深红
base = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 0))
base_draw = ImageDraw.Draw(base)

# 径向渐变模拟光照
for r in range(RADIUS + 30, 0, -1):
    ratio = r / (RADIUS + 30)
    # 从外到内：深红 → 亮红 → 稍浅
    red = int(120 + 80 * (1 - ratio))
    green = int(20 + 25 * (1 - ratio))
    blue = int(30 + 20 * (1 - ratio))
    alpha = 255
    base_draw.ellipse(
        [CENTER - r, CENTER - r, CENTER + r, CENTER + r],
        fill=(red, green, blue, alpha)
    )

# 应用蜡底遮罩
base.putalpha(seal_mask)

# ========== 3. 添加质感纹理（噪点） ==========
noise = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 0))
noise_draw = ImageDraw.Draw(noise)
random.seed(42)
for _ in range(3000):
    x = random.randint(0, SIZE - 1)
    y = random.randint(0, SIZE - 1)
    # 只在蜡区域内
    dx, dy = x - CENTER, y - CENTER
    if dx*dx + dy*dy < RADIUS*RADIUS:
        brightness = random.randint(-20, 20)
        a = random.randint(15, 40)
        noise_draw.point((x, y), fill=(brightness, brightness, brightness, a))

noise = noise.filter(ImageFilter.GaussianBlur(1))

# 合并
img = Image.alpha_composite(base, noise)

# ========== 4. 光泽高光（左上角） ==========
highlight = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 0))
hl_draw = ImageDraw.Draw(highlight)
# 椭圆高光
hl_cx, hl_cy = CENTER - 40, CENTER - 50
for r in range(60, 0, -1):
    alpha = int(35 * (1 - r / 60))
    hl_draw.ellipse(
        [hl_cx - r, hl_cy - r//2, hl_cx + r, hl_cy + r//2],
        fill=(255, 255, 255, alpha)
    )
highlight = highlight.filter(ImageFilter.GaussianBlur(5))
img = Image.alpha_composite(img, highlight)

# ========== 5. 爱心浮雕（中心） ==========
heart = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 0))
heart_draw = ImageDraw.Draw(heart)

# 爱心参数
heart_size = 45
heart_cx, heart_cy = CENTER, CENTER + 5

def draw_heart(draw, cx, cy, size, color, offset_x=0, offset_y=0):
    """绘制一个爱心"""
    cx += offset_x
    cy += offset_y
    points = []
    for t in range(0, 360):
        rad = math.radians(t)
        x = size * 16 * math.sin(rad)**3
        y = -size * (13 * math.cos(rad) - 5 * math.cos(2*rad) - 2 * math.cos(3*rad) - math.cos(4*rad))
        points.append((cx + x/16, cy + y/16))
    draw.polygon(points, fill=color)

# 爱心阴影（浮雕效果）
draw_heart(heart_draw, heart_cx, heart_cy, heart_size, (80, 10, 20, 120), offset_x=2, offset_y=2)
# 爱心主体
draw_heart(heart_draw, heart_cx, heart_cy, heart_size, (180, 50, 70, 200))
# 爱心高光
draw_heart(heart_draw, heart_cx, heart_cy, heart_size - 8, (220, 100, 120, 100), offset_x=-3, offset_y=-3)

heart = heart.filter(ImageFilter.GaussianBlur(1))
img = Image.alpha_composite(img, heart)

# ========== 6. 内圈装饰线 ==========
circle_overlay = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 0))
circle_draw = ImageDraw.Draw(circle_overlay)
# 外圈
circle_draw.ellipse(
    [CENTER - RADIUS + 25, CENTER - RADIUS + 25, CENTER + RADIUS - 25, CENTER + RADIUS - 25],
    outline=(200, 80, 100, 80), width=2
)
# 内圈
circle_draw.ellipse(
    [CENTER - RADIUS + 40, CENTER - RADIUS + 40, CENTER + RADIUS - 40, CENTER + RADIUS - 40],
    outline=(200, 80, 100, 50), width=1
)

img = Image.alpha_composite(img, circle_overlay)

# ========== 7. 最终阴影（立体感） ==========
shadow = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 0))
shadow_draw = ImageDraw.Draw(shadow)
shadow_draw.ellipse(
    [CENTER - RADIUS + 5, CENTER - RADIUS + 8, CENTER + RADIUS + 5, CENTER + RADIUS + 12],
    fill=(0, 0, 0, 60)
)
shadow = shadow.filter(ImageFilter.GaussianBlur(8))

# 阴影在后面
final = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 0))
final = Image.alpha_composite(final, shadow)
final = Image.alpha_composite(final, img)

# 重新应用圆形遮罩（去掉阴影超出部分）
final.putalpha(Image.composite(seal_mask, final.split()[3], seal_mask))

# 保存
final.save('/home/zhiqihuang/openclaw_workspace/projects/520-confession/seal.png', 'PNG')
print(f"Done! Size: {final.size}, Mode: {final.mode}")
