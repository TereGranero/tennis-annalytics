import axios from 'axios';

// Backend server API
const httpClient = axios.create({
  baseURL: 'http://127.0.0.1:5000', 
  timeout: 5000,                    
  headers: {
    'Content-Type': 'application/json',
  },
});

httpClient.interceptors.response.use(
  response => response,
  error => {
    console.error('Server Error:', error);
    return Promise.reject(error);
  }
);

// Wikidata API
const httpClientWiki = axios.create({
  baseURL: 'https://www.wikidata.org', 
  timeout: 5000,                    
  headers: {
    'Content-Type': 'application/json',
  },
});

httpClientWiki.interceptors.response.use(
  response => response,
  error => {
    console.error('Server Error:', error);
    return Promise.reject(error);
  }
);

export { httpClient, httpClientWiki }; 