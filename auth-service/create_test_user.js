const CryptoJS = require('crypto-js');
const axios = require('axios');

const secretKey = 'mysecretkey123';
const password = 'password123456';

// Encrypt the password
const encryptedPassword = CryptoJS.AES.encrypt(password, secretKey).toString();

const userData = {
  fname: 'Test',
  lname: 'User',
  email: 'test@example.com',
  organization: 'Test Organization',
  password: encryptedPassword,
  confirmPassword: encryptedPassword
};

async function createUser() {
  try {
    console.log('Sending user data:', JSON.stringify(userData, null, 2));
    const response = await axios.post('http://localhost:3030/auth/register', userData, {
      headers: {
        'Content-Type': 'application/json'
      }
    });
    console.log('User created successfully:', response.data);
    console.log('\nLogin credentials:');
    console.log('Email: test@example.com');
    console.log('Password: password123456');
  } catch (error) {
    console.error('Error creating user:', JSON.stringify(error.response?.data, null, 2));
  }
}

createUser(); 