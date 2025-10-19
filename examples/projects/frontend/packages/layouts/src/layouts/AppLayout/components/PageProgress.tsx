import { useRouter } from 'next/router';
import { useEffect, useRef, useState } from 'react';

const PageProgress = () => {
    const router = useRouter();
    const [loading, setLoading] = useState(false);
    const [progress, setProgress] = useState(0);
    const [mounted, setMounted] = useState(false);
    const progressTimer = useRef<NodeJS.Timeout | null>(null);

    useEffect(() => {
        setMounted(true);
    }, []);

    // Simulate realistic progress
    const startFakeProgress = () => {
        // Clear any existing timer
        if (progressTimer.current) {
            clearInterval(progressTimer.current);
        }

        setProgress(0);

        // Quickly go to 20% to show immediate feedback
        setTimeout(() => setProgress(20), 50);

        // Then slowly increase to 90% (never reach 100% until actually complete)
        progressTimer.current = setInterval(() => {
            setProgress((prevProgress) => {
                if (prevProgress >= 90) {
                    if (progressTimer.current) {
                        clearInterval(progressTimer.current);
                    }
                    return 90;
                }

                // Slow down as we get closer to 90%
                const increment = 90 - prevProgress;
                return prevProgress + (increment / 10);
            });
        }, 300);
    };

    const completeProgress = () => {
        // Clear any existing timer
        if (progressTimer.current) {
            clearInterval(progressTimer.current);
            progressTimer.current = null;
        }

        // Jump to 100% and then hide after showing completion
        setProgress(100);
        setTimeout(() => {
            setLoading(false);
            setTimeout(() => {
                setProgress(0);
            }, 300); // Wait for fade out animation
        }, 500); // Show 100% for half a second
    };

    useEffect(() => {
        const handleRouteChangeStart = (url: string, { shallow }: { shallow: boolean }) => {
            if (!shallow) {
                setLoading(true);
                startFakeProgress();
            }
        };

        const handleRouteChangeComplete = () => {
            completeProgress();
        };

        const handleRouteChangeError = () => {
            completeProgress();
        };

        router.events.on('routeChangeStart', handleRouteChangeStart);
        router.events.on('routeChangeComplete', handleRouteChangeComplete);
        router.events.on('routeChangeError', handleRouteChangeError);

        return () => {
            if (progressTimer.current) {
                clearInterval(progressTimer.current);
            }
            router.events.off('routeChangeStart', handleRouteChangeStart);
            router.events.off('routeChangeComplete', handleRouteChangeComplete);
            router.events.off('routeChangeError', handleRouteChangeError);
        };
    }, [router.events]);

    if (!mounted) {
        return null;
    }

    return (
        <div
            data-page-progress="root"
            data-loading={loading}
            data-progress={progress}
            className={`fixed top-0 left-0 w-full transition-opacity duration-300 ${
                loading ? 'opacity-100' : 'opacity-0'
            }`}
            style={{
                zIndex: 99999,
                height: '3px',
            }}
        >
            <div
                className="h-full transition-all duration-200 ease-linear"
                style={{
                    width: `${progress}%`,
                    background: 'linear-gradient(90deg, #3b82f6 0%, #60a5fa 50%, #3b82f6 100%)',
                    boxShadow: '0 0 10px rgba(59, 130, 246, 0.6), 0 0 20px rgba(59, 130, 246, 0.4), 0 0 30px rgba(59, 130, 246, 0.2)',
                    filter: 'drop-shadow(0 0 8px rgba(59, 130, 246, 0.8))',
                }}
            />
        </div>
    );
};

export default PageProgress; 