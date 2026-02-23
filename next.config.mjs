/** @type {import('next').NextConfig} */
const nextConfig = {
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    unoptimized: true,
  },
  output: 'standalone', // Enable standalone output for Docker
  reactStrictMode: false, // Disable to reduce hydration warnings
}

export default nextConfig
