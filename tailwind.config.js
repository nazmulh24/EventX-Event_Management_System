/** @type {import('tailwindcss').Config} */
module.exports = {
  // content: [],
  content: [
    "./templates/**/*.html", //------> Template at the --> Root
    "./**/templates/**/*.html", //---> Template inside --> Apps
  ],
  theme: {
    extend: {},
  },
  plugins: [],
};
