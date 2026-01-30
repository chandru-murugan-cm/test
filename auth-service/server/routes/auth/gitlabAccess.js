/* ========================= IMPORTS ========================= */
// core
const express = require('express');
const axios = require('axios');

// models
const OAuthState = require('../../models/OAuthStateModel');

// utilities
const {
  generateGitLabState,
  generateChallengeVerifierPair,
} = require('../../utilities/security/gitlabOAuth');

/**
 * Define the module exports as a function
 *
 * @param {*} params - Parameters passed from the ./index.js file, where all the routers are being registered
 */
module.exports = (params) => {
  // Define the router
  const router = express.Router();
  // TODO: Use Swagger to document the enpoint
  router.get('/gitlab-parameters', async (req, res) => {
    try {
      // Generate the GitLab state
      const gitLabState = generateGitLabState();

      // Generate the PKCE pair
      const gitLabPKCEPair = generateChallengeVerifierPair();

      // Store the state and code verifier in MongoDB with TTL
      await OAuthState.create({
        state: gitLabState,
        codeVerifier: gitLabPKCEPair.codeVerifier,
        provider: 'gitlab',
      });

      // Send a success response back to the client
      res.status(200).json({
        state: gitLabState,
        code_challenge: gitLabPKCEPair.codeChallenge,
      });
    } catch (error) {
      // Log the error for debugging
      console.error('Error in gitlab-parameters endpoint:', error.message);
      
      // Since the tokens are generated internally, without the use of any
      // third-party services, an error can only be an internal server error
      res.status(500).json({
        error: 'The service is unavailable. Please try again later',
      });
    }
  });

  // TODO: Use Swagger to document the enpoint
  router.post('/gitlab-oauth', async (req, res) => {
    /* ---------------- VALIDATE INPUT PARAMETERS ----------------*/
    const { code, state } = req.body;

    // Check that the code is present
    if (!code) {
      res.status(422).json({
        error: 'The authorization code is missing from the request body',
      });
      return;
    }

    /* ---------------- VALIDATE ENV VARIABLES ----------------*/
    // Define the list of required environment variables
    const requiredEnvironmentVariables = [
      'GITLAB_CLIENT_ID',
      'GITLAB_CLIENT_SECRET',
      'GITLAB_REDIRECT_URI',
    ];

    // Define the list of missing environment variables mentioned in the list above
    const missingEnvironmentVariables = requiredEnvironmentVariables.filter(
      (envVariable) => !process.env[envVariable]
    );

    // Check if all the env variables are present
    if (missingEnvironmentVariables.length != 0) {
      console.log(
        `Environment variables are missing: ${missingEnvironmentVariables.join(
          ', '
        )}`
      );
      res.status(424).json({
        error: 'GitLab authentication failed',
      });
      return;
    }

    /* ---------------- CREATE TOKEN URL ----------------*/
    // Retrieve all necessary parameters
    const client_id = process.env.GITLAB_CLIENT_ID;
    const client_secret = process.env.GITLAB_CLIENT_SECRET;
    const grant_type = 'authorization_code';
    const redirect_uri = process.env.GITLAB_REDIRECT_URI;

    try {
      // Retrieve the code_verifier from MongoDB
      const oauthState = await OAuthState.findOne({ state, provider: 'gitlab' });

      // Check that the OAuth state exists and is not expired
      if (!oauthState) {
        // Set the 'Bad Request' status code and the appropriate error message
        res.status(400).json({ error: 'Invalid or expired OAuth state' });
        return;
      }

      const code_verifier = oauthState.codeVerifier;

      // Clean up the used OAuth state immediately after retrieval
      await OAuthState.deleteOne({ _id: oauthState._id });
      // Request the tokens from the GitLab server
      const response = await axios.post(
        'https://gitlab.com/oauth/token',
        {
          client_id,
          client_secret,
          code,
          grant_type,
          redirect_uri,
          code_verifier,
        },
        {
          headers: {
            Accept: 'application/json',
          },
        }
      );

      // Check if the access_token has been retrieved succesfully from the endpoint
      if (response.data.access_token) {
        // Send a successful response back
        res.status(200).json(response.data);
      } else {
        // Set the 'Internal Server Error' status and send an error message
        res.status(500).json({
          error: 'Failed to fetch access token.',
          details: response.data,
        });
      }
    } catch (error) {
      // Log the error message for production
      console.error('GitLab OAuth Error:', error.message);

      // Provide different error messages based on error type
      if (error.name === 'MongoError' || error.name === 'MongooseError') {
        res.status(500).json({ 
          error: 'Database error occurred while processing OAuth request.' 
        });
      } else {
        // Set the 'Internal Server Error' status and send an error message
        res.status(500).json({ 
          error: 'An error occurred while processing the request.' 
        });
      }
    }
  });

  // Return the created router
  return router;
};
