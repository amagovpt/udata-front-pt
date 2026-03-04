/**
 * A Basic OEmbed loader for udata cards.
 *
 * This is only required in case standard OEmbed is not available
 * or udata is not whitelisted on a given platform.
 *
 * Instead of simply putting URL, this script requires to `div`
 * with `data-udata-*` attributes:
 *
 * Ex:
 *      <div data-udata-dataset="slug-or-id"></div>
 *      <div data-udata-reuse="slug-or-id"></div>
 *      <div data-udata-organization="slug-or-id"></div>
 */

/**
 * Extract the base URL from the URL of the current script
 */
(function() {
    function getBaseUrl() {
        const script = document.currentScript || document.querySelector('script[src$="oembed.js"]');
        const parser = document.createElement('a');
        parser.href = script.dataset.udata || script.src;
        return `${parser.protocol}//${parser.host}`;
    }

    // Base udata instance URL
    const BASE_URL = getBaseUrl();
    // OEmbed endpoint URL - adapted for udata API v1
    const OEMBED_URL = `${BASE_URL}/api/1/oembed`;
    
    // Supported attributes
    const ATTRS = ['dataset', 'reuse', 'organization'];

    /**
     * `fetch` doesn't provide an error handling based on status code.
     */
    function checkStatus(response) {
        if (response.status >= 200 && response.status < 300) {
            return response;
        } else {
            const error = new Error(response.statusText);
            error.response = response;
            throw error;
        }
    }

    /**
     * Return a promisified JSON response from an API URL
     * if status code is correct.
     */
    function fetchOEmbed(url) {
        return fetch(`${OEMBED_URL}?url=${encodeURIComponent(url)}`)
            .then(checkStatus)
            .then(response => response.json());
    }

    /**
     * Transform a string to title case
     */
    function toTitle(txt) {
        return txt.split('-').map(word => 
            word.charAt(0).toUpperCase() + word.substr(1).toLowerCase()
        ).join('');
    }

    // Load cards for supported attributes
    ATTRS.forEach(function(attr) {
        [].forEach.call(document.querySelectorAll(`[data-udata-${attr}]`), function(div) {
            // Simple loading spinner using SVG
            div.innerHTML = `
            <div style="text-align: center; padding: 20px;">
                <svg width="24" height="24" style="color: #3558a2; animation: spin 1s linear infinite;" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <style>@keyframes spin { 100% { transform: rotate(360deg); } }</style>
                    <circle style="opacity: 0.25;" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path style="opacity: 0.75;" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
            </div>`;
            
            const id = div.dataset[`udata${toTitle(attr)}`];
            
            // For dados.gov.pt / udata-front-pt, we can use the regular frontend route format to resolve objects for oembed
            // E.g. https://dados.gov.pt/pt/datasets/id/
            // The API '/api/1/oembed?url=...' handles content resolution directly if we pass it a frontend URL.
            // As a simplified fallback, we construct a generic URL to pass to the oembed endpoint.
            const urlToEmbed = `${BASE_URL}/pt/${attr}s/${id}/`;
            
            fetchOEmbed(urlToEmbed)
                .then(oembed => {
                    div.innerHTML = oembed.html;
                })
                .catch(err => {
                    console.error('Failed to load oEmbed for', attr, id, err);
                    div.innerHTML = `<div style="color: red; padding: 10px; border: 1px solid red;">Falha ao carregar o cartão de dados.</div>`;
                });
        });
    });
})();
