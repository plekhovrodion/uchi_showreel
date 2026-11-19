import React from 'react';
import {Composition} from 'remotion';
import {Main} from './Main';
import {TOTAL} from './kit';

export const Root: React.FC = () => (
  <Composition id="Main" component={Main} width={1080} height={1920} fps={60} durationInFrames={TOTAL} />
);
