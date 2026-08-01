/** @type {import('next').NextConfig} */
const nextConfig = {
    output: "standalone",
    typescript: { ignoreBuildErrors: true },
    eslint: { ignoreDuringBuilds: true },
    async rewrites() {
        return [
            {
                source: "/api/:path*",
                destination: process.env.NODE_ENV === "development" ? "http://localhost:8000/:path*" : "http://backend:8000/:path*"
            }
        ];
    }
};

export default nextConfig;
