'use client';

import { useCallback } from 'react';

import { copyText } from '../../lib/clipboard';
import { useToast } from '../feedback/useToast';

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
        const copied = await copyText(text);
        if (copied) toast.success(customSuccessMessage || successMessage);
        else toast.error(errorMessage);
        return copied;
    }, [toast, successMessage, errorMessage]);

    return { copyToClipboard };
};
