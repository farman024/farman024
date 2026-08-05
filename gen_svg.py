import numpy as np
import sys
import hashlib

BASE = r"C:\Users\Farman\AppData\Local\Temp\opencode\ghbanner"

# ============ CONFIG ============
W, H = 1180, 610
FRAME_X, FRAME_Y, FRAME_W, FRAME_H = 50, 60, 420, 490   # portrait panel
GRID_W, GRID_H = 300, 340                                # portrait grid
SCALE = min(FRAME_W / GRID_W, FRAME_H / GRID_H)         # scale to fit
OX = FRAME_X + (FRAME_W - GRID_W * SCALE) / 2
OY = FRAME_Y + (FRAME_H - GRID_H * SCALE) / 2

PALETTE_DARK = {
    "bg": "#06090F",
    "panel": "#0A101F",
    "panel_stroke": "#22D3EE",
    "portrait": "#E79047",
    "chrome": "#F0B429",
    "chrome_dim": "#94A3B8",
    "accent": "#FFC94D",
    "live": "#FF3B30",
}
PALETTE_LIGHT = {
    "bg": "#F8FAFC",
    "panel": "#FFFFFF",
    "panel_stroke": "#0891B2",
    "portrait": "#B45309",
    "chrome": "#A16207",
    "chrome_dim": "#64748B",
    "accent": "#D97706",
    "live": "#EF4444",
}

def load_dots(name):
    return np.load(f"{BASE}\\{name}")

def norm(dots, box_w, box_h, pad=0.02):
    """Normalize dots (x,y raw) into box_w x box_h with padding, centered."""
    if len(dots) == 0:
        return []
    arr = np.array(dots, dtype=float)
    x, y = arr[:, 0], arr[:, 1]
    x0, x1, y0, y1 = x.min(), x.max(), y.min(), y.max()
    cw, ch = max(x1 - x0, 1), max(y1 - y0, 1)
    # fit inside padded box preserving aspect
    avail_w = box_w * (1 - 2 * pad)
    avail_h = box_h * (1 - 2 * pad)
    s = min(avail_w / cw, avail_h / ch)
    nx = (x - x0) * s + (box_w - cw * s) / 2
    ny = (y - y0) * s + (box_h - ch * s) / 2
    return list(zip(nx.tolist(), ny.tolist()))

def drift_bands(dots, n_bands=94, noise_sigma=4.0, rng=None):
    """Group portrait dots into drift bands. Add per-dot noise before grouping."""
    rng = rng or np.random.default_rng(0)
    arr = np.array(dots, dtype=float)
    n = len(arr)
    noise = rng.normal(0, noise_sigma, (n, 2))
    j = arr + noise
    # assign to bands by x-position stripes (position-proportional)
    order = np.argsort(j[:, 0])
    bands = np.array_split(order, n_bands)
    return bands

def path_of(dots, scale=1.0):
    """Build one <path> 'd' string of M x y h0.001 lines."""
    d = []
    for x, y in dots:
        d.append(f"M{x:.1f} {y:.1f} h0.001")
    return " ".join(d)

def keyframe_animation(dots, periods, keyTimes, durations, total_loop):
    """Per-dot SMIL animate values across morph targets."""
    pass  # handled in traveler layer differently

