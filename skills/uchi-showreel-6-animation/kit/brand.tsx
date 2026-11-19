import React from 'react';
import {continueRender, delayRender, staticFile} from 'remotion';

export const C = {
  violet: '#6656F7', violet2: '#ADA4FF', violet3: '#DFD9FF', ink: '#362F73',
  coral: '#FE5C57', coral2: '#FF8A86', coral3: '#FFC5C3', coralDark: '#741E1B',
  yellow: '#FFCF24', yellow2: '#FFE16C', white: '#FFFFFF',
};
export const HEAD = "'Oceanic Grotesk Condensed', sans-serif";
export const BODY = "'Factor A', sans-serif";

export const Fonts: React.FC = () => {
  const [h] = React.useState(() => delayRender('fonts'));
  React.useEffect(() => {
    const a = new FontFace('Oceanic Grotesk Condensed', `url(${staticFile('fonts/Oceanic Grotesk Condensed-Extrabold-Web.ttf')})`, {weight: '800'});
    const b = new FontFace('Factor A', `url(${staticFile('fonts/Factor A-Regular-Web.ttf')})`, {weight: '400'});
    Promise.all([a.load(), b.load()]).then((fs) => {
      fs.forEach((f) => document.fonts.add(f));
      continueRender(h);
    });
  }, [h]);
  return null;
};

import {CLOUD_BACK, CLOUD_FRONT} from './clouds';
// Облака бренда из шаблона 02: задний и передний слой, цвета задаются снаружи
export const Cloud: React.FC<{back: string; front: string}> = ({back, front}) => (
  <g><path d={CLOUD_BACK} fill={back} /><path d={CLOUD_FRONT} fill={front} /></g>
);
