'use client';

import React from 'react';
import { settings } from '@/core/settings';

const LoginPage = () => {
  return (
    <div className="text-center mb-6">
      <h2 className="text-2xl font-bold text-foreground">
        Welcome to {settings.app.name}
      </h2>
      <p className="text-sm text-muted-foreground mt-2">
        Secure authentication powered by OTP
      </p>
    </div>
  );
};

export default LoginPage; 