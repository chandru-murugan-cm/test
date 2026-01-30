const request = require('supertest');
const mongoose = require('mongoose');
const OAuthState = require('../../../models/OAuthStateModel');

// Mock the app - this follows the same pattern as other tests
const configg = require('../../../config');
const appModule = require('../../../app');

const app = appModule(configg);

describe('GitLab OAuth Access Routes', () => {
  beforeAll(async () => {
    // Ensure MongoDB connection is established
    if (mongoose.connection.readyState !== 1) {
      await mongoose.connect(process.env.MONGODBDSN || 'mongodb://localhost:27017/auth_db_test');
    }
  });

  afterAll(async () => {
    // Clean up test data
    await OAuthState.deleteMany({ provider: 'gitlab' });
    await mongoose.connection.close();
  });

  beforeEach(async () => {
    // Clear OAuth states before each test
    await OAuthState.deleteMany({ provider: 'gitlab' });
  });

  describe('GET /auth/gitlab-parameters', () => {
    it('should generate GitLab OAuth parameters successfully', async () => {
      const response = await request(app)
        .get('/auth/gitlab-parameters')
        .expect(200);

      expect(response.body).toHaveProperty('state');
      expect(response.body).toHaveProperty('code_challenge');
      expect(typeof response.body.state).toBe('string');
      expect(typeof response.body.code_challenge).toBe('string');

      // Verify the state was stored in MongoDB
      const storedState = await OAuthState.findOne({ 
        state: response.body.state,
        provider: 'gitlab' 
      });
      expect(storedState).toBeTruthy();
      expect(storedState.codeVerifier).toBeTruthy();
    });

    it('should create unique states for multiple requests', async () => {
      const response1 = await request(app)
        .get('/auth/gitlab-parameters')
        .expect(200);

      const response2 = await request(app)
        .get('/auth/gitlab-parameters')
        .expect(200);

      expect(response1.body.state).not.toBe(response2.body.state);
      expect(response1.body.code_challenge).not.toBe(response2.body.code_challenge);

      // Verify both states are stored separately
      const storedStates = await OAuthState.find({ provider: 'gitlab' });
      expect(storedStates).toHaveLength(2);
    });
  });

  describe('POST /auth/gitlab-oauth', () => {
    let validState;
    let validCodeVerifier;

    beforeEach(async () => {
      // Set up test environment variables
      process.env.GITLAB_CLIENT_ID = 'test-client-id';
      process.env.GITLAB_CLIENT_SECRET = 'test-client-secret';
      process.env.GITLAB_REDIRECT_URI = 'http://localhost:3000/callback';

      // Create a valid OAuth state for testing
      const oauthState = await OAuthState.create({
        state: 'test-state-' + Date.now(),
        codeVerifier: 'test-verifier-' + Date.now(),
        provider: 'gitlab',
      });
      validState = oauthState.state;
      validCodeVerifier = oauthState.codeVerifier;
    });

    it('should reject request without authorization code', async () => {
      const response = await request(app)
        .post('/auth/gitlab-oauth')
        .send({ state: validState })
        .expect(422);

      expect(response.body.error).toBe('The authorization code is missing from the request body');
    });

    it('should reject request with invalid state', async () => {
      const response = await request(app)
        .post('/auth/gitlab-oauth')
        .send({ 
          code: 'test-auth-code',
          state: 'invalid-state'
        })
        .expect(400);

      expect(response.body.error).toBe('Invalid or expired OAuth state');
    });

    it('should reject request with expired state', async () => {
      // Delete the OAuth state to simulate expiration
      await OAuthState.deleteOne({ state: validState });

      const response = await request(app)
        .post('/auth/gitlab-oauth')
        .send({ 
          code: 'test-auth-code',
          state: validState
        })
        .expect(400);

      expect(response.body.error).toBe('Invalid or expired OAuth state');
    });

    it('should clean up OAuth state after retrieval', async () => {
      // This test will fail at the GitLab API call, but should successfully
      // retrieve and clean up the OAuth state from MongoDB
      await request(app)
        .post('/auth/gitlab-oauth')
        .send({ 
          code: 'test-auth-code',
          state: validState
        });

      // Verify the OAuth state was cleaned up
      const storedState = await OAuthState.findOne({ state: validState });
      expect(storedState).toBeNull();
    });

    it('should handle missing environment variables', async () => {
      // Clear environment variables
      const originalClientId = process.env.GITLAB_CLIENT_ID;
      delete process.env.GITLAB_CLIENT_ID;

      const response = await request(app)
        .post('/auth/gitlab-oauth')
        .send({ 
          code: 'test-auth-code',
          state: validState
        })
        .expect(424);

      expect(response.body.error).toBe('GitLab authentication failed');

      // Restore environment variable
      if (originalClientId) {
        process.env.GITLAB_CLIENT_ID = originalClientId;
      }
    });
  });

  describe('OAuth State Model TTL', () => {
    it('should have TTL index configured', async () => {
      // Ensure indexes are created by creating a document
      await OAuthState.create({
        state: 'test-ttl-state',
        codeVerifier: 'test-ttl-verifier',
        provider: 'gitlab'
      });

      // Wait a bit for index creation
      await new Promise(resolve => setTimeout(resolve, 100));

      const indexes = await OAuthState.collection.getIndexes();
      
      // Check if any index has expireAfterSeconds set to 600
      const hasTTLIndex = Object.values(indexes).some(index => 
        index.expireAfterSeconds === 600
      );
      
      // Alternative check: look for createdAt index specifically
      const hasCreatedAtIndex = indexes.hasOwnProperty('createdAt_1');
      
      expect(hasTTLIndex || hasCreatedAtIndex).toBe(true);
    });

    it('should store OAuth state with correct schema', async () => {
      const testData = {
        state: 'test-state-schema',
        codeVerifier: 'test-verifier-schema',
        provider: 'gitlab'
      };

      const oauthState = await OAuthState.create(testData);
      
      expect(oauthState.state).toBe(testData.state);
      expect(oauthState.codeVerifier).toBe(testData.codeVerifier);
      expect(oauthState.provider).toBe(testData.provider);
      expect(oauthState.createdAt).toBeInstanceOf(Date);
    });
  });
});