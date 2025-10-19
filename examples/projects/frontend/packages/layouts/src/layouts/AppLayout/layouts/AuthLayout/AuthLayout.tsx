import React from 'react';

import { AuthProvider, useAuthContext } from './AuthContext';
import { IdentifierForm } from './IdentifierForm';
import { OTPForm } from './OTPForm';

import type { AuthProps } from './types';

export const AuthLayout: React.FC<AuthProps> = (props) => {
  return (
    <AuthProvider {...props}>
      <div
        className={`flex flex-col items-center justify-center bg-background py-6 px-4 sm:py-12 sm:px-6 lg:px-8 ${props.className || ''}`}
      >
        <div className="w-full sm:max-w-md space-y-8">
          {props.children}

          <AuthContent />
        </div>
      </div>
    </AuthProvider>
  );
};

// Separate component to use the context
const AuthContent: React.FC = () => {
  const { step, error } = useAuthContext();

  return (
    <>
      {/* {error && (
        <div className="bg-destructive/10 border border-destructive/20 text-destructive px-4 py-3 rounded-md">
          {error}
        </div>
      )} */}

      <div>{step === 'identifier' ? <IdentifierForm /> : <OTPForm />}</div>
    </>
  );
};
