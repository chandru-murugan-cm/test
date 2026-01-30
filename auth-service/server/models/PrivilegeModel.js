const mongoose = require('mongoose');

const privilegeSchema = new mongoose.Schema(
  {
    name: {
      type: String,
      required: true,
      trim: true,
      index: { unique: true },
    },
  },
  {
    timestamps: true,
  }
);

module.exports = mongoose.model('Privilege', privilegeSchema);
