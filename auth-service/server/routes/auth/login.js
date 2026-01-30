const { Router } = require('express');
const jwt = require('jsonwebtoken');
const passport = require('passport');
const CryptoJS = require('crypto-js');

const router = Router();
const GroupService = require('../../services/GroupService');
const UserService = require('../../services/UserService');

module.exports = (params) => {
  const { config } = params;

  router.post('/login', async (req, res, next) => {
    try {
      const { email, password: encryptedPassword, targetUI } = req.body;
      // Validate email address format
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(email)) {
        return res.status(400).json({ message: 'Invalid email address' });
      }

      const secretKey = process.env.CRYPTO_SECRET_KEY;

      const password = CryptoJS.AES.decrypt(
        encryptedPassword,
        secretKey
      ).toString(CryptoJS.enc.Utf8);

      req.body.password = password;

      // Fetch user details by email and log them
      const usr = await UserService.findByEmail(email);

      passport.authenticate(
        'local',
        { session: false },
        async (err, user, info) => {
          if (user && 'isactive' in user && user.isactive !== true) {
            return res.status(400).json({
              response: 'Your account is inactive. Please contact the administrator to activate your account.',
              user,
            });
          }
          if (err) {
            console.error('Error during authentication:', err);
            return res
              .status(500)
              .json({ message: 'Authentication error', info });
          }
          if (!user) {
            console.error('User authentication failed:', info);
            return res.status(400).json({ message: 'Login failed', info });
          }
            
            // UI Service authentication check based on `targetUI`
            if (targetUI === 'admin' && (!usr.isadmin || usr.isadmin !== true)) {

              console.log("inside ui authentication check",usr.isadmin )
              // If it's the Admin UI, only allow users with `isadmin: true`
              return res.status(403).json({
                message: 'Unauthorized: Only admins can access this service',
              });
            }

          req.login(user, { session: false }, async (loginErr) => {
            if (loginErr) return next(loginErr);

            const groupIds = req?.user?.group || [];

            // Get group names based on group IDs using the findById method
            const groupNames = await Promise.all(
              groupIds.map(async (groupId) => {
                const groupRes = await GroupService.findById(groupId);
                return groupRes?.name || null;
              })
            );

            const isAdmin = usr && (usr.isadmin === true || usr.isadmin === 'true');

            const token = jwt.sign(
              {
                sub: user.id,
                userId: user.id,
                orgId: user?.org?.id,
                groupName: groupNames.filter(Boolean).join(', '),
                email: user.email,
                name: `${user.fname} ${user.lname}`,
                role: isAdmin ? 'admin' : 'user',
              },
              config.JWTSECRET,
              { expiresIn: '30d' }
            );

            return res.json({ jwt: token });
          });
        }
      )(req, res, next);
    } catch (err) {
      return next(err);
    }
  });

  return router;
};