def escape(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def norm_centered(dots, w, h):
    """Normalize dots into w x h box centered on origin."""
    pts = norm(dots, w, h)
    return [(x - w / 2, y - h / 2) for x, y in pts]


def resample(L, n):
    idx = np.linspace(0, len(L) - 1, n).astype(int)
    return np.array(L)[idx]


def build_badge_row(p, logos_dots, n_pts=180):
    """Three cube-disperse badges below the info panel.

    Each badge cycles through all 3 logos: particles burst outward, tumble,
    and reform (mirrors the three.js InstancedMesh disperse effect via SMIL).
    Base positions per badge differ (logo b) so a static render shows all 3.
    """
    rng = np.random.default_rng(11)
    slot_w, slot_h, gap = 200, 46, 30
    x0 = FRAME_X + FRAME_W + 45
    y0 = FRAME_Y + FRAME_H + 6
    # normalize each logo into a centered slot-sized box
    normed = [np.array(norm_centered(L, slot_w, slot_h)) for L in logos_dots]

    # keyframes (11): fb hold -> burst -> ang -> burst -> her -> burst -> fb
    kt = [0.000, 0.180, 0.220, 0.260, 0.420, 0.460, 0.500, 0.660, 0.700, 0.740, 1.000]
    kt_str = ";".join(f"{k:.3f}" for k in kt)
    splines = ";".join(["0.4 0 0.6 1"] * (len(kt) - 1))
    rot_vals = "0;0;150;0;0;150;0;0;150;0;0"
    BURST = 6.0

    parts = []
    for b in range(3):
        rot = [normed[(b + k) % 3] for k in range(3)]  # starts at logo b
        R = [resample(L, n_pts) for L in rot]
        theta = rng.uniform(0, np.pi * 2, n_pts)
        bx = np.cos(theta) * BURST
        by = np.sin(theta) * BURST
        ox = x0 + b * (slot_w + gap) + slot_w / 2
        oy = y0 + slot_h / 2
        for i in range(n_pts):
            r0, r1, r2 = R[0][i], R[1][i], R[2][i]
            px = [r0[0], r0[0], r0[0] + bx[i], r1[0], r1[0], r1[0] + bx[i],
                  r2[0], r2[0], r2[0] + bx[i], r0[0], r0[0]]
            py = [r0[1], r0[1], r0[1] + by[i], r1[1], r1[1], r1[1] + by[i],
                  r2[1], r2[1], r2[1] + by[i], r0[1], r0[1]]
            xv = ";".join(f"{x + ox:.1f} {y + oy:.1f}" for x, y in zip(px, py))
            parts.append(
                f'<g><animateTransform attributeName="transform" type="translate" '
                f'values="{xv}" keyTimes="{kt_str}" dur="14s" begin="3s" '
                f'repeatCount="indefinite" calcMode="spline" keySplines="{splines}"/>'
                f'<rect x="-2" y="-2" width="4" height="4" class="cube">'
                f'<animateTransform attributeName="transform" type="rotate" '
                f'values="{rot_vals}" keyTimes="{kt_str}" dur="14s" begin="3s" '
                f'repeatCount="indefinite" calcMode="spline" keySplines="{splines}"/>'
                f'</rect></g>'
            )
    return "\n".join(parts)

# ============ INFO PANEL ============
INFO_ROWS = [
    ("SUBJECT", "Farman J."),
    ("ROLE", "AI Generalist"),
    ("ORIGIN", "India"),
    ("EDUCATION", "BCA"),
    ("STATUS", "Building+Shipping"),
    ("TOOLCHAIN", "VS Code · Git · Python"),
    ("CORE.LANG", "Python · JS"),
    ("CORE.FRONTEND", "HTML · CSS · PWA"),
    ("CORE.BACKEND", "FastAPI"),
    ("CORE.DATABASE", "Supabase"),
    ("CORE.INFRA", "Vercel · Railway"),
    ("GRID.MAIL", "farman@mail"),
    ("GRID.PORTFOLIO", "farman.dev"),
    ("GRID.LINKEDIN", "/in/farman"),
    ("GRID.GITHUB", "farman024"),
]

def build_info_svg(p):
    """Right-side SYSTEM.INFO readout. Two columns, labels + dotted leaders + right-aligned values."""
    out = []
    # col geometry
    col1_x, col2_x = FRAME_X + FRAME_W + 45, FRAME_X + FRAME_W + 380
    col_w = 340
    label_x = 0     # offset within column
    value_x = 255   # value right-aligned in column
    row_h = 30
    # vertically center the columns relative to the panel
    col_height = 8 * row_h
    y_start = FRAME_Y + (FRAME_H - col_height) // 2
    rows = INFO_ROWS
    col1, col2 = rows[:8], rows[8:]
    y = y_start
    for label, value in col1:
        lx = col1_x
        vx = col1_x + value_x
        out.append(f'<text x="{lx}" y="{y:.0f}" class="lbl" textLength="{int(len(label)*7.2)}" lengthAdjust="spacingAndGlyphs">{escape(label)}</text>')
        out.append(f'<text x="{vx}" y="{y:.0f}" class="val" textLength="{int(len(value)*7.2)}" lengthAdjust="spacingAndGlyphs" text-anchor="end">{escape(value)}</text>')
        out.append(f'<line x1="{lx+int(len(label)*7.2)+8}" y1="{y-4:.0f}" x2="{vx-10}" y2="{y-4:.0f}" class="leader"/>')
        y += row_h
    y2 = y_start
    for label, value in col2:
        lx = col2_x
        vx = col2_x + value_x
        out.append(f'<text x="{lx}" y="{y2:.0f}" class="lbl" textLength="{int(len(label)*7.2)}" lengthAdjust="spacingAndGlyphs">{escape(label)}</text>')
        out.append(f'<text x="{vx}" y="{y2:.0f}" class="val" textLength="{int(len(value)*7.2)}" lengthAdjust="spacingAndGlyphs" text-anchor="end">{escape(value)}</text>')
        out.append(f'<line x1="{lx+int(len(label)*7.2)+8}" y1="{y2-4:.0f}" x2="{vx-10}" y2="{y2-4:.0f}" class="leader"/>')
        y2 += row_h
    return "\n".join(out)

# ============ BUILD ============
def densify(dots, step=1.4, radius=3.0):
    """Rasterize sparse logo dots into a dense grid point cloud matching the
    portrait's visual density (step ~ photo dot pitch, radius ~ stroke width).

    For each logo dot, mark all grid cells within radius; return occupied
    cell centers. This fills gaps so logos have the same no-gap consistency
    as the photo.
    """
    arr = np.array(dots, dtype=float)
    if len(arr) == 0:
        return []
    x0, y0 = arr[:, 0].min(), arr[:, 1].min()
    x1, y1 = arr[:, 0].max(), arr[:, 1].max()
    # pad the box a bit so strokes near edges keep full width
    gx = np.arange(x0 - radius, x1 + radius + step, step)
    gy = np.arange(y0 - radius, y1 + radius + step, step)
    # indices of the grid cell each logo dot covers, with all neighbors in radius
    r = int(radius / step) + 1
    cx = np.floor((arr[:, 0] - (gx[0] - step / 2)) / step).astype(int)
    cy = np.floor((arr[:, 1] - (gy[0] - step / 2)) / step).astype(int)
    occ = set()
    for i in range(len(arr)):
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                occ.add((cy[i] + dy, cx[i] + dx))
    occ = {(yy, xx) for yy, xx in occ if 0 <= yy < len(gy) and 0 <= xx < len(gx)}
    pts = [(gx[xx], gy[yy]) for yy, xx in occ]
    return pts


def build_band_traveler_layer(p, portrait_pts, logos_pts, n_bands=94, n_trav=6000, burst=45):
    """Single continuous dot field (cube-disperse logic).

    ONE set of dots (uniform lattice base = portrait) morphs directly through
    fb -> </> -> agent -> back to the portrait. Every dot is always visible —
    no separate photo-band layer, no opacity crossfade — so each transition is
    a genuine continuous morph in the same visual language, exactly like the
    cube animation. 14-keyframe 24s cycle, consistent 3s holds + 1.5s radial
    bloom + 1.5s fly-in.
    """
    rng = np.random.default_rng(7)
    logo_pts = [np.array(L) for L in logos_pts]
    PD = np.array(portrait_pts, dtype=float)

    # ---- uniform lattice grid (cube-disperse style: even occupancy cells) ----
    spacing = 2.0
    half = spacing / 2
    gx = np.arange(FRAME_X + half, FRAME_X + FRAME_W, spacing)
    gy = np.arange(FRAME_Y + half, FRAME_Y + FRAME_H, spacing)
    cx = np.floor((PD[:, 0] - FRAME_X) / spacing).astype(int)
    cy = np.floor((PD[:, 1] - FRAME_Y) / spacing).astype(int)
    ncols = len(gx)
    occ = { (r, c) for r, c in zip(cy.tolist(), cx.tolist()) if 0 <= r < len(gy) and 0 <= c < ncols }
    idxs = sorted(occ)
    P = np.stack([[gx[c] for r, c in idxs], [gy[r] for r, c in idxs]], axis=1)

    # ---- density weighting: face features (eyes/nose/mouth) keep more dots ----
    # Count source portrait dots per coarse cell; dense feature regions get a
    # higher sampling weight so the 6000-dot budget concentrates where detail
    # matters instead of spreading evenly by angular rank.
    cs = 8.0
    ncr = int(np.ceil(FRAME_H / cs))
    ncc = int(np.ceil(FRAME_W / cs))
    dens = np.zeros((ncr, ncc), dtype=int)
    ccx = np.floor((PD[:, 0] - FRAME_X) / cs).astype(int)
    ccy = np.floor((PD[:, 1] - FRAME_Y) / cs).astype(int)
    for r, c in zip(ccy.tolist(), ccx.tolist()):
        if 0 <= r < ncr and 0 <= c < ncc:
            dens[r, c] += 1
    lcx = np.floor((P[:, 0] - FRAME_X) / cs).astype(int)
    lcy = np.floor((P[:, 1] - FRAME_Y) / cs).astype(int)
    w = np.array([dens[min(r, ncr - 1), min(c, ncc - 1)] for r, c in zip(lcy.tolist(), lcx.tolist())], dtype=float)
    w = np.sqrt(w + 1)  # moderate so sparse regions still get some dots

    # 14 keyframes: P hold | burst | fb | hold | burst | ang | hold | burst | agent | hold | burst | P | hold
    # Consistent cadence: every logo holds 3s, every switch burst-out + fly-in
    # 1.5s+1.5s. Full cycle = 24s (P holds split across the loop boundary).
    kt = [0.000, 0.0625, 0.125, 0.1875, 0.3125, 0.375, 0.4375,
          0.5625, 0.625, 0.6875, 0.8125, 0.875, 0.9375, 1.000]
    kt_str = ";".join(f"{k:.4f}" for k in kt)
    # smooth symmetric ease-in-out all the way through
    splines = ";".join(["0.4 0 0.6 1"] * (len(kt) - 1))

    def order_angular(d):
        """Sort a dot cloud by angle around its centroid so dot i keeps the
        same angular rank in every formation -> morphs read as smooth radial
        flow instead of dots flying to arbitrary scanline spots."""
        d = np.array(d, dtype=float)
        if len(d) == 0:
            return d
        cx, cy = d[:, 0].mean(), d[:, 1].mean()
        ang = np.arctan2(d[:, 1] - cy, d[:, 0] - cx)
        return d[np.argsort(ang)]

    def resample_sort(L, n):
        d = order_angular(L)
        if len(d) == 0:
            return d
        idx = np.linspace(0, len(d) - 1, n).astype(int)
        return d[idx]

    # Portrait lattice angular-ordered too, so dot i keeps the same angular
    # rank in every formation -> smooth radial flow everywhere. Weighted by
    # source density (importance sampling): take n evenly spaced points in
    # cumulative-weight space, so feature-dense areas keep more dots while
    # preserving angular order (no crossing dots during morph).
    def resample_sort_weighted(L, n, weights=None):
        d = order_angular(L)
        if len(d) == 0:
            return d
        if weights is None:
            idx = np.linspace(0, len(d) - 1, n).astype(int)
            return d[idx]
        w = np.array(weights, dtype=float)
        w = w / w.sum()
        cw = np.cumsum(w)
        cw = cw / cw[-1]
        target = np.linspace(cw[0] * 0.5, 1 - cw[0] * 0.5, n)
        idx = np.searchsorted(cw, target)
        idx = np.clip(idx, 0, len(d) - 1)
        return d[idx]

    T = resample_sort_weighted(P, n_trav, weights=w)

    F = resample_sort(logo_pts[0], n_trav)   # FARMANS.BRAND (candlestick mask)
    A = resample_sort(logo_pts[1], n_trav)   # </> (single-stroke mask)
    H = resample_sort(logo_pts[2], n_trav)   # AI Agent (SVG gold mask)

    def radial_burst(pts, rng, burst):
        """Clean outward explosion: each dot flies away from the formation's
        centroid, so bursts read as a bloom instead of random dust."""
        pts = np.array(pts, dtype=float)
        c = pts.mean(axis=0)
        v = pts - c
        n = np.hypot(v[:, 0], v[:, 1])
        n[n == 0] = 1
        return (v / n[:, None]) * burst

    b0 = radial_burst(T, rng, burst)   # scatter out of portrait
    b1 = radial_burst(F, rng, burst)   # scatter out of fb
    b2 = radial_burst(A, rng, burst)   # scatter out of </>
    b3 = radial_burst(H, rng, burst)   # scatter out of agent

    trav_parts = []
    for i in range(n_trav):
        t0 = T[i]; f = F[i]; a = A[i]; h = H[i]
        xs = [t0[0], t0[0], t0[0]+b0[i,0], f[0], f[0], f[0]+b1[i,0],
              a[0], a[0], a[0]+b2[i,0], h[0], h[0], h[0]+b3[i,0], t0[0], t0[0]]
        ys = [t0[1], t0[1], t0[1]+b0[i,1], f[1], f[1], f[1]+b1[i,1],
              a[1], a[1], a[1]+b2[i,1], h[1], h[1], h[1]+b3[i,1], t0[1], t0[1]]
        xv = ";".join(f"{x:.1f}" for x in xs)
        yv = ";".join(f"{y:.1f}" for y in ys)
        trav_parts.append(
            f'<g class="trav">'
            f'<circle cx="{t0[0]:.1f}" cy="{t0[1]:.1f}" r="0.7">'
            f'<animate attributeName="cx" values="{xv}" keyTimes="{kt_str}" dur="24s" begin="3s" repeatCount="indefinite" calcMode="spline" keySplines="{splines}"/>'
            f'<animate attributeName="cy" values="{yv}" keyTimes="{kt_str}" dur="24s" begin="3s" repeatCount="indefinite" calcMode="spline" keySplines="{splines}"/>'
            f'</circle></g>'
        )

    return "\n".join(trav_parts)


def build_cube_layer(p, portrait_pts, logos_pts, n_pts=6000, cube=1.8, burst=9):
    """Main box: the portrait made of cubes that disperse, tumble, and reform
    through the 3 logos (mirrors the three.js cube-disperse effect via SMIL).

    Cycle: portrait -> fb -> ang -> her -> portrait, each transition bursting
    outward at its midpoint. Base = portrait, so static render shows the photo.
    """
    rng = np.random.default_rng(21)
    logo_pts = [np.array(L) for L in logos_pts]

    def resample(L, n):
        idx = np.linspace(0, len(L) - 1, n).astype(int)
        return np.array(L)[idx]

    # ---- regular-grid sampling (cube-disperse style: uniform lattice) ----
    P = np.array(portrait_pts, dtype=float)
    spacing = 3.6
    half = spacing / 2
    # grid of cell centers across the portrait box
    gx = np.arange(FRAME_X + half, FRAME_X + FRAME_W, spacing)
    gy = np.arange(FRAME_Y + half, FRAME_Y + FRAME_H, spacing)
    gxx, gyy = np.meshgrid(gx, gy)
    centers = np.stack([gxx.ravel(), gyy.ravel()], axis=1)
    # keep a cell if any portrait dot falls inside it (occupancy mask)
    cx = np.floor((P[:, 0] - FRAME_X) / spacing).astype(int)
    cy = np.floor((P[:, 1] - FRAME_Y) / spacing).astype(int)
    ncols = len(gx)
    occ = set(zip(cy.tolist(), cx.tolist()))
    occ = { (r, c) for r, c in occ if 0 <= r < len(gy) and 0 <= c < ncols }
    # map occupied cells -> cube positions (cell centers => perfect lattice)
    idxs = sorted(occ)
    sel = np.array([gy[r] for r, c in idxs]), np.array([gx[c] for r, c in idxs])
    P = np.stack(sel, axis=1)
    n_pts = len(P)
    # evenly reduce if still too many
    if n_pts > 9000:
        keep = np.linspace(0, n_pts - 1, 9000).astype(int)
        P = P[keep]
        n_pts = len(P)
    F = resample(logo_pts[0], n_pts)
    A = resample(logo_pts[1], n_pts)
    H = resample(logo_pts[2], n_pts)

    theta = rng.uniform(0, np.pi * 2, n_pts)
    bd = np.stack([np.cos(theta), np.sin(theta)], axis=1) * burst

    # 14 keyframes: P hold, burst, fb, hold, burst, ang, hold, burst, her, hold, burst, P, hold
    kt = [0.00, 0.10, 0.16, 0.22, 0.32, 0.38, 0.44, 0.54, 0.60, 0.66, 0.76, 0.82, 0.88, 1.00]
    kt_str = ";".join(f"{k:.2f}" for k in kt)
    splines = ";".join(["0.4 0 0.6 1"] * (len(kt) - 1))

    parts = []
    for i in range(n_pts):
        p = P[i]; f = F[i]; a = A[i]; h = H[i]; b = bd[i]
        xs = [p[0], p[0], p[0]+b[0], f[0], f[0], f[0]+b[0],
              a[0], a[0], a[0]+b[0], h[0], h[0], h[0]+b[0], p[0], p[0]]
        ys = [p[1], p[1], p[1]+b[1], f[1], f[1], f[1]+b[1],
              a[1], a[1], a[1]+b[1], h[1], h[1], h[1]+b[1], p[1], p[1]]
        xv = ";".join(f"{x:.1f} {y:.1f}" for x, y in zip(xs, ys))
        parts.append(
            f'<g transform="translate({p[0]:.1f} {p[1]:.1f})">'
            f'<animateTransform attributeName="transform" type="translate" '
            f'values="{xv}" keyTimes="{kt_str}" dur="14s" begin="3s" '
            f'repeatCount="indefinite" calcMode="spline" keySplines="{splines}"/>'
            f'<rect x="-{cube/2:.1f}" y="-{cube/2:.1f}" '
            f'width="{cube}" height="{cube}" class="cube"/></g>'
        )
    return "\n".join(parts)


def build_svg(dark=True):
    p = PALETTE_DARK if dark else PALETTE_LIGHT

    # portrait dots in grid coords -> banner coords
    pd = load_dots("portrait_dots.npy")
    arr = np.array(pd, dtype=float)
    px = arr[:, 0] * SCALE + OX
    py = arr[:, 1] * SCALE + OY
    portrait_pts = list(zip(px.tolist(), py.tolist()))

    # logo dots: dithered at portrait pitch (214 cells in a 300px box ~ 1.4px).
    # map grid cell -> banner box directly (no norm/densify needed).
    logo_box_w, logo_box_h = 300, 300
    lx = FRAME_X + (FRAME_W - logo_box_w) / 2
    ly = FRAME_Y + (FRAME_H - logo_box_h) / 2
    logo_cells = 214  # ~300px / 1.4px pitch
    logos = []
    for n in ("fb.npy", "ang.npy", "agent.npy"):
        L = np.array(load_dots(n), dtype=float)
        if len(L) == 0:
            logos.append([])
            continue
        sx = logo_box_w / logo_cells
        sy = logo_box_h / logo_cells
        logos.append([(x * sx + lx, y * sy + ly) for x, y in L])

    cubes = build_band_traveler_layer(p, portrait_pts, logos, burst=60)

    info = build_info_svg(p)
    style = f"""
    .bg {{ fill: {p['bg']}; }}
    .panel {{ fill: {p['panel']}; stroke: {p['panel_stroke']}; stroke-width: 1.5; }}
    .cube {{ fill: {p['chrome']}; }}
    .portrait {{ stroke: {p['portrait']}; stroke-width: 1.5; stroke-linecap: round; fill: none; }}
    .trav {{ fill: {p['chrome']}; }}
    .lbl {{ font-family: 'Courier New', monospace; font-size: 14px; fill: {p['chrome']}; }}
    .val {{ font-family: 'Courier New', monospace; font-size: 14px; fill: {p['chrome_dim']}; }}
    .leader {{ stroke: {p['chrome_dim']}; stroke-width: 1; stroke-dasharray: 1 3; opacity: 0.5; }}
    .title {{ font-family: 'Courier New', monospace; font-size: 13px; fill: {p['chrome']}; }}
    .live {{ font-family: 'Courier New', monospace; font-size: 12px; fill: {p['live']}; }}
    .badge {{ fill: {p['panel']}; stroke: {p['chrome']}; }}
    """

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<style>{style}</style>
<rect class="bg" width="{W}" height="{H}"/>
<g>
<text x="50" y="42" class="title">profile.sh --live</text>
<rect class="panel" x="{FRAME_X}" y="{FRAME_Y}" width="{FRAME_W}" height="{FRAME_H}" rx="8"/>
<text x="{FRAME_X+12}" y="{FRAME_Y+24}" class="title">VISUAL.MAP</text>
<text x="{FRAME_X+FRAME_W-70}" y="{FRAME_Y+24}" class="live">? LIVE</text>
<text x="{FRAME_X+FRAME_W-150}" y="{FRAME_Y+24}" class="badge" style="font-size:11px">[farman024]</text>
<clipPath id="pv"><rect x="{FRAME_X}" y="{FRAME_Y}" width="{FRAME_W}" height="{FRAME_H}"/></clipPath>
<g clip-path="url(#pv)">
{cubes}
</g>
</g>
 {info}
</svg>"""
    return svg


if __name__ == "__main__":
    dark_svg = build_svg(dark=True)
    light_svg = build_svg(dark=False)
    for name, content in [("dark.svg", dark_svg), ("light.svg", light_svg)]:
        with open(f"{BASE}\\{name}", "w", encoding="utf-8") as f:
            f.write(content)
        import os
        print(name, os.path.getsize(f"{BASE}\\{name}") // 1024, "KB")
