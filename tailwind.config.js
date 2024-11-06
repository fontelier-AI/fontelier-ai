module.exports = {
  content: [
    './templates/**/*.html',   // Add paths to your HTML relevant files
    './static/**/*.css',       
    './**/*.py',               
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require('daisyui'), // Set up DaisyUI through tailwind
  ],
  daisyui: {
    themes: ["nord", "light", "dark"], 
  },
};


