const request = require('supertest');
const { Router } = require('express');
const app = Router();
const authRouter = require('../../../routes/user');

// Mount the auth routes to the /auth path
app.use('/auth', authRouter);

describe('User endpoints', () => {
  let testUser;

  beforeAll(async () => {
    // Add a user to test with
    const res = await request(app)
      .post('/auth/user')
      .send({ email: 'testuser@example.com', 
              password: 'testuser',
              fname: 'Test',
              lname: 'User' });
    testUser = res.body;
  });

  afterAll(async () => {
    // Delete the test user after all tests are done
    await request(app).delete(`/auth/user/${testUser._id}`);
  });

  describe('GET /user', () => {
    it('should return a list of users', async () => {
      const res = await request(app).get('/auth/user');
      expect(res.status).toBe(200);
      expect(res.body.userList).toBeDefined();
      expect(res.body.userList.length).toBeGreaterThan(0);
    });

    it('should return a filtered list of users when a query parameter is provided', async () => {
      const res = await request(app).get('/auth/user').query({ query: 'testuser' });
      expect(res.status).toBe(200);
      expect(res.body.userList).toBeDefined();
      expect(res.body.userList.length).toBe(1);
      expect(res.body.userList[0]._id).toBe(testUser._id);
    });
  });

  describe('GET /user/:id', () => {
    it('should return a user by ID', async () => {
      const res = await request(app).get(`/auth/user/${testUser._id}`);
      expect(res.status).toBe(200);
      expect(res.body._id).toBe(testUser._id);
    });

    it('should return a 404 error when an invalid user ID is provided', async () => {
      const res = await request(app).get('/auth/user/invalidid');
      expect(res.status).toBe(404);
    });
  });

  describe('PUT /user', () => {
    it('should update an existing user', async () => {
      const res = await request(app)
        .put('/auth/user')
        .send({
          _id: testUser._id,
          email: 'newemail@example.com',
          fname: 'New',
          lname: 'Name',
        });
      expect(res.status).toBe(200);
      expect(res.body.response).toBe('updated');
    });

    it('should return a 400 error when an invalid user ID is provided', async () => {
      const res = await request(app)
        .put('/auth/user')
        .send({
          _id: 'invalidid',
          email: 'newemail@example.com',
          fname: 'New',
          lname: 'Name',
        });
      expect(res.status).toBe(400);
      expect(res.body.response).toBeDefined();
      expect(res.body.response.text).toBe('The given User does not exist!');
    });
  });

  describe('DELETE /user/:id', () => {
    it('should delete a user by ID', async () => {
      const res = await request(app).delete(`/auth/user/${testUser._id}`);
      expect(res.status).toBe(200);
      expect(res.body.result).toBe('success');
    });

    it('should return a 404 error when an invalid user ID is provided', async () => {
      const res = await request(app).delete('/auth/user/invalidid');
      expect(res.status).toBe(404);
    });
    });
});