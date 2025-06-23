/**
 * R5 Lovelace Custom Components Collection
 * Dynamic loader for multiple Lovelace custom components
 * 
 * Features:
 * - Auto-discovery of JS files in dist directory
 * - Optional manifest.json support for controlled loading
 * - Fallback mechanisms for reliability
 * 
 * Author: plosada
 * Repository: https://github.com/plosada/r5-lovelace-custom-components
 */

console.info(
  '%c R5-LOVELACE-CUSTOM-COMPONENTS %c Dynamic Collection Loader ',
  'color: orange; font-weight: bold; background: black',
  'color: white; font-weight: bold; background: dimgray'
);

// Function to load a JavaScript file dynamically
function loadScript(src, name) {
  return new Promise((resolve, reject) => {
    const script = document.createElement('script');
    script.src = src;
    script.type = 'module';
    
    script.onload = () => {
      console.info(`✓ ${name} loaded successfully`);
      resolve();
    };
    
    script.onerror = (error) => {
      console.error(`✗ Failed to load ${name}:`, error);
      reject(error);
    };
    
    document.head.appendChild(script);
  });
}

// Get the base URL for the components
function getBaseUrl() {
  // Try to get the URL from the current script
  const scripts = document.querySelectorAll('script[src*="r5-lovelace-custom-components"]');
  if (scripts.length > 0) {
    const scriptSrc = scripts[scripts.length - 1].src;
    return scriptSrc.substring(0, scriptSrc.lastIndexOf('/'));
  }
  
  // Fallback to HACS standard path
  return '/hacsfiles/r5-lovelace-custom-components';
}

// Function to load manifest file
async function loadManifest() {
  const baseUrl = getBaseUrl();
  try {
    const response = await fetch(`${baseUrl}/manifest.json`);
    if (response.ok) {
      const manifest = await response.json();
      console.info('📋 Loaded manifest with', manifest.components?.length || 0, 'components');
      return manifest;
    }
  } catch (error) {
    console.debug('No manifest found or error loading it, using auto-discovery');
  }
  return null;
}

// Function to discover JS files in the dist directory
async function discoverJSFiles() {
  const baseUrl = getBaseUrl();
  const jsFiles = [];
  
  try {
    // First try to load from manifest
    const manifest = await loadManifest();
    if (manifest && manifest.components) {
      return manifest.components
        .filter(comp => comp.file && comp.file.endsWith('.js'))
        .map(comp => ({
          file: comp.file,
          name: comp.name || comp.file.replace('.js', ''),
          description: comp.description || '',
          required: comp.required !== false
        }));
    }
    
    // Fallback: Known files list (update this as you add more components)
    const knownFiles = [
      'card-mod.js',
      'fold-entity-row.js'
      // Add more files here as needed
    ];
    
    // Test which files actually exist
    for (const file of knownFiles) {
      try {
        const response = await fetch(`${baseUrl}/${file}`, { method: 'HEAD' });
        if (response.ok) {
          jsFiles.push({
            file: file,
            name: file.replace('.js', '').replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
            description: `Component: ${file}`,
            required: true
          });
        }
      } catch (error) {
        console.debug(`File ${file} not found or not accessible`);
      }
    }
    
    // Additional auto-discovery for common Lovelace components
    const commonPatterns = [
      'button-card.js',
      'mini-graph-card.js', 
      'mini-media-player.js',
      'mushroom.js',
      'atomic-calendar-revive.js',
      'weather-card.js',
      'vertical-stack-in-card.js',
      'layout-card.js',
      'auto-entities.js',
      'template-entity-row.js',
      'slider-entity-row.js',
      'multiple-entity-row.js'
    ];
    
    for (const pattern of commonPatterns) {
      if (!jsFiles.find(item => item.file === pattern)) {
        try {
          const response = await fetch(`${baseUrl}/${pattern}`, { method: 'HEAD' });
          if (response.ok) {
            jsFiles.push({
              file: pattern,
              name: pattern.replace('.js', '').replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
              description: `Auto-discovered: ${pattern}`,
              required: false
            });
          }
        } catch (error) {
          // File doesn't exist, continue
        }
      }
    }
    
  } catch (error) {
    console.warn('Could not auto-discover JS files, using minimal fallback');
    // Minimal fallback
    jsFiles.push(
      {
        file: 'card-mod.js',
        name: 'Card Mod',
        description: 'Advanced CSS styling for Lovelace cards',
        required: true
      },
      {
        file: 'fold-entity-row.js',
        name: 'Fold Entity Row', 
        description: 'Collapsible rows for entities in Lovelace',
        required: true
      }
    );
  }
  
  return jsFiles;
}

// Main loader function
async function loadR5Components() {
  const baseUrl = getBaseUrl();
  
  console.info('🚀 Loading R5 Lovelace Custom Components...');
  console.info('📂 Discovering JS files in dist directory...');
  
  try {
    // Discover available JS files
    const components = await discoverJSFiles();
    
    console.info(`🔍 Found ${components.length} components:`, components.map(c => c.file));
    
    if (components.length === 0) {
      console.warn('⚠️ No JS files found to load');
      return;
    }
    
    // Load all discovered components
    const loadPromises = components.map(component => 
      loadScript(`${baseUrl}/${component.file}`, component.name)
    );
    
    const results = await Promise.allSettled(loadPromises);
    
    const successful = results.filter(r => r.status === 'fulfilled').length;
    const failed = results.filter(r => r.status === 'rejected').length;
    
    if (successful > 0) {
      console.info(
        `%c R5 Components Collection %c ${successful}/${components.length} components loaded successfully! `,
        'color: white; font-weight: bold; background: green',
        'color: white; font-weight: bold; background: darkgreen'
      );
    }
    
    if (failed > 0) {
      console.warn(`⚠️ ${failed} components failed to load`);
    }
    
    // Update global reference
    window.R5LoaderComponents.components = components.map(c => c.file);
    
    // Dispatch custom event to notify that loading is complete
    window.dispatchEvent(new CustomEvent('r5-components-loaded', {
      detail: {
        components: components,
        successful: successful,
        failed: failed,
        total: components.length,
        timestamp: new Date().toISOString()
      }
    }));
    
  } catch (error) {
    console.error('❌ Error loading R5 components:', error);
    
    // Dispatch error event
    window.dispatchEvent(new CustomEvent('r5-components-error', {
      detail: { error: error.message }
    }));
  }
}

// Auto-load components when script is loaded
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', loadR5Components);
} else {
  loadR5Components();
}

// Export for manual loading if needed
window.R5LoaderComponents = {
  load: loadR5Components,
  discover: discoverJSFiles,
  loadManifest: loadManifest,
  version: '1.0.0',
  components: [] // Will be populated dynamically
};

// Add some metadata for HACS
const R5_COMPONENT_INFO = {
  name: 'R5 Lovelace Custom Components',
  version: '1.0.0',
  description: 'Dynamic collection of useful Lovelace custom components',
  author: 'plosada',
  repository: 'https://github.com/plosada/r5-lovelace-custom-components',
  type: 'dynamic-loader',
  autoDiscovery: true,
  manifestSupport: true
};

console.info('📋 R5 Component Info:', R5_COMPONENT_INFO);