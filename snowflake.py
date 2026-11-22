# Spinning 3D snowflake in your terminal.
#   python3 snowflake.py                 # "let it snow ❄"
#   python3 snowflake.py --to "Alex"     # "Merry Christmas, Alex ❄"
# Press Ctrl+C to stop. Zoom the terminal out (Cmd/Ctrl + minus) for a sharper snowflake.
import math
import os
import random
import shutil
import sys
import time

FPS = 30
SPIN_SPEED = 0.9      # how fast it spins around
TWIST_SPEED = 0.25    # how fast it turns in its own plane
TILT = 0.25
CAM_DIST = 4.0
MESSAGE = "let it snow ❄"
if "--to" in sys.argv:
    i = sys.argv.index("--to")
    if i + 1 < len(sys.argv):
        MESSAGE = f"Merry Christmas, {sys.argv[i + 1][:30]} ❄"

ICE = [240, 243, 246, 248, 250, 251, 252, 253, 254, 255, 231]   # soft grey -> bright white
PINK_ICE = [152, 153, 159, 189, 195, 195, 231]  # pale icy blue (centre gem)
# Arms fade from white into soft icy blue toward the tips: (start radius, palette dark -> bright)
TIP_FADE = [
    (0.62, [248, 251, 253, 255, 231, 195, 231]),
    (0.74, [152, 189, 195, 195, 231, 195]),
    (0.86, [110, 153, 189, 159, 195, 195]),
    (0.96, [110, 152, 153, 159, 159, 195]),
]
SHADE = ".:-=+*#%@"
SNOW_COLORS = [153, 189, 195, 231, 255]
MSG_COLORS = [33, 39, 45, 81, 117, 153, 195, 231, 195, 153, 117, 81, 45, 39]
RESET = "\033[0m"

_L = (-0.4, 0.55, 0.75)
_n = math.sqrt(sum(v * v for v in _L))
LX, LY, LZ = (v / _n for v in _L)


def build():
    """The snowflake is a flat crystal with a little thickness. Each point has a
    normal so it catches the light; edges are bevelled so it looks 3D while it spins."""
    pts = []
    TH = 0.025  # half thickness

    def slab(p0, p1, w0, w1, pal, step=0.008):
        dx, dy = p1[0] - p0[0], p1[1] - p0[1]
        L = math.hypot(dx, dy)
        ux, uy = dx / L, dy / L
        px, py = -uy, ux
        n = max(2, int(L / step))
        for i in range(n + 1):
            t = i / n
            w = w0 + (w1 - w0) * t
            cx, cy = p0[0] + dx * t, p0[1] + dy * t
            m = max(1, int(w / 0.006))
            for j in range(-m, m + 1):
                s = j / m                      # -1 .. 1 across the arm
                bevel = s * 0.8                # tilt normals at the edges
                nx, ny, nz = px * bevel, py * bevel, 1.0
                l = math.sqrt(nx * nx + ny * ny + nz * nz)
                x, y = cx + px * w * s, cy + py * w * s
                ridge = 0.25 * (1 - abs(s)) ** 2   # bright ridge down the middle
                for side in (1, -1):
                    pts.append((x, y, side * TH * (1 - abs(s) * 0.6), nx / l, ny / l, side * nz / l,
                                pal, ridge, t))

    for k in range(6):
        a = k * math.pi / 3
        ca, sa = math.cos(a), math.sin(a)
        rot = lambda x, y: (x * ca - y * sa, x * sa + y * ca)
        slab(rot(0, 0.10), rot(0, 1.0), 0.05, 0.022, ICE)               # main arm
        for pos, ln, w in ((0.32, 0.30, 0.03), (0.58, 0.27, 0.026), (0.80, 0.15, 0.02)):
            for side in (-1, 1):
                end = (side * ln * math.sin(math.pi / 3), pos + ln * math.cos(math.pi / 3))
                slab(rot(0, pos), rot(*end), w, w * 0.45, PINK_ICE if pos > 0.7 else ICE)
        # little diamond at the tip
        slab(rot(0, 0.96), rot(0, 1.08), 0.045, 0.0, PINK_ICE)
        # inner hexagon edge
        b = (k + 1) * math.pi / 3
        p0 = (0.16 * -math.sin(a), 0.16 * math.cos(a))
        p1 = (0.16 * -math.sin(b), 0.16 * math.cos(b))
        slab(p0, p1, 0.02, 0.02, ICE)
    # centre gem
    for r in range(1, 12):
        rr = r / 11 * 0.1
        for j in range(int(rr * 300) + 6):
            ph = j / (int(rr * 300) + 6) * 2 * math.pi
            for side in (1, -1):
                pts.append((rr * math.cos(ph), rr * math.sin(ph), side * 0.03 * (1 - rr / 0.1),
                            math.cos(ph) * rr * 4, math.sin(ph) * rr * 4, side, PINK_ICE, 0.15, 0.0))
    return pts


