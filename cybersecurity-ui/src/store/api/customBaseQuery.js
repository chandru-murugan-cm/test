// src/services/customBaseQuery.js

const customBaseQuery = async (args, api, extraOptions) => {
  const baseUrls = {
    auth: import.meta.env.VITE_API_AUTH_BASE_URL,
    "cyber-service": import.meta.env.VITE_API_CYBER_SERVICE_BASE_URL,
    "cyber-scan": import.meta.env.VITE_API_CYBER_SCAN_BASE_URL,
  };

  // Determine which base URL to use based on the endpoint path
  let url;
  if (args.url.startsWith("/crscan") || args.url.startsWith("/cs/")) {
    url = `${baseUrls["cyber-service"]}${args.url}`;
  } else {
    url = `${baseUrls["auth"]}${args.url}`;
  }

  // Prepare headers with auth token if available
  const headers = new Headers(args.headers || {});
  const token = api.getState().auth.token;
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }
  headers.set("Content-Type", "application/json");
  const body = args.body ? JSON.stringify(args.body) : undefined;

  // Use fetch to make the request with the fully constructed URL
  return fetch(url, {
    ...args,
    body,
    headers,
  }).then((response) =>
    response.json().then((data) => ({
      data: response.ok ? data : null,
      error: response.ok ? null : data,
    }))
  );
};

export default customBaseQuery;
