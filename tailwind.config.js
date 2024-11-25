const {
  getIconCollections,
  iconsPlugin,
} = require("@egoist/tailwindcss-icons");
const colors = require("tailwindcss/colors");

/**
 * @param {keyof colors} name
 * @returns {{ DEFAULT: string, light: string, dark: string }}
 * */
function getColor(name) {
  return {
    DEFAULT: colors[name][500],
    light: colors[name][400],
    dark: colors[name][600],
  }
}

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./static/**/*.js", "**/templates/**/*.{html,dj}"],
  theme: {
    extend: {
      colors: {
        primary: getColor('sky'),
        accent: getColor('emerald'),
        neutral: getColor('slate'),
        background: {
          DEFAULT: colors.gray[100],
        },
        surface: {
          DEFAULT: colors.white,
        },
        error: getColor('rose'),
        warning: getColor('amber'),
        success: getColor('green'),
        info: getColor('blue'),
      },
    },
  },
  plugins: [
    require("@tailwindcss/typography"),
    require("@tailwindcss/forms"),
    iconsPlugin({
      collections: getIconCollections(["lucide", "ri"]),
    }),
  ],
};
