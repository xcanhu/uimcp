# UI2Code Demo

UI2Code Demo is an interactive web application that demonstrates how to reconstruct high-fidelity frontend code from UI screenshots or design mockups, step by step. It is designed for research, education, and showcasing code generation techniques for modern web interfaces.

## Features
- **Multiple Real-World Demos:** Includes step-by-step reconstructions of YouTube, Instagram, and Google Search interfaces.
- **Progressive Code Generation:** Visualizes the incremental build-up of complex UIs, showing each step in the process.
- **Live Preview:** Responsive, high-fidelity preview of the generated code at every step.
- **Custom Screenshot Upload:** (Optional) Upload your own screenshot to experience AI-driven code generation (if integrated).
- **Final HTML Output:** Each demo provides a complete, production-quality HTML/CSS result for reference.
- **Modern UI/UX:** Built with React, Tailwind CSS, and Monaco Editor for a smooth developer and user experience.

## Getting Started
### Prerequisites
- Node.js (v16+ recommended)
- pnpm (recommended) or npm

### Installation
```bash
pnpm install
# or
npm install
```

### Running the Development Server
```bash
pnpm run dev
# or
npm run dev
```
Visit [http://localhost:5173](http://localhost:5173) in your browser to use the demo.

## Usage
1. **Select a Demo:** Choose from YouTube, Instagram, or Google Search Design in the left sidebar.
2. **Play the Generation:** Click the "▶️ Play" button to watch the UI being reconstructed step by step, or use the slider to scrub through steps manually.
3. **View Final Result:** At the end, see the complete HTML/CSS for the chosen interface.
4. **(Optional) Upload Screenshot:** If enabled, upload your own screenshot to try AI-powered code generation.

## Demo Data & Extensibility
- **Step Files:** Each demo consists of a manifest and a sequence of HTML files (`0001.html`, `0002.html`, ...), plus a `final_*.html` for the complete result.
- **Adding New Demos:**
  1. Prepare your stepwise HTML files and a manifest in a new folder under `public/demos/`.
  2. Add a thumbnail image to `public/assets/`.
  3. Update `public/demos.json` with the new demo's metadata.
- **Assets:** All images used in demos are stored in `public/assets/` and referenced relatively in HTML.

## Dependencies
- [React](https://react.dev/) 18+
- [Vite](https://vitejs.dev/)
- [Tailwind CSS](https://tailwindcss.com/)
- [@monaco-editor/react](https://github.com/suren-atoyan/monaco-react)

## Scripts
- `script/prepare_steps.py`: Python script to generate stepwise HTML files from a design.

## Tools
- `UIED`: Tradition UI element detection used to detect elements in the screenshot and obtain corresponding bboxes.