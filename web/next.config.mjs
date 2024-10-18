/** @type {import('next').NextConfig} */
import withPWAInit from "@ducanh2912/next-pwa";

const withPWA = withPWAInit({
    dest: "public",
});

const nextConfig = {
    images: {
        domains: ['lh3.googleusercontent.com', 'github.com'],
    },
};

export default withPWA({
    ...nextConfig,
});
