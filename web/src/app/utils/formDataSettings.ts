export const formDataSettings = (access_token?: string) => {
    return {
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'multipart/form-data',
            'Authorization': `Bearer ${access_token}`,
        },
        withCredentials: true,
    }
}