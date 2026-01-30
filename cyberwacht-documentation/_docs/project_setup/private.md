---
title: Add Private Repositary
description: How to add private Repositary
---

# Adding a Private Repository to Your Project

This document outlines the steps involved in adding a repository to your existing CyberWacht project.

## Prerequisites:

- A GitHub account with the necessary permissions to access the repository

## Steps:

### Navigate to Project Settings:

1. Click on the settings icon next to your project name in the top left corner.
2. On the project overview page, you will find a button labeled **Repositories**."

### Click the **Add Repository** Button:

1. On the **Repositories** page, you will see a button labeled **Add Repository**.
2. Click this button to initiate the repository addition process.

### Provide Repository Details:

1. A modal window will appear where you need to provide the following information:

   - **Repository URL**: Enter the URL of the Git repository you want to add.
   - **Repository Label**: Add an optional label to identify the repository within the project.
   - **Is this a private repository?**: Check this box if the repository is private. This will trigger the GitHub authentication process.

   ![Create Account]({{ site.baseurl }}/assets/img/is_private.png){: .centered-image }

### Authenticate with GitHub:

1. If you checked the **Is this a private repository?** box, you will be prompted to authenticate with GitHub.
2. Click the **Authenticate with GitHub** button.
3. Enter your GitHub credentials (username and password) in the popup window.
4. Click the **Sign in** button to proceed.
   ![Create Account]({{ site.baseurl }}/assets/img/Sign_in.png){: .centered-image }

### Grant Repository Access:

1. After successful authentication, you will be redirected to a page where you can grant CyberWacht access to your repository.
2. Select the desired repository from the list and click the **Install & Authorize** button.

**step 1:** Select the repositary

![Create Account]({{ site.baseurl }}/assets/img/install.png){: .centered-image }

**step 2:** Click the Install & Authorize

![Create Account]({{ site.baseurl }}/assets/img/install_auth.png){: .centered-image }

### Confirm Authorization:

Follow these steps to verify the authorization

1. **Log in to Your GitHub Account**  
   Access your GitHub account by visiting [github.com](https://github.com) and logging in.

2. **Access Your Profile Settings**

   - Click on your profile picture in the upper-right corner of the page.
   - Select **Settings** from the dropdown menu.

3. **Navigate to Applications**

   - In the left-hand sidebar, click on **"Applications"**.

4. **View Authorized OAuth Apps**
   - Click on the **"Authorized OAuth Apps"** tab.
   - This tab will display a list of all applications that have been granted access to your GitHub account.

### Add Repository to Project:

1. Once the installation is complete, the repository will be added to your CyberWacht project.
2. You can now initiate scans and analyze the code for vulnerabilities.

## Additional Tips:

- Ensure that your GitHub account has the necessary permissions to access the repository.
- If you encounter any issues during the process, refer to the CyberWacht documentation or contact their support team.
