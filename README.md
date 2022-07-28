# USACO-ProblemChecklist-FastAPI
## What is this?
This web app is a simple checklist for USACOders to keep track of which problems they have completed. Heavily inspired by sites like IOChecklist and USACO Rating, this app also allows you to **sync with your USACO account** and **share your checklist with others**.

## FAQ
- What information is stored?
  - Your password is not and never will be stored in plain text.
  - Your USACO information is directly sent to USACO for authentication. It is never saved or stored.
- Why doesn't this site use HTTPS?
  - Let's Encrypt does not offer SSL certificates for direct IPs. The API for this web app is hosted in china - to register a domain with it requires an ICP license, which I cannot obtain.
  - Still worried? The official USACO.org website doesn't use HTTPS either.
- I'm still worried about security.
  - No worries. Your account is not linked to any personal information. Use a password that you don't use anywhere else, and you'll be fine.
  - It is your choice to submit information to sync with your USACO account. Don't want to? Don't need to.
- Want to make a suggestion or found an error?
  - Open a GitHub issue. I'm always trying to learn :)
