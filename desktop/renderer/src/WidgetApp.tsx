import { useEffect, useState, useRef } from 'react';
import { X } from 'lucide-react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import './WidgetApp.css';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

const WAVE_WIDTH = 146;
const WAVE_HEIGHT = 34;
const WAVE_POINT_COUNT = 29;
const WAVE_CENTER_Y = WAVE_HEIGHT / 2;

function clamp(value: number, min: number, max: number) {
  return Math.min(max, Math.max(min, value));
}

function wrapDistance(value: number, center: number) {
  let distance = value - center;
  while (distance > 0.5) distance -= 1;
  while (distance < -0.5) distance += 1;
  return distance;
}

function gaussian(value: number, center: number, width: number) {
  const distance = value - center;
  return Math.exp(-(distance * distance) / width);
}

function createHeartbeatShape(progress: number, beatProgress: number) {
  const local = wrapDistance(progress, beatProgress);
  const pWave = 0.18 * gaussian(local, -0.12, 0.0009);
  const qWave = -0.32 * gaussian(local, -0.028, 0.00012);
  const rWave = 1.48 * gaussian(local, 0, 0.000075);
  const sWave = -0.62 * gaussian(local, 0.022, 0.00014);
  const tWave = 0.34 * gaussian(local, 0.13, 0.0026);
  return pWave + qWave + rWave + sWave + tWave;
}

function createWavePoints(
  state: 'idle' | 'recording' | 'processing' | 'error',
  amplitude: number,
  phase: number
) {
  return Array.from({ length: WAVE_POINT_COUNT }, (_, index) => {
    const progress = index / (WAVE_POINT_COUNT - 1);
    const x = progress * WAVE_WIDTH;
    const centerDistance = Math.abs(progress - 0.5) / 0.5;
    const edgeFade = 1 - Math.pow(centerDistance, 1.45) * 0.22;

    let displacement = 0;

    if (state === 'recording') {
      const beatProgress = (phase * 0.12) % 1;
      const beatStrength = clamp(amplitude * 1.9, 0.42, 1.65);
      const secondaryStrength = beatStrength * 0.72;
      const heartbeat =
        createHeartbeatShape(progress, beatProgress) +
        createHeartbeatShape(progress, (beatProgress + 0.48) % 1) * secondaryStrength;
      const baseline =
        Math.sin(progress * Math.PI * 1.8 + phase * 0.18) * 0.55 +
        Math.cos(progress * Math.PI * 0.95 - phase * 0.11) * 0.28;
      displacement = heartbeat * (8.5 + beatStrength * 7.8) + baseline * 1.15;
    } else if (state === 'processing') {
      const beatProgress = (phase * 0.07) % 1;
      const heartbeat =
        createHeartbeatShape(progress, beatProgress) * 0.72 +
        createHeartbeatShape(progress, (beatProgress + 0.5) % 1) * 0.5;
      const baseline = Math.sin(progress * Math.PI * 2.4 + phase * 0.45) * 0.8;
      displacement = heartbeat * 8.4 + baseline * 1.4;
    } else if (state === 'error') {
      const tremor = Math.sin(progress * Math.PI * 3.4 + phase * 1.6) * 0.6;
      displacement = tremor * 3.2;
    } else {
      const beatProgress = (phase * 0.04) % 1;
      const heartbeat = createHeartbeatShape(progress, beatProgress) * 0.42;
      const baseline = Math.sin(progress * Math.PI * 2 + phase * 0.35) * 0.45;
      displacement = heartbeat * 5 + baseline * 1.05;
    }

    displacement *= edgeFade;
    const y = clamp(WAVE_CENTER_Y + displacement, 3, WAVE_HEIGHT - 3);

    return { x, y };
  });
}

function buildSmoothPath(points: Array<{ x: number; y: number }>) {
  if (points.length === 0) {
    return '';
  }

  if (points.length === 1) {
    return `M ${points[0].x} ${points[0].y}`;
  }

  let path = `M ${points[0].x} ${points[0].y}`;

  for (let index = 0; index < points.length - 1; index += 1) {
    const current = points[index];
    const next = points[index + 1];
    const midX = (current.x + next.x) / 2;
    const midY = (current.y + next.y) / 2;
    path += ` Q ${current.x} ${current.y} ${midX} ${midY}`;
  }

  const lastPoint = points[points.length - 1];
  path += ` T ${lastPoint.x} ${lastPoint.y}`;
  return path;
}

