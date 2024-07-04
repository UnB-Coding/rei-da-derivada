import { headers } from 'next/headers';
import { settings } from './settings';

export const settingsWithAuth = (access_token?: string) => {
    return {
        ...settings,
        headers: {
            ...settings.headers,
            'Authorization': `Bearer ${access_token}`,
        }
    }
}