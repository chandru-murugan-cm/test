const request = require('supertest');
const { Router } = require('express');
const app = Router();
const authRouter = require('../../../routes/auth/login');

// Mount the auth routes to the /auth path
app.use('/auth', authRouter);

const request = require('supertest');
const jwt = require('jsonwebtoken');
const passport = require('passport');

const mockConfig = { JWTSECRET: 'mock-secret' };

jest.mock('passport', () => ({
    authenticate: jest.fn((strategy, options, callback) => (req, res, next) => {
        callback(null, { id: 'mock-user-id', username: 'mock-username', org: { id: 'mock-org-id' } }, next);
    }),
}));

describe('Auth endpoints', () => {
    describe('POST /login', () => {
        it('should return a JWT token when given valid credentials', async () => {
            const credentials = { username: 'mock-username', password: 'mock-password' };
            const orgtype = await request(app)
                .post('/auth/orgtype')
                .send({ name: 'OrgType 2', desc: 'OrgType 2 description' });
            expect(response.statusCode).toBe(201);
            const orgData = {
                name: 'Acme Inc.',
                type: orgtype.body._id,
                address: '123 Main St, USA'
            };
            const orgResponse = await request(app)
                .post('/auth/org')
                .send(orgData)
                .expect(201);
            const mockToken = jwt.sign(
                { userId: 'mock-user-id', sub: 'mock-user-id', orgId: orgResponse.body._id },
                mockConfig.JWTSECRET,
                { expiresIn: '24h' },
            );

            const response = await request(authRouter)
                .post('/auth/auth/login')
                .send(credentials);

            expect(response.status).toBe(200);
            expect(response.body).toHaveProperty('jwt');
            expect(response.body.jwt).toBe(mockToken);
        });

        it('should return a 401 error when given invalid credentials', async () => {
            const credentials = { username: 'mock-username', password: 'incorrect-password' };

            const response = await request(authRouter)
                .post('/auth/auth/login')
                .send(credentials);

            expect(response.status).toBe(401);
        });
    });

    describe('GET /whoami', () => {
        it('should return the username when given a valid JWT token', async () => {
            const orgtype = await request(app)
                .post('/auth/orgtype')
                .send({ name: 'OrgType 2', desc: 'OrgType 2 description' });
            expect(response.statusCode).toBe(201);
            const orgData = {
                name: 'Ace Inc.',
                type: orgtype.body._id,
                address: '123 Main St, USA'
            };
            const orgResponse = await request(app)
                .post('/auth/org')
                .send(orgData)
                .expect(201);
            const mockToken = jwt.sign(
                { userId: 'mock-user-id', sub: 'mock-user-id', orgId: orgResponse.body._id },
                mockConfig.JWTSECRET,
                { expiresIn: '24h' },
            );

            const response = await request(authRouter)
                .get('/auth/auth/whoami')
                .set('Authorization', `Bearer ${mockToken}`);

            expect(response.status).toBe(200);
            expect(response.body).toHaveProperty('username');
            expect(response.body.username).toBe('mock-username');
        });

        it('should return a 401 error when given an invalid JWT token', async () => {
            const invalidToken = 'invalid-token';

            const response = await request(authRouter)
                .get('/auth/auth/whoami')
                .set('Authorization', `Bearer ${invalidToken}`);

            expect(response.status).toBe(401);
        });
    });
});

