import React, { useEffect, useRef } from 'react';
import './OTPInput.css';

const DIGITS = 6;

/**
 * OTPInput - 6 inputs con auto-paste, auto-focus, navegacion con teclado.
 * onComplete(codigo) se invoca cuando los 6 digitos estan listos.
 */
export default function OTPInput({ value, onChange, onComplete, disabled = false, autoFocus = true }) {
  const refs = useRef([]);

  useEffect(() => {
    if (autoFocus && refs.current[0] && !disabled) {
      refs.current[0].focus();
    }
  }, [autoFocus, disabled]);

  const setDigit = (idx, ch) => {
    const v = (ch || '').replace(/\D/g, '').slice(-1);
    if (!v) return;
    const next = (value || '').split('');
    while (next.length < DIGITS) next.push('');
    next[idx] = v;
    const joined = next.join('').slice(0, DIGITS);
    onChange?.(joined);
    if (joined.length === DIGITS) onComplete?.(joined);
    if (idx < DIGITS - 1) refs.current[idx + 1]?.focus();
  };

  const clearDigit = (idx) => {
    const next = (value || '').split('');
    while (next.length < DIGITS) next.push('');
    next[idx] = '';
    onChange?.(next.join(''));
    refs.current[idx]?.focus();
  };

  const handleChange = (idx, e) => {
    setDigit(idx, e.target.value);
  };

  const handleKeyDown = (idx, e) => {
    if (e.key === 'Backspace') {
      e.preventDefault();
      const current = (value || '').padEnd(DIGITS, ' ').split('');
      if (current[idx] && current[idx] !== ' ') {
        clearDigit(idx);
      } else if (idx > 0) {
        const next = (value || '').split('');
        while (next.length < DIGITS) next.push('');
        next[idx - 1] = '';
        onChange?.(next.join(''));
        refs.current[idx - 1]?.focus();
      }
    } else if (e.key === 'ArrowLeft' && idx > 0) {
      e.preventDefault();
      refs.current[idx - 1]?.focus();
    } else if (e.key === 'ArrowRight' && idx < DIGITS - 1) {
      e.preventDefault();
      refs.current[idx + 1]?.focus();
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if ((value || '').length === DIGITS) onComplete?.(value);
    }
  };

  const handlePaste = (idx, e) => {
    const text = (e.clipboardData.getData('text') || '').replace(/\D/g, '').slice(0, DIGITS);
    if (!text) return;
    e.preventDefault();
    const next = text.padEnd(DIGITS, '').split('');
    onChange?.(next.join(''));
    if (text.length === DIGITS) onComplete?.(text);
    const lastIdx = Math.min(text.length, DIGITS) - 1;
    refs.current[lastIdx]?.focus();
  };

  const handleFocus = (e) => e.target.select();

  return (
    <div className="otp-input" role="group" aria-label="Codigo de verificacion">
      {Array.from({ length: DIGITS }).map((_, idx) => {
        const ch = (value || '').padEnd(DIGITS, ' ')[idx] || '';
        return (
          <input
            key={idx}
            ref={(el) => (refs.current[idx] = el)}
            id={`otp-${idx}`}
            type="text"
            inputMode="numeric"
            autoComplete="one-time-code"
            maxLength={1}
            value={ch.trim()}
            onChange={(e) => handleChange(idx, e)}
            onKeyDown={(e) => handleKeyDown(idx, e)}
            onPaste={(e) => handlePaste(idx, e)}
            onFocus={handleFocus}
            disabled={disabled}
            aria-label={`Digito ${idx + 1} de ${DIGITS}`}
            className="otp-input__cell"
          />
        );
      })}
    </div>
  );
}
