// First we have to bring in mongoose
const mongoose = require('mongoose');

// Here we define the schema for our organization
const orgSchema = new mongoose.Schema(
  {
    name: {
      type: String,
      required: true,
      trim: true, // trim preceding spaces and trailing whitespaces
      index: { unique: true }, // the org name needs to be unique
    },
    type: [
      {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'OrgType',
      },
    ],
    address: {
      type: String,
      trim: true, // trim preceding spaces and trailing whitespaces
    },
  },
  {
    timestamps: true,
  }
);

// We export the model `Organization` from the `OrgSchema`
module.exports = mongoose.model('Org', orgSchema);
