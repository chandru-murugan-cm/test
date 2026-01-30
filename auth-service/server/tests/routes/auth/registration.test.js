const request = require('supertest');
const { Router } = require('express');
const app = Router();
const authRouter = require('../../../routes/auth/registration');

// Mount the auth routes to the /auth path
app.use('/auth', authRouter);

describe('Registration endpoint', () => {
  it('should return 201 and created user details on successful registration', async () => {
    const response = await request(app)
      .post('/auth/auth/register')
      .send({
        email: 'virgilvandijk@example.com',
        password: 'password123',
        confirmPassword: 'password123',
        fname: 'Virgil van',
        lname: 'Dijk',
      });

    expect(response.status).toBe(201);
    expect(response.body.response.id).toBeDefined();
    expect(response.body.response.text).toBe('created');
  });

  it('should return 400 with error message when email already exists', async () => {
    const response = await request(app)
      .post('/auth/auth/register')
      .send({
        email: 'virgilvandijk@example.com',
        password: 'password',
        confirmPassword: 'password',
        fname: 'Frenkie',
        lname: 'De Jong',
      });

    expect(response.status).toBe(400);
    expect(response.body.response.text).toBe('The given email address exist already!');
  });

  it('should return 400 with validation errors when inputs are invalid', async () => {
    const response = await request(app)
      .post('/auth/auth/register')
      .send({
        email: 'invalidemail',
        password: 'password123',
        confirmPassword: 'password456',
        fname: '',
        lname: '',
      });

    expect(response.status).toBe(400);
    expect(response.body.response.errors.length).toBeGreaterThan(0);
  });
});
