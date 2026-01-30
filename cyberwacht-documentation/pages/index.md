---
layout: page
title: Cyberwacht
permalink: /
---

# Introduction

<!-- ## Features -->

<!-- ### User Interaction -->

In today’s ever-evolving threat landscape, safeguarding your digital assets is more critical than ever. CyberWacht stands at the forefront of cybersecurity innovation, offering a unified, intelligent, and user-friendly solution tailored to modern organizations’ needs.

<!-- # General Information -->

# What is CyberWacht?

CyberWacht is a comprehensive cybersecurity platform designed to streamline and enhance your vulnerability management processes. With its intelligent architecture and user-focused design, it provides businesses with the tools needed to proactively identify, assess, and mitigate vulnerabilities across their digital ecosystem

# Cyberwacht never stores your code

- Cyberwacht does not store your code after analysis has taken place. Some of the analysis jobs such as SAST or Secrets Detection require a git clone operation. Below we talk about the technical measures we take to ensure your code is protected:

- We perform different actions such as git clones in a fresh docker container for each repository. After analysis, the data is wiped and the docker container is terminated.

- For GitHub, no refresh or access tokens are ever stored in our database. We use the new GitHub Apps which do not require this. Even a database breach of Cyberwacht itself would not result in your GitHub code being downloadable.
