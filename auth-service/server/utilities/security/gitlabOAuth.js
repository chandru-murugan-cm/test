/* ========================= IMPORTS ========================= */
const crypto = require('crypto');

/* ========================= CONFIG ========================= */
/**
 * Generates the state recommended for GitLab OAuth protocol
 * This state token also acts like protection mechanism against CSRF.
 * https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html#introduction
 */
function generateGitLabState() {
  // generate the token
  const gitLabState = crypto.randomUUID();

  // send it back to the caller
  return gitLabState;
}

/**
 //? PKCE = Proof Key for Code Exchange
 * Generates a code verifier and then the code challenge, by hashing the verifier using SHA256
 * Accoring to OAuth2 standards specified here: https://www.oauth.com/oauth2-servers/pkce/authorization-request/
 *
 * @returns - An object containing the two variables that are part of the PKCE
 */
function generateChallengeVerifierPair() {
  // Generate code verifier
  const codeVerifier = crypto.randomUUID();

  // Generate the code challenge
  const hashedCodeVerifier = crypto.createHash('sha256').update(codeVerifier);
  const codeChallenge = hashedCodeVerifier.digest('base64url');

  // Return the pair
  return { codeVerifier, codeChallenge };
}

module.exports = {
  generateGitLabState,
  generateChallengeVerifierPair,
};
