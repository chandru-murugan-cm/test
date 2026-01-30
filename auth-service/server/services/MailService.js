require('dotenv').config();
const nodemailer = require('nodemailer');

module.exports = () => {
  const mailService = nodemailer.createTransport({
    service: 'gmail',
    auth: {
      user: process.env.PROJECT_EMAIL_FROM_EMAIL,
      pass: process.env.PROJECT_MAIL_APP_PASSWORD,
    },
  });

  return mailService;
};
