# Contributing Guidelines

Guidelines for developing and contributing to this project.

## List of project maintainers

- [gonzo](https://github.com/dgonzo)
- [zan](https://github.com/zmarkan)

## Opening new issues

- Before opening a new issue check if there are any existing FAQ entries (if one exists), issues or pull requests that match your case
- Open an issue, and make sure to label the issue accordingly - bug, improvement, feature request, etc...
- Be as specific and detailed as possible


## Setting up the development environment

- Checkout the project
- Make a branch for your improvement
- Install dependencies:
    - plugin to your editor that honors [editorconfig](https://editorconfig.org/)
    - Python contributions:
        - lint with [black](https://black.readthedocs.io/en/stable/)
        - install dependencies based on the example you are improving
            - e.g. python: pip install -r dependencies/python/requirements.txt
            - e.g. datarobot client: pip install -r dependencies/datarobot-client/requirements.txt
- Create a `.env` file following `example.env`
- Create a DataRobot key, and add the credentials to your environment variables
- Make changes and commit
- Issue a Pull Request with your changes

## Project structure
If you wish to add a code example in new language add it to the `code` directory
in a file named `<language>-example.<extension>`. If it needs a dependencies
 declaration create a subdirectory in `dependencies`.

## Making a pull request

- Have a branch with a descriptive name
- Squash / rebase your commits before opening your pull request
- Pull the latest changes from `master`
- Provide sufficient description of the pull request. Include whether it relates to an existing issue, and specify what the pull request does - (bug fix, documentation correction, dependency update, new functionality, etc...). When in doubt, overcommunicate

## Responding to issues and pull requests

This project's maintainers will make every effort to respond to any open issues as soon as possible.

If you don't get a response within 7 days of creating your issue or pull request, please send us an email at community@datarobot.com.









