const mongoose = require('mongoose');

const orgtypeSchema = new mongoose.Schema(
  {
    name: {
      type: String,
      required: true,
      trim: true,
      index: { unique: true },
    },
    desc: {
      type: String,
      trim: true,
    },
  },
  {
    timestamps: true,
  }
);

module.exports = mongoose.model('OrgType', orgtypeSchema);
