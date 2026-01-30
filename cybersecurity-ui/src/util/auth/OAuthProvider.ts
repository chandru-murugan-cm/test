/**
 * The purpose of this enum is to provide the scanners with knowledge with regards to
 * which service hosts the repository
 * Currently, the options available are: GitLab or GitHub
 */
enum RepositoryProvider {
  GitLab = "gitlab",
  GitHub = "github",
  NotApplicable = "not_applicable", // This field is used for public repositories. We don't want null values in the db
}

export default RepositoryProvider;
