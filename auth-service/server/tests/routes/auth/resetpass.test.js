const request = require('supertest');
const { Router } = require('express');
const app = Router();
const UserService = require('../../../services/UserService');
const authRouter = require('../../../routes/auth/resetpassword');

// Mount the auth routes to the /auth path
app.use('/auth', authRouter);

describe('POST /resetpassword', () => {
  afterEach(() => {
    jest.resetAllMocks();
  });

  it('should return 201 status code with response "created" on successful registration', async () => {
    const mockUserService = jest.spyOn(UserService, 'changePassword').mockImplementation(() => Promise.resolve());
    const requestBody = {
      email: 'memphisdepay@example.com',
      password: 'password123',
      confirmPassword: 'password123'
    };
    const response = await request(app).post('/auth/auth/resetpassword').send(requestBody);

    expect(response.statusCode).toBe(201);
    expect(response.body).toEqual({ response: 'created' });
    expect(mockUserService).toHaveBeenCalledTimes(1);
    expect(mockUserService).toHaveBeenCalledWith(requestBody.email, requestBody.password);
  });

  it('should return 400 status code with validation errors in response body if email validation fails', async () => {
    const requestBody = {
      email: 'ronaldkoeman@example.com',
      password: 'password123',
      confirmPassword: 'password123'
    };
    const response = await request(app).post('/auth/auth/resetpassword').send(requestBody);

    expect(response.statusCode).toBe(400);
    expect(response.body.response.errors).toContainEqual({ msg: 'Invalid email address', param: 'email' });
  });

  it('should return 400 status code with validation errors in response body if password validation fails', async () => {
    const requestBody = {
      email: 'user@example.com',
      password: 'pw',
      confirmPassword: 'pw'
    };
    const response = await request(app).post('/auth/auth/resetpassword').send(requestBody);

    expect(response.statusCode).toBe(400);
    expect(response.body.response.errors).toContainEqual({ msg: 'Password must be at least 8 characters long', param: 'password' });
  });

  it('should return 400 status code with validation errors in response body if password confirmation fails', async () => {
    const requestBody = {
      email: 'leomessi@example.com',
      password: 'password123',
      confirmPassword: 'password456'
    };
    const response = await request(app).post('/auth/auth/resetpassword').send(requestBody);

    expect(response.statusCode).toBe(400);
    expect(response.body.response.errors).toContainEqual({ msg: 'Passwords do not match', param: 'confirmPassword' });
  });

  it('should return 500 status code with error message in response body if UserService throws an error', async () => {
    const mockUserService = jest.spyOn(UserService, 'changePassword').mockImplementation(() => Promise.reject(new Error('Internal Server Error')));
    const requestBody = {
      email: 'ronaldkoeman@example.com',
      password: 'password123',
      confirmPassword: 'password123'
    };
    const response = await request(app).post('/auth/auth/resetpassword').send(requestBody);

    expect(response.statusCode).toBe(500);
    expect(response.body).toEqual({ message: 'Internal Server Error' });
    expect(mockUserService).toHaveBeenCalledTimes(1);
    expect(mockUserService).toHaveBeenCalledWith(requestBody.email, requestBody.password);
  });
});
