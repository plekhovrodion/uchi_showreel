// Каркас ролика. Копируется в showreel/<slug>/src/ скриптом scaffold.py. Правь сцены, переходы не пиши с нуля.
// Правила: время только из timing.json (B, TOTAL) и слов диктора (wf), никаких чисел-кадров в коде.
import React from 'react';
import {AbsoluteFill, Audio, staticFile, useCurrentFrame} from 'remotion';
import {C, Fonts, HEAD, BODY, Cloud} from './brand';
import {B, H, Layer, Pop, Svg, Wipe, blurIn, drift, eio, prog, wf, Sty} from './kit';

// ---- Сцены: lf = номер кадра от начала сцены (может быть < 0, пока сцена въезжает под переход) ----
const S1: React.FC<{lf: number}> = ({lf}) => (
  <Svg>
    <rect width={1080} height={1920} fill={C.violet3} />
    <Cloud back={C.violet2} front={C.violet} />
    <g style={blurIn(lf, 20, 54)}>
      <text x={540} y={1000} textAnchor="middle" fontFamily={HEAD} fontWeight={800} fontSize={190} fill={C.ink}>Заголовок</text>
    </g>
  </Svg>
);
const S2: React.FC<{lf: number}> = ({lf}) => (
  <Svg>
    <rect width={1080} height={1920} fill={C.violet} />
    <g style={blurIn(lf, wf(10) - B[0], 44)}>{/* слово №10 озвучки задаёт появление */}
      <text x={70} y={900} fontFamily={HEAD} fontWeight={800} fontSize={170} fill={C.white}>Вторая сцена</text>
    </g>
  </Svg>
);

// ---- Монтаж: границы B[k] между сценами k+1 и k+2 (в кадрах). Окна переходов: шторка [B-28, B+8], push [B-24, B+24] ----
export const Main: React.FC = () => {
  const f = useCurrentFrame();
  const out: React.ReactNode[] = [];
  const [b0] = B;
  if (f < b0 + 8) out.push(<Layer key={1}><S1 lf={f} /></Layer>);
  if (f >= b0 + 8) out.push(<Layer key={2}><S2 lf={f - b0} /></Layer>);
  return (
    <AbsoluteFill style={{backgroundColor: C.violet3}}>
      <Fonts />
      {out}
      <Wipe f={f} from={b0 - 28} to={b0 + 8} color={C.violet /* цвет фона следующей сцены */} />
      <Audio src={staticFile('audio/mix.wav')} />
    </AbsoluteFill>
  );
};
