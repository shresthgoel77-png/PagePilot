import type { Config } from "tailwindcss";
import colors from "tailwindcss/colors";

const config: Config = {
    darkMode: ["class"],
    content: [
        './pages/**/*.{js,ts,jsx,tsx,mdx}',
        './components/**/*.{js,ts,jsx,tsx,mdx}',
        './app/**/*.{js,ts,jsx,tsx,mdx}',
    ],
    theme: {
        extend: {
            colors: {
                primary: {
                    DEFAULT: colors.slate[900],
                    foreground: colors.slate[50],
                },
                secondary: {
                    DEFAULT: colors.slate[100],
                    foreground: colors.slate[900],
                },
                accent: {
                    DEFAULT: colors.slate[800],
                    foreground: colors.slate[50],
                },
            },
        },
    },
    plugins: [],
};
export default config;
