import { useEffect, useRef, useState, useLayoutEffect } from 'react';
import Editor from '@monaco-editor/react';
import DemoSelector from './DemoSelector';

// Auto-scale Hook - simplified back to its original purpose
function useAutoScale(iframeRef, wrapRef) {
  useLayoutEffect(() => {
    if (!iframeRef.current || !wrapRef.current) return;

    const calc = () => {
      const doc = iframeRef.current.contentDocument;
      if (!doc || !doc.body) return;

      // Inject base styles for responsive scaling, if not present
      if (!doc.querySelector('style[data-responsive-scale]')) {
        const style = doc.createElement('style');
        style.setAttribute('data-responsive-scale', '');
        style.innerHTML = `
          html, body {
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100%;
            overflow: hidden;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          }
          .container {
            position: relative;
            width: 100%;
            height: 100vh;
            box-sizing: border-box;
          }
          .box {
            position: absolute;
            box-sizing: border-box;
            overflow: hidden;
          }
          .box img { max-width: 100%; height: auto; }
          .box p, .box span:not(.sidebar-text) { font-size: max(16px, 1.2vw); line-height: 1.4; }
          .box button { font-size: max(14px, 1.0vw); padding: max(6px, 0.4vw) max(12px, 0.8vw); }
          .box input { font-size: max(16px, 1.2vw); padding: max(6px, 0.4vw) max(12px, 0.8vw); }
          .box svg { width: max(20px, 1.5vw); height: max(20px, 1.5vw); }
        `;
        doc.head.appendChild(style);
      }
    };

    const iframe = iframeRef.current;
    iframe.addEventListener('load', calc);
    calc();

    window.addEventListener('resize', calc);
    return () => {
      iframe.removeEventListener('load', calc);
      window.removeEventListener('resize', calc);
    };
  }, [iframeRef, wrapRef]);
}

// Instagram-specific preview component
function InstagramPreview({ code }) {
  const iframeRef = useRef(null);
  const wrapRef = useRef(null);
  
  useLayoutEffect(() => {
    if (!iframeRef.current || !wrapRef.current) return;

    const calc = () => {
      const doc = iframeRef.current.contentDocument;
      if (!doc || !doc.body) return;

      // Inject Instagram-specific responsive styles
      if (!doc.querySelector('style[data-instagram-responsive]')) {
        const style = doc.createElement('style');
        style.setAttribute('data-instagram-responsive', '');
        style.innerHTML = `
          html, body {
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100%;
            overflow: hidden;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          }
          .container {
            position: relative;
            width: 100%;
            height: 100vh;
            box-sizing: border-box;
            overflow: hidden;
          }
          .box {
            position: absolute;
            box-sizing: border-box;
            overflow: hidden;
          }
          // .box img { max-width: 100%; height: auto; }
          // .box p, .box span { font-size: max(14px, 1.0vw); line-height: 1.4; }
          // .box button { font-size: max(12px, 0.9vw); padding: max(4px, 0.3vw) max(8px, 0.6vw); }
          // .box input { font-size: max(14px, 1.0vw); padding: max(4px, 0.3vw) max(8px, 0.6vw); }
          // .box svg { width: max(16px, 1.2vw); height: max(16px, 1.2vw); }
        `;
        doc.head.appendChild(style);
      }
    };

    const iframe = iframeRef.current;
    iframe.addEventListener('load', calc);
    calc();

    window.addEventListener('resize', calc);
    return () => {
      iframe.removeEventListener('load', calc);
      window.removeEventListener('resize', calc);
    };
  }, [iframeRef, wrapRef]);

  return (
    <div className="w-full h-full bg-gray-100 flex items-center justify-center p-2">
      <div ref={wrapRef} className="w-full h-full bg-white shadow-xl rounded-lg overflow-hidden">
        <iframe 
          ref={iframeRef} 
          srcDoc={code} 
          className="w-full h-full border-0"
          style={{ 
            transform: 'scale(1.0)',
            transformOrigin: 'center',
            imageRendering: '-webkit-optimize-contrast'
          }}
        />
      </div>
    </div>
  );
}

