# How to contribute

We love that your are passing by to contribute to `vDistrict`. However, there
are a few little rules, we would like you to follow. If you are not familiar
with git, please have a look at:
https://github.com/RWTH-EBC/EBC-Tutorials/tree/master/EBC-Git-101

1. __Always create a new issue first__

    If you found a bug, want to edit some features or even integrate a new
    feature, the first thing you should do is to open a new issue for that in
    our issue section on GitLab. Choose an illustrative name for as a title and
    describe briefly why you open this issue and what you next steps are (e.g.
    describe the bug and how to solve it). Always choose an assignee, the
    assignee is responsible for this issue. In most cases the assignee will be
    you :-).

2. __Create a new branch__

    Never work on code without branches. If you created a new issue and start to
    work on this issue, create a new branch and name it after the issue, e.g.
    `issue71_description`, where the number is the issue number and the text is
    a very short description (e.g. parts of your title)

3. __Work in small commits__

    To avoid merge conflicts and to have a good overview about the current
    status of the branches, commit your changes once in a while. Try to avoid to
    only commit once a day (e.g. before leaving the institute).

4. __Follow PEP8 and write documentation__

    It is important that the code is readable for all current and future users,
    thus we agreed to use PEP8 for this repository (more information here:
    https://www.python.org/dev/peps/pep-0008/). Every editor will have some
    tool, that'll help you with PEP8. Also, please write documentation for all
    classes, functions and scripts. Examples how the documentation should look
    like, can be found in the code.

5. __Write unit test NOTE: ONCE WE HAVE A UNIT TEST THIS BECOMES RELEVANT__

    After you finished your implementation, write a proper unit test.

4. __Create a merge request__

    After you tested your code and reviewd it for PEP8 and documentation, you
    are ready to create a merge request on GitLab. Always reference the
    corresponding issue in your description, and give a small inside what you
    have done to solve this issue. __Always__ assign a reviewer (most likely
    Michael Mans (michael.mans) or Peter Remmen (peter.remmen)), who will have
    a look at your changes, test the code and add a review. After the reviewer
    approves your changes, you are ready to merge your features into the master.
