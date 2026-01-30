// OAuth state model for storing temporary PKCE code verifiers
const mongoose = require('mongoose');

// Schema for storing OAuth state and code verifier pairs with TTL
const oAuthStateSchema = new mongoose.Schema(
  {
    state: {
      type: String,
      required: true,
      trim: true,
      index: { unique: true }, // State should be unique
    },
    codeVerifier: {
      type: String,
      required: true,
      trim: true,
    },
    provider: {
      type: String,
      required: true,
      enum: ['gitlab', 'github'], // Support for multiple OAuth providers
      default: 'gitlab',
    },
    createdAt: {
      type: Date,
      default: Date.now,
      expires: 600, // TTL: 10 minutes (600 seconds)
    },
  },
  {
    timestamps: false, // We're using custom createdAt with TTL
  }
);

// Ensure TTL index is created explicitly
oAuthStateSchema.index({ createdAt: 1 }, { expireAfterSeconds: 600 });

// Export the model
module.exports = mongoose.model('OAuthState', oAuthStateSchema);