// Design-specific preview component
function DesignPreview({ code }) {
  const iframeRef = useRef(null);
  const wrapRef = useRef(null);

  useLayoutEffect(() => {
    if (!iframeRef.current || !wrapRef.current) return;
    const calc = () => {
      const doc = iframeRef.current.contentDocument;
      if (!doc || !doc.body) return;
      if (!doc.querySelector('style[data-design-responsive]')) {
        const style = doc.createElement('style');
        style.setAttribute('data-design-responsive', '');
        style.innerHTML = `
          html, body {
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100%;
            overflow: hidden;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          }
          .container {
            position: relative;
            width: 100%;
            height: 100vh;
            box-sizing: border-box;
            overflow: hidden;
          }
          .box {
            position: absolute;
            box-sizing: border-box;
            overflow: hidden;
          }
        `;
        doc.head.appendChild(style);
      }
    };
    const iframe = iframeRef.current;
    iframe.addEventListener('load', calc);
    calc();
    window.addEventListener('resize', calc);
    return () => {
      iframe.removeEventListener('load', calc);
      window.removeEventListener('resize', calc);
    };
  }, [iframeRef, wrapRef]);

  return (
    <div className="w-full h-full bg-gray-100 flex items-center justify-center p-2">
      <div ref={wrapRef} className="w-full h-full bg-white shadow-xl rounded-lg overflow-hidden">
        <iframe
          ref={iframeRef}
          srcDoc={code}
          className="w-full h-full border-0"
          style={{
            transform: 'scale(1.0)',
            transformOrigin: 'top left',
            imageRendering: '-webkit-optimize-contrast'
          }}
        />
      </div>
    </div>
  );
}

// LinkedIn-specific preview component
function LinkedInPreview({ code }) {
  const iframeRef = useRef(null);
  const wrapRef = useRef(null);

  useLayoutEffect(() => {
    if (!iframeRef.current || !wrapRef.current) return;
    const calc = () => {
      const doc = iframeRef.current.contentDocument;
      if (!doc || !doc.body) return;
      if (!doc.querySelector('style[data-linkedin-responsive]')) {
        const style = doc.createElement('style');
        style.setAttribute('data-linkedin-responsive', '');
        style.innerHTML = `
          html, body {
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100%;
            overflow: hidden;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          }
          .container {
            position: relative;
            width: 100%;
            height: 100vh;
            box-sizing: border-box;
            overflow: hidden;
          }
          .box {
            position: absolute;
            box-sizing: border-box;
            overflow: hidden;
          }
        `;
        doc.head.appendChild(style);
      }
    };
    const iframe = iframeRef.current;
    iframe.addEventListener('load', calc);
    calc();
    window.addEventListener('resize', calc);
    return () => {
      iframe.removeEventListener('load', calc);
      window.removeEventListener('resize', calc);
    };
  }, [iframeRef, wrapRef]);

  return (
    <div className="w-full h-full bg-gray-100 flex items-center justify-center p-2">
      <div ref={wrapRef} className="w-full h-full bg-white shadow-xl rounded-lg overflow-hidden">
        <iframe
          ref={iframeRef}
          srcDoc={code}
          className="w-full h-full border-0"
          style={{
            transform: 'scale(1.01)',
            transformOrigin: 'center',
            // imageRendering: '-webkit-optimize-contrast'
          }}
        />
      </div>
    </div>
  );
}

// Scaled preview component
function ScaledPreview({ code, demoId }) {
  const iframeRef = useRef(null);
  const wrapRef = useRef(null);
  
  useAutoScale(iframeRef, wrapRef);
  
  if (demoId === 'instagram') {
    return <InstagramPreview code={code} />;
  }
  if (demoId === 'design') {
    return <DesignPreview code={code} />;
  }
  if (demoId === 'linkedin') {
    return <LinkedInPreview code={code} />;
  }

  // Default preview for all other demos
  return (
    <div ref={wrapRef} className="w-full h-full overflow-hidden bg-gray-50">
      <iframe 
        ref={iframeRef} 
        srcDoc={code} 
        className="w-full h-full border-0 bg-white"
        style={{ 
          imageRendering: '-webkit-optimize-contrast',
          minHeight: '800px',
          transform: 'scale(1.1)',
          transformOrigin: 'top left'
        }}
      />
    </div>
  );
}

