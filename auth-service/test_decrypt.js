const CryptoJS = require('crypto-js');

const secretKey = 'mysecretkey123';
const encryptedPassword = 'U2FsdGVkX18piO6MWkBBjRYZUb7doy1MOZkcfu68mz8=';

try {
  const decryptedPassword = CryptoJS.AES.decrypt(encryptedPassword, secretKey).toString(CryptoJS.enc.Utf8);
  console.log('Decrypted password:', decryptedPassword);
  console.log('Password length:', decryptedPassword.length);
  console.log('Is 8+ characters:', decryptedPassword.length >= 8);
} catch (error) {
  console.error('Decryption error:', error);
} 