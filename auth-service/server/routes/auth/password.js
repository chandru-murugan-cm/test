const { Router } = require('express');
const jwt = require('jsonwebtoken');
const UserService = require('../../services/UserService');
const mailService = require('../../services/MailService');
require('dotenv').config();

const router = Router();
const mail = mailService();

module.exports = (params) => {
  const { config } = params;
  router.post('/forgot-password', async (req, res, next) => {
    const { email } = req.body;
    try {
      const user = await UserService.findByEmail(email);
      if (!user?.id) {
        return next(new Error('User not found'));
      }

      const resetPasswordToken = jwt.sign(
        {
          type: 'reset-password',
          email,
          userId: user.id,
        },
        config.JWTSECRET,
        { expiresIn: '30m' }
      );

      const resetLink = process.env.PRODUCTION_BASE_URL
          ? `${process.env.PRODUCTION_BASE_URL}/reset-password/${resetPasswordToken}`
          : `http://localhost:5173/reset-password/${resetPasswordToken}`;

      // if (process.env.PROJECT_EMAIL_DOMAIN) {
        mail.sendMail(
          {
            to: email,
            subject: `Reset Password for ${process.env.PROJECT_NAME}`,
            html: passwordResetHtml({
              projectName: process.env.PROJECT_NAME,
              name: user.fname,
              resetLink,
            }),
          },
          (err) => {
            if (err) {
              console.error(err);
            }
          }
        );
        console.log("email sent successfully")
      // }

      return res
        .status(200)
        .json(
          req.app.get('env') === 'development'
            ? { resetLink }
            : 'reset password successful'
        );
    } catch (err) {
      return next(err);
    }
  });

  router.post('/reset-password', async (req, res, next) => {
    const { password, token } = req.body;
    try {
      const decodedToken = jwt.verify(token, config.JWTSECRET);

      const resetTokenIssuance = new Date(decodedToken.iat * 1000);
      const { email, userId, type } = decodedToken;

      if (type !== 'reset-password') {
        return next(new Error('This is not a reset password token'));
      }

      const user = await UserService.findById(userId);
      if (!user) {
        return next(new Error('User not found'));
      }

      const userUpdatedAt = new Date(user.updatedAt);
      if (userUpdatedAt.getTime() > resetTokenIssuance.getTime()) {
        return next(new Error('Invalid reset password token'));
      }

      await UserService.changePassword(email, password);

      return res.status(200).json('Password successfully reset');
    } catch (err) {
      return next(err);
    }
  });

  return router;
};

function passwordResetHtml({ projectName, name, resetLink }) {
  return `
<!DOCTYPE html>
<html>
<head>
  <title>${projectName} Password Reset</title>
</head>
<body>
  <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
    <h2>${projectName} Password Reset</h2>
    <p>Hello ${name},</p>
    <p>You are receiving this email because a password reset request was made for your ${projectName} account.</p>
    <p>If you did not initiate this request, please ignore this email.</p>
    <p>Otherwise, click the button below to reset your password:</p>
    <div style="text-align: center; margin-top: 20px;">
      <a href="${resetLink}" style="display: inline-block; background-color: #007bff; color: #ffffff; text-decoration: none; padding: 10px 20px; border-radius: 5px;">Reset Password</a>
    </div>
    <p>If the button above doesn't work, you can also copy and paste the following link into your browser:</p>
    <p>${resetLink}</p>
    <p>Please note that this link is valid for a limited time.</p>
    <p>If you have any questions or need further assistance, please contact our support team at support@${projectName.toLowerCase()}.com.</p>
    <p>Thank you,</p>
    <p>The ${projectName} Team</p>
  </div>
</body>
</html>
`;
}
