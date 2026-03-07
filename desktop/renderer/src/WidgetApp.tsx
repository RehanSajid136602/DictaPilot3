import { useEffect, useState, useRef } from 'react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import './WidgetApp.css';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

function WidgetApp() {
  const [dictationState, setDictationState] = useState<'idle' | 'recording' | 'processing' | 'error'>('idle');
  const [amplitude, setAmplitude] = useState(0);

  const stateRef = useRef(dictationState);
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
          // Smooth out and boost amplitude for visual effect
          setAmplitude(Math.min(1.0, Math.max(0.1, amp * 5.0)));
        }
      });

      return () => {
        unsubState();
        if (unsubAmp) unsubAmp();
      };
    }
  }, []);

  const bars = Array.from({ length: 11 });

  return (
    <div className={cn("widget-container", dictationState)}>
      {bars.map((_, i) => {
        // simple arch curve
        const centerDist = Math.abs(i - 5) / 5;
        const arch = 1.0 - Math.pow(centerDist, 1.5) * 0.5;

        let height = 4;
        if (dictationState === 'recording') {
          height = 4 + (amplitude * 20 * arch);
        } else if (dictationState === 'processing') {
          height = 4 + (Math.sin(Date.now() / 200 + i) * 10 * arch);
        }

        return (
          <div
            key={i}
            className="bar"
            style={{ height: `${Math.max(4, height)}px` }}
          />
        );
      })}
    </div>
  );
}

export default WidgetApp;