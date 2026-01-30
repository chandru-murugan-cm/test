const express = require('express');
const axios = require('axios');

module.exports = (params) => {
  const router = express.Router();

  // Existing auth routes...

  router.post('/github-oauth', async (req, res) => {
    const { code } = req.body;
    const client_id = process.env.CLIENT_ID;
    const client_secret = process.env.CLIENT_SECRET;
    const redirectUri = process.env.GITHUB_REDIRECT_URI;  
    if (!code) {
      return res.status(400).json({ error: 'Authorization code is required.' });
    }

    try {
      const response = await axios.post(
        'https://github.com/login/oauth/access_token',
        {
          client_id,
          client_secret,
          code,
          redirect_uri: redirectUri 
        },
        {
          headers: {
            Accept: 'application/json',
          },
        }
      );

      if (response.data.access_token) {
        res.json({ access_token: response.data.access_token });
      } else {
        res.status(500).json({
          error: 'Failed to fetch access token.',
          details: response.data,
        });
      }
    } catch (error) {
      console.error('GitHub OAuth Error:', error.message);
      res
        .status(500)
        .json({ error: 'An error occurred while processing the request.' });
    }
  });

  return router;
};
