const { body, validationResult } = require('express-validator');
const CryptoJS = require('crypto-js');

const decryptPassword = (encryptedPassword) => {
  const secretKey = process.env.CRYPTO_SECRET_KEY;

  return CryptoJS.AES.decrypt(encryptedPassword, secretKey).toString(
    CryptoJS.enc.Utf8
  );
};

module.exports.validatePassword = body('password').custom((value, { req }) => {
  // Decrypt the password first
  const decryptedPassword = decryptPassword(value);
  
  // Check if the decrypted password is at least 8 characters long
  if (decryptedPassword.length < 8) {
    throw new Error('The password must be at least 8 characters long.');
  }

  return true;
});

module.exports.validatePasswordMatch = body('password').custom(
  (value, { req }) => {
    // Decrypt both the password and confirmPassword
    const decryptedPassword = decryptPassword(value);
    const decryptedConfirmPassword = decryptPassword(req.body.confirmPassword);

    // Check if the passwords match
    if (decryptedPassword !== decryptedConfirmPassword) {
      throw new Error("Passwords don't match.");
    }

    return true;
  }
);

module.exports.validateEmail = body('email')
  .custom((value) => {
    // Custom email validation pattern allowing '.' character
    const pattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    if (!pattern.test(value)) {
      throw new Error('Please enter a valid email address.');
    }
    return true;
  })
  .normalizeEmail();

module.exports.validationResult = validationResult;