function buildFillPath(points: Array<{ x: number; y: number }>) {
  if (points.length === 0) {
    return '';
  }

  const linePath = buildSmoothPath(points);
  const lastPoint = points[points.length - 1];
  const firstPoint = points[0];
  return `${linePath} L ${lastPoint.x} ${WAVE_HEIGHT} L ${firstPoint.x} ${WAVE_HEIGHT} Z`;
}

function WidgetApp() {
  const [dictationState, setDictationState] = useState<'idle' | 'recording' | 'processing' | 'error'>('idle');
  const [wavePoints, setWavePoints] = useState<Array<{ x: number; y: number }>>(() =>
    createWavePoints('idle', 0.12, 0)
  );

  const stateRef = useRef(dictationState);
  const phaseRef = useRef(0);
  const animationFrameRef = useRef<number | null>(null);
  const amplitudeTargetRef = useRef(0.14);
  const animatedAmplitudeRef = useRef(0.14);

  stateRef.current = dictationState;

  useEffect(() => {
    // @ts-ignore
    if (window.dictationAPI) {
      // @ts-ignore
      const unsubState = window.dictationAPI.onStateChange((data: any) => {
        setDictationState(data.state);
      });

      // @ts-ignore
      const unsubAmp = window.dictationAPI.onAmplitudeUpdate((amp: number) => {
        if (stateRef.current === 'recording') {
          amplitudeTargetRef.current = clamp(amp * 10.5, 0.18, 1.15);
        }
      });

      return () => {
        unsubState();
        if (unsubAmp) unsubAmp();
      };
    }
  }, []);

  useEffect(() => {
    const animate = () => {
      if (stateRef.current === 'recording') {
        animatedAmplitudeRef.current += (amplitudeTargetRef.current - animatedAmplitudeRef.current) * 0.22;
        amplitudeTargetRef.current = Math.max(0.18, amplitudeTargetRef.current * 0.94);
        phaseRef.current += 0.24;
      } else if (stateRef.current === 'processing') {
        animatedAmplitudeRef.current += (0.55 - animatedAmplitudeRef.current) * 0.12;
        phaseRef.current += 0.16;
      } else if (stateRef.current === 'error') {
        animatedAmplitudeRef.current += (0.24 - animatedAmplitudeRef.current) * 0.18;
        phaseRef.current += 0.22;
      } else {
        animatedAmplitudeRef.current += (0.12 - animatedAmplitudeRef.current) * 0.1;
        phaseRef.current += 0.08;
      }

      setWavePoints(createWavePoints(stateRef.current, animatedAmplitudeRef.current, phaseRef.current));
      animationFrameRef.current = window.requestAnimationFrame(animate);
    };

    animationFrameRef.current = window.requestAnimationFrame(animate);

    return () => {
      if (animationFrameRef.current !== null) {
        window.cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, []);

  const strokePath = buildSmoothPath(wavePoints);
  const fillPath = buildFillPath(wavePoints);

  return (
    <div className={cn("widget-container", dictationState)}>
      <button
        className="widget-close-btn"
        type="button"
        onClick={() => window.dictationAPI?.closeWidgetWindow()}
        aria-label="Close widget"
        title="Close widget"
      >
        <X size={12} />
      </button>
      <div className="widget-wave">
        <svg
          className="widget-wave-svg"
          viewBox={`0 0 ${WAVE_WIDTH} ${WAVE_HEIGHT}`}
          aria-hidden="true"
          preserveAspectRatio="none"
        >
          <defs>
            <linearGradient id="wave-stroke-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="rgba(255,255,255,0.3)" />
              <stop offset="16%" stopColor="rgba(255,255,255,0.92)" />
              <stop offset="50%" stopColor="rgba(255,255,255,1)" />
              <stop offset="84%" stopColor="rgba(255,255,255,0.92)" />
              <stop offset="100%" stopColor="rgba(255,255,255,0.3)" />
            </linearGradient>
            <linearGradient id="wave-fill-gradient" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="rgba(255,255,255,0.2)" />
              <stop offset="100%" stopColor="rgba(255,255,255,0)" />
            </linearGradient>
          </defs>
          <path className="wave-fill" d={fillPath} />
          <path className="wave-glow" d={strokePath} />
          <path className="wave-core" d={strokePath} />
        </svg>
      </div>
    </div>
  );
}

export default WidgetApp;
