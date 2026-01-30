const customBaseQuery = async (args, api, extraOptions) => {
  const baseUrls = {
    auth: import.meta.env.VITE_API_AUTH_BASE_URL,
    "cyber-service": import.meta.env.VITE_API_CYBER_SERVICE_BASE_URL,
    "cyber-scan": import.meta.env.VITE_API_CYBER_SCAN_BASE_URL,
  };

  if (!baseUrls.auth || !baseUrls["cyber-service"]) {
    throw new Error("Base URL for 'auth' or 'cyber-service' is not defined");
  }

   let url;
  if (args.url.startsWith("/crscan") || args.url.startsWith("/cs/")) {
    url = `${baseUrls["cyber-service"]}${args.url}`;
  } else {
    url = `${baseUrls["auth"]}${args.url}`;
  }

  const token = api.getState()?.auth?.token || null; 

  const headers = new Headers(args.headers || {});

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  headers.set("Content-Type", "application/json");

  const body = args.body ? JSON.stringify(args.body) : undefined;

  try {
    const response = await fetch(url, {
      ...args,
      body,
      headers,
    });

    const data = await response.json();
    if (response.ok) {
      return { data };
    } else {
      return { error: data };
    }
  } catch (error) {
    return { error: { message: error.message } };
  }
};

export default customBaseQuery;
