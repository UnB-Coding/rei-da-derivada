/** @type {import('next').NextConfig} */
import withPWAInit from "@ducanh2912/next-pwa";

const withPWA = withPWAInit({
    dest: "public",
    register: true,
    reloadOnOnline: true,
    fallbacks: {
        document: "src/app/~offline/page.tsx",
    },
    cacheOnFrontEndNav:true,
});

const nextConfig = {
    images: {
        remotePatterns: [
            {
                protocol: 'https',
                hostname: 'lh3.googleusercontent.com',
            },
            {
                protocol: 'https',
                hostname: 'github.com',
            },
        ],
    },
};

export default withPWA({
    ...nextConfig,
});
