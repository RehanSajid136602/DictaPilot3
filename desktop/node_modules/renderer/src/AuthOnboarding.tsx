import type { ReactNode } from 'react';
import {
  Cloud,
  LockKeyhole,
  Mail,
  RefreshCw,
  ShieldCheck,
  Sparkles,
  UserRound,
} from 'lucide-react';
import { getOnboardingFormConfig, type AuthMode } from '@shared/authFlow';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

type FeedbackTone = 'error' | 'success' | 'info';

interface AuthFormState {
  displayName: string;
  email: string;
  password: string;
  confirmPassword: string;
}

interface AuthOnboardingProps {
  authMode: AuthMode;
  authForm: AuthFormState;
  feedback: string | null;
  feedbackTone: FeedbackTone;
  isSubmitting: boolean;
  onModeChange: (mode: AuthMode) => void;
  onFieldChange: (key: keyof AuthFormState, value: string) => void;
  onEmailSubmit: () => void;
  onGoogleSignIn: () => void;
  renderSecretInput: (
    key: string,
    value: string,
    placeholder: string,
    onChange: (value: string) => void,
  ) => ReactNode;
}

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function AuthOnboarding({
  authMode,
  authForm,
  feedback,
  feedbackTone,
  isSubmitting,
  onModeChange,
  onFieldChange,
  onEmailSubmit,
  onGoogleSignIn,
  renderSecretInput,
}: AuthOnboardingProps) {
  const formConfig = getOnboardingFormConfig(authMode);

  return (
    <section className="auth-gate">
      <div className="auth-gate-hero glass">
        <div className="auth-gate-copy">
          <p className="account-kicker">Account Required</p>
          <h1>Unlock DictaPilot on this desktop</h1>
          <p>
            Every desktop session now starts with your account. Sign in once, restore your workspace,
            and keep DictaPilot tied to you instead of the device.
          </p>
        </div>

        <div className="auth-gate-points">
          <div className="auth-gate-point">
            <ShieldCheck size={18} />
            <div>
              <strong>Session restore</strong>
              <span>Come back to the app already signed in when your saved session is still valid.</span>
            </div>
          </div>
          <div className="auth-gate-point">
            <Cloud size={18} />
            <div>
              <strong>Account-first sync</strong>
              <span>Settings, snippets, and dictionary data follow your account across devices.</span>
            </div>
          </div>
          <div className="auth-gate-point">
            <Sparkles size={18} />
            <div>
              <strong>One-click Google option</strong>
              <span>Use email and password or jump in with Google from the same onboarding flow.</span>
            </div>
          </div>
        </div>
      </div>

      <div className="auth-gate-panel glass">
        <div className="auth-gate-panel-head">
          <div className="auth-mode-switch">
            <button
              className={cn('auth-mode-btn', authMode === 'sign-in' && 'active')}
              type="button"
              onClick={() => onModeChange('sign-in')}
            >
              Sign in
            </button>
            <button
              className={cn('auth-mode-btn', authMode === 'sign-up' && 'active')}
              type="button"
              onClick={() => onModeChange('sign-up')}
            >
              Create account
            </button>
          </div>

          <div className="auth-panel-heading">
            <h2>{formConfig.title}</h2>
            <p>{formConfig.description}</p>
          </div>
        </div>

        {feedback && (
          <div className={cn('feedback-banner', feedbackTone)}>
            {feedbackTone === 'success' ? <ShieldCheck size={15} /> : <RefreshCw size={15} />}
            <span>{feedback}</span>
          </div>
        )}

        <div className="auth-grid">
          {formConfig.showDisplayName && (
            <div className="setting-group">
              <label htmlFor="auth-display-name">Display name</label>
              <input
                id="auth-display-name"
                className="glass-input"
                type="text"
                value={authForm.displayName}
                placeholder="How should DictaPilot label this account?"
                onChange={(event) => onFieldChange('displayName', event.target.value)}
              />
            </div>
          )}

          <div className="setting-group">
            <label htmlFor="auth-email">Email</label>
            <input
              id="auth-email"
              className="glass-input"
              type="email"
              value={authForm.email}
              placeholder="name@example.com"
              onChange={(event) => onFieldChange('email', event.target.value)}
            />
          </div>

          <div className="setting-group">
            <label htmlFor="auth-password">Password</label>
            {renderSecretInput('auth-password', authForm.password, 'Enter password', (value) => {
              onFieldChange('password', value);
            })}
          </div>

          {formConfig.showConfirmPassword && (
            <div className="setting-group">
              <label htmlFor="auth-confirm-password">Confirm password</label>
              {renderSecretInput('auth-confirm-password', authForm.confirmPassword, 'Confirm password', (value) => {
                onFieldChange('confirmPassword', value);
              })}
            </div>
          )}
        </div>

        <button
          className="account-action primary"
          type="button"
          onClick={onEmailSubmit}
          disabled={isSubmitting}
        >
          <UserRound size={16} />
          {isSubmitting ? 'Working...' : formConfig.submitLabel}
        </button>

        <div className="auth-divider">
          <span></span>
          <p>or</p>
          <span></span>
        </div>

        <button
          className="account-action google"
          type="button"
          onClick={onGoogleSignIn}
          disabled={isSubmitting}
        >
          <Mail size={16} />
          {formConfig.googleLabel}
        </button>

        <div className="auth-gate-footnote">
          <LockKeyhole size={15} />
          <p>DictaPilot requires an account before desktop dictation and settings become available.</p>
        </div>
      </div>
    </section>
  );
}
