module.exports = {
  content: [
    './templates/**/*.html',   // Add paths to your HTML template files
    './static/**/*.css',       // Add paths to your CSS files if you use Tailwind classes in CSS
    './**/*.py',               // Add this if you're using Jinja templates in Flask
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


