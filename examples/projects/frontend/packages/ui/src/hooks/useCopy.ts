import { useCallback } from 'react';

import { useToast } from './useToast';

interface UseCopyOptions {
    successMessage?: string;
    errorMessage?: string;
}

export const useCopy = (options: UseCopyOptions = {}) => {
    const { toast } = useToast();

    const {
        successMessage = "Copied to clipboard",
        errorMessage = "Failed to copy to clipboard"
    } = options;

    const copyToClipboard = useCallback(async (text: string, customSuccessMessage?: string) => {
        try {
            await navigator.clipboard.writeText(text);
            toast({
                title: "Success!",
                description: customSuccessMessage || successMessage,
                variant: "default",
            });
            return true;
        } catch (error) {
            console.error('Failed to copy:', error);
            toast({
                title: "Error",
                description: errorMessage,
                variant: "destructive",
            });
            return false;
        }
    }, [toast, successMessage, errorMessage]);

    return { copyToClipboard };
};
