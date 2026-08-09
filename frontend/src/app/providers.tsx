import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useState, type ReactNode } from 'react';
import React from 'react';

interface ProvidersProps {
  children: ReactNode;
}

export function Providers({ children }: ProvidersProps) {
  // Initialize QueryClient inside component to prevent stale state across SSR/requests
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 5 * 60 * 1000, // 5 minutes - appropriate for medical reference data
            retry: 1,
            refetchOnWindowFocus: false, // Prevent unnecessary re-fetches during clinical workflows
          },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>
      {/* Future providers: AuthProvider, ThemeProvider, NotificationProvider */}
      {children}
    </QueryClientProvider>
  );
}
