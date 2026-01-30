# Cyberwacht Documentation

This repository contains the documentation for the Cyberwacht project, built using Jekyll.

## Prerequisites

- Ruby (version 3.2 or later)
- Bundler
- Homebrew (for macOS users)

## Installation Steps

1. **Install Ruby and Bundler:**

   If you don't have Ruby installed, you can install it using Homebrew:

   ```bash
   brew install ruby@3.2
   ```

   Add Ruby to your PATH by adding the following line to your `~/.zshrc` file:

   ```bash
   echo 'export PATH="/usr/local/opt/ruby@3.2/bin:$PATH"' >> ~/.zshrc
   source ~/.zshrc
   ```

   Install Bundler:

   ```bash
   gem install bundler
   ```

2. **Clone the Repository:**

   Clone the repository to your local machine:

   ```bash
   git clone <repository-url>
   cd cyberwacht-documentation
   ```

3. **Install Dependencies:**

   Install the project's dependencies using Bundler:

   ```bash
   bundle install
   ```

4. **Run the Documentation Site Locally:**

   Start the Jekyll server to view the documentation site locally:

   ```bash
   bundle exec jekyll serve
   ```

   The site will be available at `http://localhost:4000`.

## Additional Information

- For more detailed output during the build process, you can run the server with the `--verbose` flag:

  ```bash
  bundle exec jekyll serve --verbose
  ```

- If you encounter any issues, ensure that all dependencies are correctly installed and that you are in the correct directory (`cyberwacht-documentation`).

## Contributing

Please read the contributing guidelines before submitting a pull request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