export default function App() {
  const [currentDemo, setCurrentDemo] = useState(null);
  const [showDemoSelector, setShowDemoSelector] = useState(true);
  const [steps, setSteps] = useState([]);
  const [idx, setIdx] = useState(0);
  const [progress, setProgress] = useState(0); // Continuous progress percentage
  const [code, setCode] = useState(`
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Screenshot to Code</title>
      <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-50 flex items-center justify-center min-h-screen">
      <div class="text-center">
        <div class="text-6xl mb-4">🎨</div>
        <h1 class="text-2xl font-bold text-gray-800 mb-2">UI2Code Demo</h1>
        <p class="text-gray-600 mb-4">Choose a demo to see how code generation works</p>
        <div class="bg-white rounded-lg p-6 shadow-lg max-w-md mx-auto">
          <p class="text-sm text-gray-500">
            Select a demo from the list to start the interactive code generation experience.
          </p>
        </div>
      </div>
    </body>
    </html>
  `);
  const [playing, setPlaying] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const [loadingError, setLoadingError] = useState(null);
  const [uploadedImage, setUploadedImage] = useState(null);
  const [imageReady, setImageReady] = useState(false);
  const intervalRef = useRef(null);
  const progressIntervalRef = useRef(null);
  const fileInputRef = useRef(null);
  const [designPrompt, setDesignPrompt] = useState('');

  // load manifest when demo is selected
  useEffect(() => {
    if (!currentDemo) return;
    
    fetch(currentDemo.manifest)
      .then(res => {
        if (!res.ok) {
          throw new Error(`HTTP error! status: ${res.status}`);
        }
        return res.json();
      })
      .then(data => {
        setSteps(data);
        setLoadingError(null);
      })
      .catch(err => {
        console.error('Failed to load manifest:', err);
        setLoadingError('Failed to load build steps manifest');
        // Create a simple default step
        setSteps([
          { file: 'demo.html', caption: 'Demo Interface', description: 'Demo Interface' }
        ]);
      });
  }, [currentDemo]);

  // load code whenever idx changes - but only if image is ready AND playing
  useEffect(() => {
    if (!steps.length || !imageReady || !playing || !currentDemo) return;

    // if finalHtml is available, show finalHtml when idx equals steps.length
    if (
      currentDemo.finalHtml &&
      idx === steps.length
    ) {
      // load finalHtml
      fetch(currentDemo.finalHtml)
        .then(res => {
          if (!res.ok) {
            throw new Error(`HTTP error! status: ${res.status}`);
          }
          return res.text();
        })
        .then(html => {
          setCode(html);
          setLoadingError(null);
        })
        .catch(err => {
          console.error('Failed to load final HTML:', err);
          setLoadingError('Failed to load final HTML');
          setCode(`
            <!DOCTYPE html>
            <html lang="en">
            <head>
              <meta charset="UTF-8">
              <meta name="viewport" content="width=device-width, initial-scale=1.0">
              <title>Error</title>
              <script src="https://cdn.tailwindcss.com"></script>
            </head>
            <body class="bg-gray-100 flex items-center justify-center min-h-screen">
              <div class="text-center">
                <div class="text-6xl mb-4">⚠️</div>
                <h1 class="text-2xl font-bold text-gray-800 mb-2">Final HTML Not Found</h1>
                <p class="text-gray-600 mb-4">Could not load final HTML</p>
                <div class="bg-white rounded-lg p-6 shadow-lg max-w-md mx-auto">
                  <p class="text-sm text-gray-500">
                    The final HTML file might be missing or the path is incorrect.
                  </p>
                </div>
              </div>
            </body>
            </html>
          `);
        });
    } else {
        // normal steps
      const step = steps[idx];
      if (!step) return;
      const demoBasePath = currentDemo.manifest.replace('/manifest.json', '');
      fetch(demoBasePath + '/' + step.file)
        .then(res => {
          if (!res.ok) {
            throw new Error(`HTTP error! status: ${res.status}`);
          }
          return res.text();
        })
        .then(html => {
          setCode(html);
          setLoadingError(null);
        })
        .catch(err => {
          console.error('Failed to load step file:', err);
          setLoadingError(`Failed to load step: ${step.file}`);
          // Create a simple error page
          setCode(`
            <!DOCTYPE html>
            <html lang="en">
            <head>
              <meta charset="UTF-8">
              <meta name="viewport" content="width=device-width, initial-scale=1.0">
              <title>Error</title>
              <script src="https://cdn.tailwindcss.com"></script>
            </head>
            <body class="bg-gray-100 flex items-center justify-center min-h-screen">
              <div class="text-center">
                <div class="text-6xl mb-4">⚠️</div>
                <h1 class="text-2xl font-bold text-gray-800 mb-2">File Not Found</h1>
                <p class="text-gray-600 mb-4">Could not load: ${step.file}</p>
                <div class="bg-white rounded-lg p-6 shadow-lg max-w-md mx-auto">
                  <p class="text-sm text-gray-500">
                    This might be because the build steps haven't been generated yet, 
                    or the file path is incorrect.
                  </p>
                </div>
              </div>
            </body>
            </html>
          `);
        });
    }
  }, [idx, steps, imageReady, playing, currentDemo]);

  // autoplay with smooth progress and auto-stop at the end
  useEffect(() => {
    if (!playing) {
      clearInterval(progressIntervalRef.current);
      return;
    }
    
    // Check if the current demo has a specific interval time
    const customIntervalTime = currentDemo?.intervalTime;
    
    // Define total duration based on whether a custom interval is set
    const totalDuration = customIntervalTime 
      ? customIntervalTime * (steps.length || 1) // Use custom time if available
      : (steps.length > 100 ? 100 : 200) * (steps.length || 1); // Default dynamic duration
      
    const updateInterval = 50; // Update UI every 50ms
    const progressStep = 100 / (totalDuration / updateInterval);
    
    progressIntervalRef.current = setInterval(() => {
      setProgress(currentProgress => {
        const newProgress = currentProgress + progressStep;
        
        // Calculate which step we should be at
        // if finalHtml is available, total steps include finalHtml
        const totalSteps = currentDemo?.finalHtml ? steps.length + 1 : steps.length;
        const targetStepIndex = Math.min(totalSteps, Math.floor((newProgress / 100) * totalSteps));
        
        // Directly set the index without causing re-trigger of this effect
        setIdx(targetStepIndex);
        
        // If reaching 100%, stop playing
        if (newProgress >= 100) {
          setPlaying(false);
          // Ensure we are at the very end (finalHtml if available, otherwise last step)
          setIdx(totalSteps - 1);
          return 100;
        }
        
        return newProgress;
      });
    }, updateInterval);
    
    return () => {
      clearInterval(progressIntervalRef.current);
    };
  }, [playing, steps.length, currentDemo]);

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const files = Array.from(e.dataTransfer.files);
    handleFiles(files);
  };

  const handleFileSelect = (e) => {
    const files = Array.from(e.target.files);
    handleFiles(files);
  };

  const handleDemoSelect = (demo) => {
    setCurrentDemo(demo);
    setShowDemoSelector(false);
    setUploadedImage(demo.thumbnail);
    setImageReady(true);
    setIdx(0);
    setProgress(0); // Reset progress
    setPlaying(false);
    // Set ready page
    setCode(`
      <!DOCTYPE html>
      <html lang="en">
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Ready to Generate</title>
        <script src="https://cdn.tailwindcss.com"></script>
      </head>
      <body class="bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center min-h-screen">
        <div class="text-center">
          <div class="text-6xl mb-4">🚀</div>
          <h1 class="text-3xl font-bold text-gray-800 mb-2">Ready to Generate!</h1>
          <p class="text-gray-600 mb-4">Demo "${demo.name}" is loaded and ready</p>
          <div class="bg-white rounded-lg p-6 shadow-lg max-w-md mx-auto">
            <p class="text-sm text-gray-500 mb-4">
              Click the "▶️ Play" button to start the step-by-step code generation.
            </p>
            <div class="flex items-center justify-center space-x-2">
              <div class="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
              <span class="text-sm font-medium text-green-600">Ready to start</span>
            </div>
          </div>
        </div>
      </body>
      </html>
    `);
  };

  const handleFiles = (files) => {
    const imageFiles = files.filter(file => file.type.startsWith('image/'));
    if (imageFiles.length > 0) {
      const file = imageFiles[0];
      const reader = new FileReader();
      reader.onload = (e) => {
        console.log('Image loaded:', e.target.result ? 'Success' : 'Failed');
        setUploadedImage(e.target.result);
        setImageReady(true);
        setIdx(0); // Reset to first step
        setProgress(0); // Reset progress
        setPlaying(false); // Don't auto-play, wait for user to click play
        // Set ready page
        setCode(`
          <!DOCTYPE html>
          <html lang="en">
          <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Ready to Generate</title>
            <script src="https://cdn.tailwindcss.com"></script>
          </head>
          <body class="bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center min-h-screen">
            <div class="text-center">
              <div class="text-6xl mb-4">🚀</div>
              <h1 class="text-3xl font-bold text-gray-800 mb-2">Ready to Generate!</h1>
              <p class="text-gray-600 mb-4">Your screenshot has been uploaded successfully</p>
              <div class="bg-white rounded-lg p-6 shadow-lg max-w-md mx-auto">
                <p class="text-sm text-gray-500 mb-4">
                  Click the "▶️ Play" button to start generating code from your design.
                </p>
                <div class="flex items-center justify-center space-x-2">
                  <div class="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                  <span class="text-sm font-medium text-green-600">Ready to start</span>
                </div>
              </div>
            </div>
          </body>
          </html>
        `);
      };
      reader.onerror = (e) => {
        console.error('Error reading file:', e);
        setLoadingError('Failed to read image file');
      };
      reader.readAsDataURL(file);
    }
  };

  const handlePlayToggle = () => {
    if (!imageReady && !playing) {
      // If no image uploaded, prompt user
      return;
    }
    setPlaying(p => {
      const newPlaying = !p;
      // If starting to play, reset progress
      if (newPlaying) {
        setProgress(0);
        setIdx(0);
      }
      // If starting to play, immediately load first step code
      if (newPlaying && steps.length > 0 && currentDemo) {
        const step = steps[0];
        if (step) {
          const demoBasePath = currentDemo.manifest.replace('/manifest.json', '');
          fetch(demoBasePath + '/' + step.file)
            .then(res => {
              if (!res.ok) {
                throw new Error(`HTTP error! status: ${res.status}`);
              }
              return res.text();
            })
            .then(html => {
              setCode(html);
              setLoadingError(null);
            })
            .catch(err => {
              console.error('Failed to load step file:', err);
              setLoadingError(`Failed to load step: ${step.file}`);
            });
        }
      }
      return newPlaying;
    });
  };

  const handleReset = () => {
    setIdx(0);
    setProgress(0); // Reset progress
    setPlaying(false);
    // If image uploaded, return to Ready state, otherwise return to initial state
    if (imageReady) {
      setCode(`
        <!DOCTYPE html>
        <html lang="en">
        <head>
          <meta charset="UTF-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <title>Ready to Generate</title>
          <script src="https://cdn.tailwindcss.com"></script>
        </head>
        <body class="bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center min-h-screen">
          <div class="text-center">
            <div class="text-6xl mb-4">🚀</div>
            <h1 class="text-3xl font-bold text-gray-800 mb-2">Ready to Generate!</h1>
            <p class="text-gray-600 mb-4">Your screenshot has been uploaded successfully</p>
            <div class="bg-white rounded-lg p-6 shadow-lg max-w-md mx-auto">
              <p class="text-sm text-gray-500 mb-4">
                Click the "▶️ Play" button to start generating code from your design.
              </p>
              <div class="flex items-center justify-center space-x-2">
                <div class="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                <span class="text-sm font-medium text-green-600">Ready to start</span>
              </div>
            </div>
          </div>
        </body>
        </html>
      `);
    }
  };

  const step = steps[idx] || {};
  const isDesignDemo = currentDemo?.id === 'design';

  // If showing demo selector
  if (showDemoSelector) {
    return (
      <div className="min-h-screen bg-gray-50">
        <DemoSelector onDemoSelect={handleDemoSelect} currentDemo={currentDemo} />
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Left side - Screenshot to Code area */}
      <div className="w-2/5 bg-white border-r border-gray-200 flex flex-col">
        {/* Title area */}
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center justify-between mb-1">
            <h1 className="text-xl font-bold text-gray-900">Screenshot to Code</h1>
            <button
              onClick={() => setShowDemoSelector(true)}
              className="text-xs text-blue-600 hover:text-blue-800 underline"
            >
              ← Back to Demos
            </button>
          </div>
          <p className="text-sm text-gray-600">
            {currentDemo ? `Demo: ${currentDemo.name}` : 'Drag & drop a screenshot to get started.'}
          </p>
        </div>

        {/* Upload area */}
        <div className="p-4 border-b border-gray-100">
          {!uploadedImage ? (
            <div
              className={`border-2 border-dashed rounded-lg p-4 text-center cursor-pointer transition-colors ${
                dragOver ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'
              }`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
            >
              <div className="text-2xl mb-2">📸</div>
              <p className="text-sm text-gray-600 mb-1">Drop an image here</p>
              <p className="text-xs text-gray-500">or click to browse</p>
            </div>
          ) : (
            <div className="text-center">
              <div className="text-sm text-green-700 font-medium mb-2">✅ Image uploaded successfully!</div>
              <button 
                className="text-xs text-blue-600 hover:text-blue-800 underline"
                onClick={() => {
                  setUploadedImage(null);
                  setImageReady(false);
                  setPlaying(false);
                  setIdx(0);
                  setProgress(0); // Reset progress
                  // Clear file input
                  if (fileInputRef.current) {
                    fileInputRef.current.value = '';
                  }
                  // Reset code to initial state
                  setCode(`
                    <!DOCTYPE html>
                    <html lang="en">
                    <head>
                      <meta charset="UTF-8">
                      <meta name="viewport" content="width=device-width, initial-scale=1.0">
                      <title>Screenshot to Code</title>
                      <script src="https://cdn.tailwindcss.com"></script>
                    </head>
                    <body class="bg-gray-50 flex items-center justify-center min-h-screen">
                      <div class="text-center">
                        <div class="text-6xl mb-4">📸</div>
                        <h1 class="text-2xl font-bold text-gray-800 mb-2">Upload a Screenshot</h1>
                        <p class="text-gray-600 mb-4">Upload an image to start generating code</p>
                        <div class="bg-white rounded-lg p-6 shadow-lg max-w-md mx-auto">
                          <p class="text-sm text-gray-500">
                            Click the "▶️ Play" button after uploading your screenshot to begin the code generation process.
                          </p>
                        </div>
                      </div>
                    </body>
                    </html>
                  `);
                }}
              >
                Upload different image
              </button>
            </div>
          )}

          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            multiple
            onChange={handleFileSelect}
            className="hidden"
          />
        </div>

        {/* Upload image preview area */}
        {uploadedImage && (
          <div className="p-4 border-b border-gray-100">
            <h3 className="text-sm font-semibold text-gray-800 mb-2">📋 Target Design</h3>
            <div className="bg-gray-50 rounded-lg p-2">
              <img 
                src={uploadedImage} 
                alt="Uploaded screenshot" 
                className="w-full h-auto rounded-md shadow-sm border border-gray-200"
                style={{ maxHeight: '300px', objectFit: 'contain' }}
                onLoad={() => console.log('Image rendered successfully')}
                onError={(e) => {
                  console.error('Image render error:', e);
                  setLoadingError('Failed to display image');
                }}
              />
            </div>
          </div>
        )}

        {/* 仅在design demo时显示 Design Prompt，在Target Design和Code Generation之间 */}
        {isDesignDemo && (
          <div className="p-4 border-b border-blue-200 bg-blue-50">
            <h3 className="text-sm font-semibold text-blue-800 mb-2">📝 Design Prompt</h3>
            <textarea
              className="w-full min-h-[80px] border border-blue-300 rounded p-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 bg-white"
              placeholder="Describe your design prompt here..."
              value={designPrompt}
              onChange={e => setDesignPrompt(e.target.value)}
            />
          </div>
        )}

        {/* Generation progress and status info */}
        <div className="flex-1 p-4 flex flex-col">
          <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg p-4 border border-blue-100">
            <div className="text-center mb-4">
              <div className="text-3xl mb-2">⚡</div>
              <h3 className="text-lg font-semibold text-gray-800 mb-1">Code Generation</h3>
              <p className="text-xs text-gray-600">
                {!imageReady ? 'Please upload an image to start' : 
                 playing ? 'Generating code from your design...' : 
                 'Ready to generate code'}
              </p>
            </div>
            
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs text-gray-600">Progress:</span>
                <div className="w-full bg-gray-200 rounded-full h-2 ml-3">
                  <div 
                    className="bg-gradient-to-r from-blue-500 to-indigo-500 h-2 rounded-full transition-all duration-100" 
                    style={{ width: `${Math.round(progress)}%` }}
                  ></div>
                </div>
                <span className="text-xs font-medium text-gray-800 ml-2">
                  {Math.round(progress)}%
                </span>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-xs text-gray-600">Current Step:</span>
                <span className="text-xs font-medium text-gray-800">{step.caption || 'Loading images... Done!'}</span>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-xs text-gray-600">Status:</span>
                <span className={`text-xs font-medium flex items-center gap-1 ${
                  playing ? 'text-green-600' : imageReady ? 'text-blue-600' : 'text-gray-600'
                }`}>
                  {playing ? (
                    <>
                      <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                      Generating
                    </>
                  ) : imageReady ? (
                    <>
                      <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
                      Ready
                    </>
                  ) : (
                    <>
                      <span className="w-2 h-2 bg-gray-400 rounded-full"></span>
                      Waiting
                    </>
                  )}
                </span>
              </div>
            </div>
            
            {loadingError && (
              <div className="mt-3 text-xs text-red-600 bg-red-50 p-2 rounded border border-red-200">
                {loadingError}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Right side - Preview area */}
      <div className="w-3/5 bg-white flex flex-col">
        {/* Preview header */}
        <div className="border-b border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">Live Preview</h2>
            <div className="flex items-center space-x-4">
              <button 
                className={`px-3 py-1 rounded text-sm transition-colors ${
                  !imageReady 
                    ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    : playing 
                      ? 'bg-red-500 text-white hover:bg-red-600' 
                      : 'bg-green-500 text-white hover:bg-green-600'
                }`}
                onClick={handlePlayToggle}
                disabled={!imageReady}
                title={!imageReady ? 'Please upload an image first' : ''}
              >
                {playing ? '⏸️ Pause' : '▶️ Play'}
              </button>
              <button 
                className={`px-3 py-1 rounded text-sm transition-colors ${
                  !imageReady
                    ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
                onClick={handleReset}
                disabled={!imageReady}
              >
                🔄 Reset
              </button>
              <div className="flex items-center space-x-2">
                <div className="w-24 bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-blue-600 h-2 rounded-full transition-all duration-100" 
                    style={{ width: `${Math.round(progress)}%` }}
                  ></div>
                </div>
                <span className="text-xs text-gray-500 min-w-0">
                  {Math.round(progress)}%
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Preview content - using ScaledPreview component */}
        <div className="flex-1 p-0">
          <div className="w-full h-full bg-white overflow-hidden">
            <ScaledPreview code={code} demoId={currentDemo?.id} />
          </div>
        </div>

        {/* Bottom control bar */}
        <div className="border-t border-gray-200 p-4">
          <div className="flex items-center space-x-4">
            <input
              type="range"
              min={0}
              max={100}
              value={Math.round(progress)}
              onChange={e => {
                const newProgress = Number(e.target.value);
                setProgress(newProgress);
                // Calculate corresponding step based on progress
                const targetStepIndex = Math.floor((newProgress / 100) * steps.length);
                if (targetStepIndex < steps.length) {
                  setIdx(targetStepIndex);
                }
              }}
              className="flex-1"
              disabled={!imageReady}
            />
            <div className="text-sm text-gray-500 min-w-0">
              {step.caption || step.description || 'Loading images... Done!'}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}