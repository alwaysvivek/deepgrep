/**
 * DeepGrep JavaScript SDK
 * Client library for DeepGrep API
 */

class DeepGrepClient {
  /**
   * Create a new DeepGrep client
   * @param {string} baseUrl - Base URL of the DeepGrep API
   * @param {string} apiKey - Optional API key for authentication
   */
  constructor(baseUrl = 'http://localhost:8000', apiKey = null) {
    this.baseUrl = baseUrl.replace(/\/$/, '');
    this.apiKey = apiKey;
  }

  /**
   * Get headers for requests
   * @private
   */
  _getHeaders() {
    const headers = {
      'Content-Type': 'application/json',
    };
    
    if (this.apiKey) {
      headers['Authorization'] = `Bearer ${this.apiKey}`;
    }
    
    return headers;
  }

  /**
   * Make API request
   * @private
   */
  async _request(endpoint, method = 'GET', body = null) {
    const options = {
      method,
      headers: this._getHeaders(),
    };

    if (body) {
      options.body = JSON.stringify(body);
    }

    const response = await fetch(`${this.baseUrl}${endpoint}`, options);
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || `HTTP ${response.status}: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Perform regex pattern search
   * @param {string} pattern - Regex pattern to search for
   * @param {string} text - Text to search in
   * @returns {Promise<Object>} Search results
   */
  async searchRegex(pattern, text) {
    return this._request('/api/v1/search/regex', 'POST', {
      pattern,
      text,
    });
  }

  /**
   * Perform semantic search
   * @param {string} query - Search query
   * @param {Object} options - Search options
   * @param {string} options.text - Single text to search
   * @param {string[]} options.documents - Multiple documents to search
   * @param {number} options.topK - Number of results (default: 10)
   * @returns {Promise<Object>} Semantic search results
   */
  async searchSemantic(query, options = {}) {
    const { text, documents, topK = 10 } = options;
    
    if (!text && !documents) {
      throw new Error('Either text or documents must be provided');
    }

    const payload = {
      query,
      top_k: topK,
    };

    if (text) payload.text = text;
    if (documents) payload.documents = documents;

    return this._request('/api/v1/search/semantic', 'POST', payload);
  }

  /**
   * Perform batch search
   * @param {string[]} queries - List of search queries
   * @param {string} text - Text to search in
   * @param {string} searchType - Type of search ('regex' or 'semantic')
   * @returns {Promise<Object>} Batch results
   */
  async batchSearch(queries, text, searchType = 'regex') {
    return this._request('/api/v1/search/batch', 'POST', {
      queries,
      text,
      search_type: searchType,
    });
  }

  /**
   * Upload a file
   * @param {File} file - File to upload
   * @returns {Promise<Object>} Upload result
   */
  async uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${this.baseUrl}/api/v1/upload`, {
      method: 'POST',
      headers: this.apiKey ? {
        'Authorization': `Bearer ${this.apiKey}`,
      } : {},
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Upload failed: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get search history
   * @param {number} limit - Maximum number of entries (default: 50)
   * @returns {Promise<Object>} History entries
   */
  async getHistory(limit = 50) {
    return this._request(`/api/v1/history?limit=${limit}`, 'GET');
  }

  /**
   * Check API health
   * @returns {Promise<Object>} Health status
   */
  async healthCheck() {
    return this._request('/health', 'GET');
  }
}

/**
 * Quick regex search without creating a client
 * @param {string} pattern - Regex pattern
 * @param {string} text - Text to search
 * @param {string} baseUrl - API base URL
 * @returns {Promise<Object>} Search results
 */
async function searchRegex(pattern, text, baseUrl = 'http://localhost:8000') {
  const client = new DeepGrepClient(baseUrl);
  return client.searchRegex(pattern, text);
}

/**
 * Quick semantic search without creating a client
 * @param {string} query - Search query
 * @param {string} text - Text to search
 * @param {string} baseUrl - API base URL
 * @param {number} topK - Number of results
 * @returns {Promise<Object>} Search results
 */
async function searchSemantic(query, text, baseUrl = 'http://localhost:8000', topK = 10) {
  const client = new DeepGrepClient(baseUrl);
  return client.searchSemantic(query, { text, topK });
}

// Export for different module systems
if (typeof module !== 'undefined' && module.exports) {
  // CommonJS
  module.exports = {
    DeepGrepClient,
    searchRegex,
    searchSemantic,
  };
}

if (typeof window !== 'undefined') {
  // Browser global
  window.DeepGrep = {
    Client: DeepGrepClient,
    searchRegex,
    searchSemantic,
  };
}
