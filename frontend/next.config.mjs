/** @type {import('next').NextConfig} */
const nextConfig = {
    output: "standalone",
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
