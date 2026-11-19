// Эффекты типографики и анимации: буквы по очереди, дрожь от холода, плавающее слово, снежинки, пульс кольца, плашка-шторка.
import React from 'react';
import {Easing} from 'remotion';
import {HEAD} from './brand';
import {H, W, prog, Sty} from './kit';

const over = Easing.bezier(0.34, 1.45, 0.64, 1);

/** Буквы появляются по очереди: подпрыгивают снизу с лёгким поворотом и проявляются из размытия. */
export const Letters: React.FC<{x: number; y: number; size: number; fill: string; lf: number; d: number; anchor?: 'start' | 'middle'; font?: string; stagger?: number; float?: number; children: string}> = ({x, y, size, fill, lf, d, anchor = 'start', font = HEAD, stagger = 3, float = 0, children}) => {
  const ref = React.useRef<SVGTextElement>(null);
  const [pos, setPos] = React.useState<{xs: number[]; w: number} | null>(null);
  React.useLayoutEffect(() => {
    const el = ref.current; if (!el) return;
    const n = children.length;
    const xs: number[] = [];
    for (let i = 0; i < n; i++) xs.push(el.getStartPositionOfChar(i).x);
    setPos({xs, w: el.getComputedTextLength()});
  }, [children, size, font]);
  return (
    <g>
      <text ref={ref} x={x} y={y} fontFamily={font} fontWeight={font === HEAD ? 800 : 400} fontSize={size} fill="none" opacity={0}>{children}</text>
      {pos && children.split('').map((ch, i) => {
        if (ch === ' ') return null;
        const p = prog(lf, d + i * stagger, 34, over);
        const fl = float ? Math.sin((lf + i * 9) / 22) * float * Math.min(1, p) : 0;
        const st: Sty = {
          opacity: Math.min(1, p * 2.2), filter: `blur(${(1 - Math.min(1, p)) * 10}px)`,
          transform: `translateY(${(1 - p) * 90 + fl}px) rotate(${(1 - p) * (i % 2 ? 10 : -10)}deg) scale(${0.7 + 0.3 * p})`,
          transformOrigin: '50% 50%', transformBox: 'fill-box',
        };
        return <text key={i} x={pos.xs[i] - (anchor === 'middle' ? pos.w / 2 : 0)} y={y} fontFamily={font} fontWeight={font === HEAD ? 800 : 400} fontSize={size} fill={fill} style={st}>{ch}</text>;
      })}
    </g>
  );
};

/** Лёгкая дрожь от холода: детерминированное смещение после появления. */
export const Shiver: React.FC<{lf: number; from: number; amp?: number; children: React.ReactNode}> = ({lf, from, amp = 4, children}) => {
  const k = Math.min(1, Math.max(0, (lf - from) / 20));
  const dx = (Math.sin(lf * 1.9) + Math.sin(lf * 3.3 + 1)) * 0.5 * amp * k;
  const dy = Math.sin(lf * 2.6 + 2) * 0.5 * amp * k;
  return <g transform={`translate(${dx} ${dy})`}>{children}</g>;
};

/** Снежинки: крупные плоские, их немного (не больше 20 элементов), плывут слева направо и вниз. */
export const Snow: React.FC<{f: number; color: string; n?: number}> = ({f, color, n = 9}) => (
  <g>
    {Array.from({length: n}).map((_, i) => {
      const s = 46 + ((i * 37) % 64);
      const sx = 0.55 + (i % 3) * 0.22, sy = 0.9 + ((i * 5) % 4) * 0.3;
      const x = ((i * 173 + f * sx) % (W + 240)) - 120;
      const y = ((i * 311 + f * sy) % (H + 240)) - 120;
      const rot = f * (i % 2 ? 0.35 : -0.3) + i * 20;
      return (
        <g key={i} transform={`translate(${x} ${y}) rotate(${rot})`} stroke={color} strokeWidth={Math.max(6, s / 9)} strokeLinecap="round" fill="none">
          {[0, 60, 120].map((a) => <line key={a} x1={-s / 2} y1={0} x2={s / 2} y2={0} transform={`rotate(${a})`} />)}
        </g>
      );
    })}
  </g>
);

/** Плашка выезжает шторкой слева направо. */
export const revealX = (lf: number, d: number, dur = 30): Sty => {
  const p = prog(lf, d, dur);
  return {clipPath: `inset(0 ${(1 - p) * 100}% 0 0)`, opacity: p > 0 ? 1 : 0};
};

/** Кольцо пульсирует вокруг точки на карте. */
export const Pulse: React.FC<{cx: number; cy: number; lf: number; d: number; color: string; r?: number}> = ({cx, cy, lf, d, color, r = 70}) => {
  const t = ((lf - d) % 70 + 70) % 70 / 70;
  if (lf < d) return null;
  return <circle cx={cx} cy={cy} r={18 + r * t} fill="none" stroke={color} strokeWidth={8 * (1 - t) + 1} opacity={1 - t} />;
};