def render(pts, t, cols, rows, snow, sparkles):
    view_rows = rows - 2
    chars = [[" "] * cols for _ in range(rows)]
    colors = [[0] * cols for _ in range(rows)]
    zbuf = [[-1e9] * cols for _ in range(rows)]
    scale = max(1.0, min((view_rows - 2) / 2.35, (cols - 2) / 4.7))
    cx, cy = cols / 2, view_rows / 2

    spin, twist = t * SPIN_SPEED, t * TWIST_SPEED
    cs, ss = math.cos(spin), math.sin(spin)
    cw, sw = math.cos(twist), math.sin(twist)
    ct, st = math.cos(TILT), math.sin(TILT)

    def xf(x, y, z):
        x, y = x * cw - y * sw, x * sw + y * cw      # turn in its own plane
        x, z = x * cs + z * ss, -x * ss + z * cs      # spin around the vertical axis
        y, z = y * ct - z * st, y * st + z * ct       # look down a little
        return x, y, z

    def plot(c, r, z, ch, color):
        if 0 <= r < view_rows and 0 <= c < cols and z > zbuf[r][c]:
            zbuf[r][c] = z
            chars[r][c] = ch
            colors[r][c] = color

    for s in snow:
        c = int((s[0] + 0.02 * math.sin(t + s[3])) * cols) % cols
        plot(c, int(s[1] * view_rows), -50, s[5], s[4])

    glint = (t * 0.6) % 1.4   # a shine that runs along the arms
    for x, y, z, nx, ny, nz, pal, tone, along in pts:
        rad = math.hypot(x, y)
        for start, fade in TIP_FADE:
            if rad >= start:
                pal = fade
        X, Y, Z = xf(x, y, z)
        NX, NY, NZ = xf(nx, ny, nz)
        dot = NX * LX + NY * LY + NZ * LZ
        if dot < 0:
            dot = -dot * 0.6       # two-sided, the back is a bit dimmer
        shine = 0.35 if abs(along - glint) < 0.06 else 0.0
        b = min(0.999, max(0.0, 0.1 + 0.7 * dot + tone + shine))
        f = CAM_DIST / (CAM_DIST - Z)
        plot(int(cx + X * f * scale * 2), int(cy - Y * f * scale), Z,
             SHADE[int(b * len(SHADE))], pal[int(b * len(pal))])

    for x, y, z, ph, sp in sparkles:
        X, Y, Z = xf(x, y, z)
        f = CAM_DIST / (CAM_DIST - Z)
        tw = math.sin(t * sp + ph)
        ch = "*" if tw > 0.85 else "+" if tw > 0.5 else "·" if tw > 0.2 else None
        if ch:
            plot(int(cx + X * f * scale * 2), int(cy - Y * f * scale), Z + 0.1, ch, 231)

    mrow = rows - 2
    start = max(0, (cols - len(MESSAGE)) // 2)
    shift = int(t * 6)
    for i, ch in enumerate(MESSAGE):
        if start + i < cols:
            chars[mrow][start + i] = ch
            colors[mrow][start + i] = MSG_COLORS[(i + shift) % len(MSG_COLORS)]

    out = []
    for r in range(rows):
        last, parts = -1, []
        for c in range(cols):
            ch = chars[r][c]
            if ch != " " and colors[r][c] != last:
                last = colors[r][c]
                parts.append(f"\033[38;5;{last}m")
            parts.append(ch)
        out.append("".join(parts))
    return "\033[H" + "\n".join(out) + RESET


def main():
    if os.name == "nt":
        os.system("")
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    pts = build()
    rnd = random.Random(3)
    sparkles = []
    for _ in range(40):
        a, r = rnd.random() * 6.28, rnd.uniform(0.2, 1.1)
        sparkles.append((r * math.cos(a), r * math.sin(a), rnd.uniform(-0.05, 0.05),
                         rnd.uniform(0, 6.28), rnd.uniform(1.5, 4.0)))
    snow = []
    sys.stdout.write("\033[?25l\033[2J")
    start = last = time.perf_counter()
    last_size = None
    try:
        while True:
            now = time.perf_counter()
            dt, last = now - last, now
            size = shutil.get_terminal_size((80, 30))
            cols, rows = max(20, size.columns - 1), max(12, size.lines - 1)
            if (cols, rows) != last_size:
                sys.stdout.write("\033[2J")
                last_size = (cols, rows)
            while len(snow) < 30:
                snow.append([random.random(), random.random() * -0.3, random.uniform(0.04, 0.1),
                             random.uniform(0, 6.28), random.choice(SNOW_COLORS), random.choice("❄*··")])
            for s in snow:
                s[1] += s[2] * dt
                if s[1] > 1:
                    s[0], s[1] = random.random(), 0.0
            sys.stdout.write(render(pts, now - start, cols, rows, snow, sparkles))
            sys.stdout.flush()
            wait = 1 / FPS - (time.perf_counter() - now)
            if wait > 0:
                time.sleep(wait)
    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write(RESET + "\033[?25h\033[2J\033[H")
        print("\033[38;5;195m❄\033[0m")


if __name__ == "__main__":
    main()
