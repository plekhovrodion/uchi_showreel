// Набор помощников для роликов Учи.ру в Remotion. Всё считается от номера кадра, 60 fps.
import React from 'react';
import {AbsoluteFill, Easing, interpolate, staticFile} from 'remotion';
import {C} from './brand';
import {CLOUD_BACK, CLOUD_FRONT} from './clouds';
import words from './words.json';
import timing from './timing.json';

export const W = 1080, H = 1920;
export const B: number[] = timing.boundaries;          // границы сцен в кадрах, из timing.json
export const TOTAL: number = timing.total;             // длительность ролика в кадрах, из timing.json
export const eo = Easing.bezier(0.16, 1, 0.3, 1);      // вход
export const eio = Easing.bezier(0.45, 0, 0.2, 1);     // крупные перемещения и переходы
export const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
export const prog = (lf: number, delay: number, dur: number, ease = eo) => interpolate(lf, [delay, delay + dur], [0, 1], {...clamp, easing: ease});
/** Кадр, на котором диктор начинает слово номер i (сквозной индекс по всему тексту). */
export const wf = (i: number) => Math.round((words as {start: number}[])[i].start * 60);

export type Sty = React.CSSProperties;
export const blurIn = (lf: number, d: number, dur = 48, dy = 30): Sty => {
  const p = prog(lf, d, dur);
  return {opacity: Math.min(1, p * 1.6), filter: `blur(${(1 - p) * 14}px)`, transform: `translateY(${(1 - p) * dy}px) scale(${0.95 + 0.05 * p})`, transformOrigin: '50% 50%', transformBox: 'fill-box'};
};
export const drift = (f: number, amp: number, period: number, ph = 0) => Math.sin(((f + ph) / period) * Math.PI * 2) * amp;

export const Img: React.FC<{n: string; x: number; y: number; w: number; rot?: number; style?: Sty}> = ({n, x, y, w, rot = 0, style}) => (
  <image href={staticFile(`images/${n}.png`)} x={x} y={y} width={w} height={w} transform={`rotate(${rot} ${x + w / 2} ${y + w / 2})`} style={style} />
);
export const Pop: React.FC<{lf: number; d: number; children: React.ReactNode}> = ({lf, d, children}) => {
  const p = prog(lf, d, 40, Easing.bezier(0.34, 1.35, 0.64, 1));
  return <g style={{opacity: Math.min(1, p * 2.5), transform: `scale(${0.6 + 0.4 * p})`, transformOrigin: '50% 50%', transformBox: 'fill-box'}}>{children}</g>;
};
export const Svg: React.FC<{children: React.ReactNode}> = ({children}) => (
  <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`} style={{position: 'absolute', left: 0, top: 0}}>{children}</svg>
);
export const Clouds: React.FC<{f: number; back: string; front: string}> = ({f, back, front}) => (
  <g>
    <g transform={`translate(0 ${drift(f, 14, 330)})`}><path d={CLOUD_BACK} fill={back} /></g>
    <g transform={`translate(0 ${drift(f, 14, 330, 110)})`}><path d={CLOUD_FRONT} fill={front} /></g>
  </g>
);
export const Shape: React.FC<{d: string; fill: string; x: number; y: number; s: number; side?: string; rot?: number}> = ({d, fill, x, y, s, side = C.ink, rot = 0}) => (
  <g transform={`translate(${x} ${y}) rotate(${rot}) scale(${s})`}>
    <path d={d} transform="translate(12 14)" fill={side} />
    <path d={d} fill={fill} />
  </g>
);

// ---------- Переходы ----------
export const Wipe: React.FC<{f: number; from: number; to: number; color: string}> = ({f, from, to, color}) => {
  if (f < from || f > to) return null;
  const p = eio((f - from) / (to - from));
  const y = 1960 - 1980 * p;
  return (
    <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`} style={{position: 'absolute', left: 0, top: 0}}>
      <g transform={`translate(0 ${y})`} fill={color}>
        <g transform="translate(0 -1440)"><path d={CLOUD_FRONT} /></g>
        <rect x={-50} y={440} width={W + 100} height={2200} />
      </g>
    </svg>
  );
};
export const WordT: React.FC<{f: number; from: number; to: number; color: string}> = ({f, from, to, color}) => {
  if (f < from || f > to) return null;
  const p = (f - from) / (to - from);
  const sc = Math.exp(interpolate(p, [0, 1], [Math.log(0.5), Math.log(26)], {easing: Easing.bezier(0.5, 0, 0.9, 0.6)}));
  const fillA = interpolate(p, [0.8, 1], [0, 1], clamp);
  return (
    <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`} style={{position: 'absolute', left: 0, top: 0}}>
      <g transform={`translate(540 960) scale(${sc}) translate(-540 -960)`}>
        <text x={540} y={1030} textAnchor="middle" fontFamily={HEAD} fontWeight={800} fontSize={200} fill={color}>Босфор</text>
      </g>
      <rect width={W} height={H} fill={color} opacity={fillA} />
    </svg>
  );
};

export const Layer: React.FC<{style?: Sty; children: React.ReactNode}> = ({style, children}) => (
  <AbsoluteFill style={style}>{children}</AbsoluteFill>
);

